#!/usr/bin/env python3
"""
Reset user preferences for testing
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from backend.app.config.database import init_db, get_db
from bson import ObjectId

async def reset_user_preferences(user_id=None):
    """Reset user preferences and swipes for testing"""
    await init_db()
    db = await get_db().__anext__()
    
    if user_id:
        # Reset specific user
        user_object_id = ObjectId(user_id)
        
        # Clear user preferences
        await db.users.update_one(
            {"_id": user_object_id},
            {"$set": {"preferences": {}}}
        )
        
        # Delete all swipes for this user
        result = await db.swipes.delete_many({"user_id": user_object_id})
        
        print(f"✅ Reset user {user_id}")
        print(f"🗑️  Deleted {result.deleted_count} swipes")
        print(f"🔄 Cleared preferences")
        
    else:
        # Reset all users
        await db.users.update_many({}, {"$set": {"preferences": {}}})
        await db.swipes.delete_many({})
        
        print("✅ Reset all users")
        print("🗑️  Deleted all swipes")
        print("🔄 Cleared all preferences")

if __name__ == "__main__":
    import sys
    user_id = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(reset_user_preferences(user_id))
