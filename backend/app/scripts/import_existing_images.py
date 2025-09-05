#!/usr/bin/env python3
"""
Import existing images from uploads folder into the database for the Tinder app
"""

import asyncio
import os
import sys
import glob
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from backend.app.config.database import init_db, get_db
from backend.app.models.clip_model import CLIPModel
from backend.app.controllers.tag_extractor import TagExtractor
from backend.app.config.tag_list_en import GARMENT_TYPES

async def import_existing_images():
    """Import all existing images from uploads folder into the database"""
    await init_db()
    db = await get_db().__anext__()
    
    # Initialize models
    clip_model = CLIPModel()
    tag_extractor = TagExtractor(tag_dict=GARMENT_TYPES)
    
    # Get all image files from uploads folder
    uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "uploads")
    image_files = glob.glob(os.path.join(uploads_dir, "*.jpg")) + glob.glob(os.path.join(uploads_dir, "*.jpeg")) + glob.glob(os.path.join(uploads_dir, "*.png"))
    
    print(f"📁 Found {len(image_files)} images in uploads folder")
    
    # Check which images are already in the database
    existing_files = set()
    async for item in db.clothing_items.find({}, {"filename": 1}):
        existing_files.add(item["filename"])
    
    print(f"📊 {len(existing_files)} images already in database")
    
    imported_count = 0
    skipped_count = 0
    error_count = 0
    
    for i, image_path in enumerate(image_files):
        filename = os.path.basename(image_path)
        
        # Skip if already in database
        if filename in existing_files:
            skipped_count += 1
            continue
        
        try:
            print(f"🔄 Processing {i+1}/{len(image_files)}: {filename}")
            
            # Get embedding
            embedding = clip_model.get_image_embedding(image_path)
            
            # Determine garment type
            garment_type = tag_extractor.determine_garment_type(embedding)
            
            # Extract tags
            if garment_type != "Unknown":
                tags_dict = tag_extractor.extract_tags(embedding, garment_type)
                tags = list(tags_dict.values())
            else:
                tags = ["Unknown garment type"]
            
            # Create clothing item document
            clothing_item = {
                "filename": filename,
                "image_path": image_path,
                "embedding": embedding.squeeze().tolist(),
                "tags": tags,
                "garment_type": garment_type,
                "uploaded_at": datetime.utcnow()
            }
            
            # Insert into database
            await db.clothing_items.insert_one(clothing_item)
            imported_count += 1
            
            if imported_count % 10 == 0:
                print(f"✅ Imported {imported_count} items so far...")
                
        except Exception as e:
            print(f"❌ Error processing {filename}: {str(e)}")
            error_count += 1
            continue
    
    print(f"\n🎉 Import completed!")
    print(f"✅ Imported: {imported_count} items")
    print(f"⏭️  Skipped: {skipped_count} items (already in database)")
    print(f"❌ Errors: {error_count} items")
    print(f"📊 Total items in database: {imported_count + skipped_count}")
    
    # Show some sample items
    print(f"\n📋 Sample items in database:")
    async for item in db.clothing_items.find({}).limit(5):
        print(f"  - {item['filename']}: {item['garment_type']} - {', '.join(item['tags'][:3])}")

if __name__ == "__main__":
    asyncio.run(import_existing_images())
