import logging
from typing import List
from fastapi import UploadFile, File
from ..controllers.clothing_detector import detect_and_crop_garments
from ..controllers.tag_extractor import extract_tags_from_image  # Assume this exists
from fastapi import APIRouter, HTTPException
from ..schemas.clothing_schemas import (
    UploadClothingItemRequest,
    UploadClothingItemResponse,
    TagRequest,
    TagResponse,
    SwipeRequest,
    SwipeResponse,
    UserPreferences,
    FeedItem,
    CreateUserRequest
)
from ..controllers.clothing_controller import (
    handle_upload_clothing_item,
    handle_tag_request,
    get_similar_items,
    cleanup_orphan_images,
)
from ..controllers.user_controller import (
    create_user,
    record_swipe,
    get_user_preferences,
    get_user_feed,
    get_next_feed_item
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/clothing", tags=["Clothing"])

@router.post("/upload", response_model=UploadClothingItemResponse)
async def upload_clothing_item(payload: UploadClothingItemRequest):
    """
    Upload a clothing item image and return the predicted garment type and feature tags.
    """
    try:
        return await handle_upload_clothing_item(payload)
    except Exception as e:
        logger.exception("Error during clothing upload")
        raise HTTPException(status_code=500, detail="Failed to process clothing upload.")

@router.post("/tag", response_model=TagResponse)
async def tag_clothing_image(payload: TagRequest):
    """
    Tag a clothing image with garment type and relevant features without storing the item.
    """
    try:
        return await handle_tag_request(payload)
    except Exception as e:
        logger.exception("Error during clothing image tagging")
        raise HTTPException(status_code=500, detail="Failed to extract tags from image.")

@router.post("/multi-tag")
async def multi_garment_tagging(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        cropped_images = detect_and_crop_garments(image_bytes)

        tags_list = []
        for garment_img in cropped_images:
            tags = extract_tags_from_image(garment_img)
            tags_list.append(tags)
        return {"garments": tags_list}
    except Exception as e:
        logger.error(f"Multi-tagging error: {e}")
        raise HTTPException(status_code=500, detail="Failed to tag garments.")

@router.get("/similar/{item_id}")
async def get_similar_clothing(item_id: str, limit: int = 5):
    """
    Get similar clothing items based on visual similarity
    """
    try:
        return await get_similar_items(item_id, limit)
    except Exception as e:
        logger.exception("Error getting similar items")
        raise HTTPException(status_code=500, detail="Failed to find similar items.")

@router.post("/maintenance/cleanup_orphans")
async def maintenance_cleanup_orphans():
    try:
        return await cleanup_orphan_images()
    except Exception as e:
        logger.exception("Error cleaning orphan images")
        raise HTTPException(status_code=500, detail="Failed to cleanup orphan images.")

# --------------------------
# Tinder-like App Routes
# --------------------------

@router.post("/users", response_model=dict)
async def create_new_user(user_data: CreateUserRequest):
    """Create a new user account"""
    try:
        user_id = await create_user(user_data.username, user_data.email)
        return {"user_id": user_id, "message": "User created successfully"}
    except Exception as e:
        logger.exception("Error creating user")
        raise HTTPException(status_code=500, detail="Failed to create user.")

@router.post("/swipe", response_model=SwipeResponse)
async def swipe_item(swipe_request: SwipeRequest):
    """Record a user's swipe (like/dislike) on a clothing item"""
    try:
        return await record_swipe(swipe_request.user_id, swipe_request)
    except Exception as e:
        logger.exception("Error recording swipe")
        raise HTTPException(status_code=500, detail="Failed to record swipe.")

@router.get("/users/{user_id}/preferences", response_model=UserPreferences)
async def get_user_preferences_endpoint(user_id: str):
    """Get user's preferences and swipe statistics"""
    try:
        return await get_user_preferences(user_id)
    except Exception as e:
        logger.exception("Error getting user preferences")
        raise HTTPException(status_code=500, detail="Failed to get user preferences.")

@router.get("/users/{user_id}/feed", response_model=List[FeedItem])
async def get_user_feed_endpoint(user_id: str, limit: int = 10):
    """Get personalized feed for user"""
    try:
        return await get_user_feed(user_id, limit)
    except Exception as e:
        logger.exception("Error getting user feed")
        raise HTTPException(status_code=500, detail="Failed to get user feed.")

@router.get("/users/{user_id}/next", response_model=dict)
async def get_next_item(user_id: str):
    """Get the next item for swiping"""
    try:
        next_item = await get_next_feed_item(user_id)
        if next_item:
            return next_item
        else:
            return {"message": "No more items to show", "item": None}
    except Exception as e:
        logger.exception("Error getting next item")
        raise HTTPException(status_code=500, detail="Failed to get next item.")
