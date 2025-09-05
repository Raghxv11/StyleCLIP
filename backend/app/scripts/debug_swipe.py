#!/usr/bin/env python3
"""
Debug script to test swipe functionality
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from backend.app.config.database import init_db, get_db
from backend.app.controllers.user_controller import record_swipe
from backend.app.schemas.clothing_schemas import SwipeRequest
from bson import ObjectId

async def debug_swipe():
    """Debug the swipe functionality"""
    await init_db()
    db = await get_db().__anext__()
    
    test_user_id = "68bb595b32342cc4cdd5ee61"
    test_item_id = "68baacd27127cd83f0fd8186"
    
    print(f"🔍 Testing swipe functionality")
    print(f"User ID: {test_user_id}")
    print(f"Item ID: {test_item_id}")
    
    # Check if user exists
    user = await db.users.find_one({"_id": ObjectId(test_user_id)})
    if not user:
        print("❌ User not found!")
        return
    print(f"✅ User found: {user['username']}")
    
    # Check if item exists
    item = await db.clothing_items.find_one({"_id": ObjectId(test_item_id)})
    if not item:
        print("❌ Item not found!")
        return
    print(f"✅ Item found: {item['filename']}")
    
    # Test swipe
    try:
        swipe_request = SwipeRequest(
            user_id=test_user_id,
            clothing_item_id=test_item_id,
            action="like"
        )
        
        print(f"🔄 Testing swipe...")
        result = await record_swipe(test_user_id, swipe_request)
        print(f"✅ Swipe successful: {result}")
        
    except Exception as e:
        print(f"❌ Swipe failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_swipe())
