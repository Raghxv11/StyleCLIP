#!/usr/bin/env python3
"""
Debug script to check why the feed is empty
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from backend.app.config.database import init_db, get_db
from bson import ObjectId

async def debug_feed():
    """Debug the feed system"""
    await init_db()
    db = await get_db().__anext__()
    
    test_user_id = "68bb595b32342cc4cdd5ee61"
    
    print(f"🔍 Debugging feed for user: {test_user_id}")
    
    # Check if user exists
    user = await db.users.find_one({"_id": ObjectId(test_user_id)})
    if not user:
        print("❌ User not found!")
        return
    print(f"✅ User found: {user['username']}")
    
    # Check total clothing items
    total_items = await db.clothing_items.count_documents({})
    print(f"📊 Total clothing items in database: {total_items}")
    
    # Check user's swipes
    swiped_item_ids = await db.swipes.distinct(
        "clothing_item_id", 
        {"user_id": ObjectId(test_user_id)}
    )
    print(f"👆 Items user has swiped on: {len(swiped_item_ids)}")
    
    # Check available items (not swiped)
    query = {"_id": {"$nin": swiped_item_ids}}
    available_items = await db.clothing_items.count_documents(query)
    print(f"🎯 Available items for user: {available_items}")
    
    # Get some sample available items
    cursor = db.clothing_items.find(query).limit(5)
    sample_items = []
    async for item in cursor:
        sample_items.append({
            "id": str(item["_id"]),
            "filename": item["filename"],
            "garment_type": item.get("garment_type", "Unknown"),
            "tags": item.get("tags", [])[:3]
        })
    
    print(f"\n📋 Sample available items:")
    for item in sample_items:
        print(f"  - {item['filename']}: {item['garment_type']} - {', '.join(item['tags'])}")
    
    # Test the get_next_feed_item function
    print(f"\n🧪 Testing get_next_feed_item function...")
    from backend.app.controllers.user_controller import get_next_feed_item
    next_item = await get_next_feed_item(test_user_id)
    
    if next_item:
        print(f"✅ Next item found: {next_item['filename']}")
    else:
        print("❌ No next item found")

if __name__ == "__main__":
    asyncio.run(debug_feed())
