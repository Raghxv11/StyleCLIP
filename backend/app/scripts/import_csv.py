import asyncio
import sys
from pathlib import Path
import csv
import os
import uuid
from datetime import datetime
from typing import Optional

import aiohttp
from motor.motor_asyncio import AsyncIOMotorDatabase

"""Allow running this script directly without setting PYTHONPATH.
It prepends the repo root (StyleCLIP) to sys.path so 'backend.app' imports resolve.
"""
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.models.clip_model import CLIPModel
from backend.app.controllers.tag_extractor import TagExtractor
from backend.app.config.tag_list_en import GARMENT_TYPES
from backend.app.config.database import init_db, get_db, close_db


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def download_image(session: aiohttp.ClientSession, url: str, filename: Optional[str] = None, insecure: bool = False) -> Optional[str]:
    name = filename or f"{uuid.uuid4().hex}.jpg"
    path = os.path.join(UPLOAD_DIR, name)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        "Referer": "https://us.princesspolly.com/",
    }
    timeout = aiohttp.ClientTimeout(total=60)
    last_error = None
    for attempt in range(3):
        try:
            async with session.get(url, headers=headers, timeout=timeout, allow_redirects=True, ssl=False if insecure else None) as resp:
                if resp.status != 200:
                    text = await resp.text(errors="ignore")
                    snippet = text[:120].replace("\n", " ") if text else ""
                    print(f"Skip {url}: HTTP {resp.status} {resp.reason} {snippet}")
                    last_error = f"HTTP {resp.status}"
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                data = await resp.read()
                with open(path, "wb") as f:
                    f.write(data)
                return path
        except Exception as e:
            last_error = str(e)
            await asyncio.sleep(0.5 * (attempt + 1))
            continue
    print(f"Error downloading {url}: {last_error}")
    return None


async def process_row(db: AsyncIOMotorDatabase, session: aiohttp.ClientSession, clip_model: CLIPModel, tag_extractor: TagExtractor, url: str, external_id: Optional[str] = None, insecure: bool = False):
    image_path = await download_image(session, url, insecure=insecure)
    if not image_path:
        return

    try:
        embedding = clip_model.get_image_embedding(image_path)
        garment_type = tag_extractor.determine_garment_type(embedding)
        if garment_type != "Unknown":
            tags_dict = tag_extractor.extract_tags(embedding, garment_type)
            tags = list(tags_dict.values())
        else:
            tags = ["Unknown garment type"]

        doc = {
            "external_id": external_id,
            "original_url": url,
            "filename": os.path.basename(image_path),
            "image_path": image_path,
            "embedding": embedding.squeeze().tolist(),
            "tags": tags,
            "garment_type": garment_type,
            "uploaded_at": datetime.utcnow(),
        }

        if external_id:
            await db.clothing_items.update_one({"external_id": external_id}, {"$set": doc}, upsert=True)
        else:
            await db.clothing_items.insert_one(doc)

    except Exception as e:
        print(f"Failed to process {url}: {e}")


async def main(csv_path: str, url_column: str = "image_url", id_column: Optional[str] = None, concurrency: int = 8, insecure: bool = False):
    await init_db()
    db = await get_db().__anext__()

    clip_model = CLIPModel()
    tag_extractor = TagExtractor(tag_dict=GARMENT_TYPES)

    connector = aiohttp.TCPConnector(limit=concurrency)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row.get(url_column)
                if not url:
                    continue
                external_id = row.get(id_column) if id_column else None
                tasks.append(process_row(db, session, clip_model, tag_extractor, url, external_id, insecure=insecure))

        # Run in chunks to avoid overwhelming memory
        CHUNK = concurrency * 10
        for i in range(0, len(tasks), CHUNK):
            await asyncio.gather(*tasks[i:i+CHUNK])

    await close_db()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Import clothing items from CSV URLs")
    parser.add_argument("csv_path", help="Path to CSV file")
    parser.add_argument("--url-column", default="image_url", help="CSV column containing image URL")
    parser.add_argument("--id-column", default=None, help="Optional CSV column to use as external_id for upserts")
    parser.add_argument("--concurrency", type=int, default=8, help="Max concurrent HTTP downloads")
    parser.add_argument("--insecure", action="store_true", help="Disable SSL verification for image downloads (use only if necessary)")

    args = parser.parse_args()
    asyncio.run(main(args.csv_path, args.url_column, args.id_column, args.concurrency, args.insecure))


