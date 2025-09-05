#!/usr/bin/env python3
"""
Create a test user for the Tinder-like clothing app
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from backend.app.config.database import init_db, get_db
from backend.app.config.settings import settings
from datetime import datetime

async def create_test_user():
    """Create a test user for development"""
    await init_db()
    db = await get_db().__anext__()
    
    # Create test user
    test_user = {
        "username": "testuser",
        "email": "test@example.com",
        "preferences": {},
        "created_at": datetime.utcnow(),
        "last_active": datetime.utcnow()
    }
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": "test@example.com"})
    if existing_user:
        print(f"✅ Test user already exists with ID: {existing_user['_id']}")
        return str(existing_user['_id'])
    
    # Insert test user
    result = await db.users.insert_one(test_user)
    user_id = str(result.inserted_id)
    
    print(f"✅ Test user created successfully!")
    print(f"📧 Email: test@example.com")
    print(f"👤 Username: testuser")
    print(f"🆔 User ID: {user_id}")
    print(f"🔗 Use this ID for testing: {user_id}")
    
    return user_id

if __name__ == "__main__":
    asyncio.run(create_test_user())
