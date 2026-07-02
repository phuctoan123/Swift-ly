"""Analytics Worker to process click events from Redis Stream."""

import asyncio
import json
import logging
import os
from datetime import datetime

import geoip2.database
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from user_agents import parse

from app.config import get_settings
from app.database import AsyncSessionLocal
from app.models.url import ClickEvent

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log = logging.getLogger("worker")

settings = get_settings()

STREAM_KEY = "url_click_stream"
GROUP_NAME = "analytics_group"
CONSUMER_NAME = f"consumer-{os.getpid()}"

# Load GeoIP Database if exists
GEOIP_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "GeoLite2-City.mmdb")
geoip_reader = None
if os.path.exists(GEOIP_DB_PATH):
    try:
        geoip_reader = geoip2.database.Reader(GEOIP_DB_PATH)
        log.info(f"Loaded GeoIP database from {GEOIP_DB_PATH}")
    except Exception as e:
        log.warning(f"Failed to load GeoIP database: {e}")
else:
    log.warning(f"GeoIP database not found at {GEOIP_DB_PATH}. IP Geolocation will be disabled.")


def parse_user_agent(ua_string: str):
    """Parse user agent string to extract device info."""
    if not ua_string:
        return None, None, None
        
    ua = parse(ua_string)
    device_type = "desktop"
    if ua.is_mobile:
        device_type = "mobile"
    elif ua.is_tablet:
        device_type = "tablet"
        
    return device_type, ua.browser.family, ua.os.family


def get_geoip_info(ip_address: str):
    """Lookup IP to get country and city."""
    if not geoip_reader or not ip_address:
        return None, None
        
    # Xử lý local IP
    if ip_address in ("127.0.0.1", "::1", "localhost") or ip_address.startswith(("192.168.", "10.")):
        return "Local", "Local"
        
    try:
        response = geoip_reader.city(ip_address)
        country = response.country.iso_code
        city = response.city.name
        return country, city
    except Exception:
        return None, None


async def process_messages(db: AsyncSession, messages: list):
    """Process a batch of messages and insert into DB."""
    events_to_insert = []
    message_ids = []
    
    for stream, stream_msgs in messages:
        for msg_id, msg_data in stream_msgs:
            try:
                data = json.loads(msg_data["data"])
                
                device_type, browser, os_family = parse_user_agent(data.get("user_agent"))
                country, city = get_geoip_info(data.get("ip_address"))
                
                event = ClickEvent(
                    short_code=data["short_code"],
                    clicked_at=datetime.fromisoformat(data["clicked_at"]),
                    ip_address=data.get("ip_address"),
                    user_agent=data.get("user_agent"),
                    referer=data.get("referer"),
                    country_code=country,
                    city=city,
                    device_type=device_type,
                    browser=browser,
                    os=os_family,
                )
                events_to_insert.append(event)
                message_ids.append(msg_id)
            except Exception as e:
                log.error(f"Error processing message {msg_id}: {e}")
                # Vẫn ack message lỗi để không bị kẹt
                message_ids.append(msg_id)
                
    if events_to_insert:
        db.add_all(events_to_insert)
        try:
            await db.commit()
            log.info(f"Inserted {len(events_to_insert)} click events.")
        except Exception as e:
            await db.rollback()
            log.error(f"Failed to insert events to DB: {e}")
            return [] # Không ack nếu lỗi DB
            
    return message_ids


async def main():
    """Main worker loop."""
    log.info("Starting Analytics Worker...")
    
    redis = await aioredis.from_url(settings.redis_url, decode_responses=True)
    
    # Create consumer group
    try:
        await redis.xgroup_create(STREAM_KEY, GROUP_NAME, id="0", mkstream=True)
        log.info(f"Created consumer group {GROUP_NAME} for stream {STREAM_KEY}")
    except aioredis.ResponseError as e:
        if "BUSYGROUP Consumer Group name already exists" not in str(e):
            log.error(f"Failed to create consumer group: {e}")
            raise
    
    while True:
        try:
            # Read messages
            messages = await redis.xreadgroup(
                GROUP_NAME, 
                CONSUMER_NAME, 
                {STREAM_KEY: ">"}, 
                count=100, 
                block=5000
            )
            
            if messages:
                async with AsyncSessionLocal() as db:
                    processed_ids = await process_messages(db, messages)
                    if processed_ids:
                        await redis.xack(STREAM_KEY, GROUP_NAME, *processed_ids)
            
        except Exception as e:
            log.error(f"Worker loop error: {e}")
            await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Worker stopped.")
