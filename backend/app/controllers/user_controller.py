import numpy as np
from typing import List, Dict, Optional
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException
from backend.app.config.database import get_db
from backend.app.schemas.clothing_schemas import (
    User, Swipe, SwipeRequest, SwipeResponse, 
    UserPreferences, FeedItem
)
from backend.app.controllers.clothing_controller import find_similar_clothing
from backend.app.models.clip_model import CLIPModel
import torch

clip_model = CLIPModel()

async def create_user(username: str, email: str) -> str:
    """Create a new user"""
    db = await get_db().__anext__()
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    user = User(
        username=username,
        email=email,
        preferences={},
        created_at=datetime.utcnow(),
        last_active=datetime.utcnow()
    )
    
    result = await db.users.insert_one(user.dict(by_alias=True, exclude={"id"}))
    return str(result.inserted_id)

async def record_swipe(user_id: str, swipe_request: SwipeRequest) -> SwipeResponse:
    """Record a user's swipe and update preferences"""
    db = await get_db().__anext__()
    
    try:
        # Record the swipe
        swipe = Swipe(
            user_id=user_id,
            clothing_item_id=swipe_request.clothing_item_id,
            action=swipe_request.action,
            timestamp=datetime.utcnow()
        )
        
        # Convert string IDs to ObjectId for database insertion
        swipe_doc = swipe.dict(by_alias=True, exclude={"id"})
        swipe_doc["user_id"] = ObjectId(swipe_doc["user_id"])
        swipe_doc["clothing_item_id"] = ObjectId(swipe_doc["clothing_item_id"])
        
        await db.swipes.insert_one(swipe_doc)
        
        # Update user preferences based on the swipe
        await update_user_preferences(user_id, swipe_request.clothing_item_id, swipe_request.action)
        
        # Get next item for the feed
        next_item = await get_next_feed_item(user_id)
        
        return SwipeResponse(
            success=True,
            message=f"Swiped {swipe_request.action}",
            next_item=next_item
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording swipe: {str(e)}")

async def update_user_preferences(user_id: str, clothing_item_id: str, action: str):
    """Update user preferences based on their swipe"""
    db = await get_db().__anext__()
    
    # Get the clothing item's tags
    clothing_item = await db.clothing_items.find_one({"_id": ObjectId(clothing_item_id)})
    if not clothing_item:
        return
    
    tags = clothing_item.get('tags', [])
    
    # Get current user preferences
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return
    
    preferences = user.get('preferences', {})
    
    # Update preferences based on action
    weight = 0.1  # Learning rate
    if action == "like":
        weight = 0.1
    elif action == "dislike":
        weight = -0.1
    
    # Update preference scores for each tag
    for tag in tags:
        if tag in preferences:
            preferences[tag] += weight
        else:
            preferences[tag] = weight
        
        # Keep preferences in reasonable range
        preferences[tag] = max(-1.0, min(1.0, preferences[tag]))
    
    # Update user in database
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "preferences": preferences,
                "last_active": datetime.utcnow()
            }
        }
    )

async def get_user_preferences(user_id: str) -> UserPreferences:
    """Get user's current preferences and swipe statistics"""
    db = await get_db().__anext__()
    
    # Get user data
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get swipe statistics
    total_swipes = await db.swipes.count_documents({"user_id": ObjectId(user_id)})
    likes = await db.swipes.count_documents({"user_id": ObjectId(user_id), "action": "like"})
    dislikes = total_swipes - likes
    
    return UserPreferences(
        user_id=user_id,
        preferences=user.get('preferences', {}),
        total_swipes=total_swipes,
        likes=likes,
        dislikes=dislikes
    )

async def get_next_feed_item(user_id: str, limit: int = 1) -> Optional[Dict]:
    """Get the next item for the user's feed based on their preferences"""
    db = await get_db().__anext__()
    
    # Get user preferences
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return None
    
    preferences = user.get('preferences', {})
    
    # Get items the user hasn't swiped on yet
    swiped_item_ids = await db.swipes.distinct(
        "clothing_item_id", 
        {"user_id": ObjectId(user_id)}
    )
    
    # Query for items not yet swiped
    query = {"_id": {"$nin": swiped_item_ids}}
    cursor = db.clothing_items.find(query).limit(50)  # Get a batch to score
    
    items = []
    async for item in cursor:
        items.append(item)
    
    if not items:
        return None
    
    # Score items based on user preferences
    scored_items = []
    for item in items:
        score = calculate_preference_score(item, preferences)
        scored_items.append((item, score))
    
    # Sort by score (highest first) and return the best item
    scored_items.sort(key=lambda x: x[1], reverse=True)
    
    if scored_items:
        best_item, score = scored_items[0]
        return {
            "id": str(best_item["_id"]),
            "filename": best_item["filename"],
            "tags": best_item["tags"],
            "similarity_score": score,
            "reason": get_recommendation_reason(best_item, preferences)
        }
    
    return None

def calculate_preference_score(item: Dict, preferences: Dict[str, float]) -> float:
    """Calculate how well an item matches user preferences"""
    if not preferences:
        return 0.0
    
    item_tags = item.get('tags', [])
    if not item_tags:
        return 0.0
    
    total_score = 0.0
    matched_tags = 0
    
    for tag in item_tags:
        if tag in preferences:
            total_score += preferences[tag]
            matched_tags += 1
    
    # Normalize by number of matched tags
    if matched_tags > 0:
        return total_score / matched_tags
    
    return 0.0

def get_recommendation_reason(item: Dict, preferences: Dict[str, float]) -> str:
    """Generate a reason why this item was recommended"""
    item_tags = item.get('tags', [])
    if not item_tags or not preferences:
        return "New item in our collection"
    
    # Find the highest scoring tags
    tag_scores = [(tag, preferences.get(tag, 0)) for tag in item_tags if tag in preferences]
    if not tag_scores:
        return "New item in our collection"
    
    tag_scores.sort(key=lambda x: x[1], reverse=True)
    top_tag, score = tag_scores[0]
    
    if score > 0.5:
        return f"Based on your love for {top_tag}"
    elif score > 0.1:
        return f"Similar to your preferences in {top_tag}"
    else:
        return "New item in our collection"

async def get_user_feed(user_id: str, limit: int = 10) -> List[FeedItem]:
    """Get a feed of recommended items for the user"""
    db = await get_db().__anext__()
    
    # Get user preferences
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return []
    
    preferences = user.get('preferences', {})
    
    # Get items the user hasn't swiped on yet
    swiped_item_ids = await db.swipes.distinct(
        "clothing_item_id", 
        {"user_id": ObjectId(user_id)}
    )
    
    # Query for items not yet swiped
    query = {"_id": {"$nin": swiped_item_ids}}
    cursor = db.clothing_items.find(query).limit(100)  # Get more items to score
    
    items = []
    async for item in cursor:
        items.append(item)
    
    if not items:
        return []
    
    # Score and sort items
    scored_items = []
    for item in items:
        score = calculate_preference_score(item, preferences)
        scored_items.append((item, score))
    
    scored_items.sort(key=lambda x: x[1], reverse=True)
    
    # Convert to FeedItem objects
    feed_items = []
    for item, score in scored_items[:limit]:
        feed_items.append(FeedItem(
            id=str(item["_id"]),
            filename=item["filename"],
            tags=item["tags"],
            similarity_score=score,
            reason=get_recommendation_reason(item, preferences)
        ))
    
    return feed_items
