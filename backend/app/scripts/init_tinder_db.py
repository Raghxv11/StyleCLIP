#!/usr/bin/env python3
"""
Initialize database collections for the Tinder-like clothing app
"""

import asyncio
from backend.app.config.database import init_db, get_db
from backend.app.config.settings import settings

async def create_collections():
    """Create necessary collections with indexes"""
    await init_db()
    db = await get_db().__anext__()
    
    # Create users collection with indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("username")
    await db.users.create_index("last_active")
    
    # Create swipes collection with indexes
    await db.swipes.create_index("user_id")
    await db.swipes.create_index("clothing_item_id")
    await db.swipes.create_index([("user_id", 1), ("clothing_item_id", 1)], unique=True)
    await db.swipes.create_index("timestamp")
    
    # Create clothing_items collection with indexes (if not exists)
    await db.clothing_items.create_index("filename")
    await db.clothing_items.create_index("garment_type")
    await db.clothing_items.create_index("uploaded_at")
    
    print("✅ Database collections and indexes created successfully!")
    print(f"📊 Database: {settings.MONGO_DB_NAME}")
    print("📋 Collections created:")
    print("   - users (with email, username, last_active indexes)")
    print("   - swipes (with user_id, clothing_item_id, timestamp indexes)")
    print("   - clothing_items (with filename, garment_type, uploaded_at indexes)")

if __name__ == "__main__":
    asyncio.run(create_collections())
