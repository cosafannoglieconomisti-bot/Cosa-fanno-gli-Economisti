import requests
import json
import os
import sys

# Buffer API Config
ACCESS_TOKEN = [REDACTED]
FB_PROFILE_ID = "69baada37be9f8b1716baa0d"
API_BASE = "https://api.bufferapp.com/1"

def get_pending_count():
    url = f"{API_BASE}/profiles/{FB_PROFILE_ID}/updates/pending.json?access_token={ACCESS_TOKEN}"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            return res.json().get('total', 0)
    except:
        pass
    return 0

def schedule_post(text, video_url, thumbnail_url=None, scheduled_at=None):
    """
    Schedules a post via Buffer API.
    video_url: The YouTube link.
    thumbnail_url: Optional, overrides the default preview image.
    scheduled_at: String 'YYYY-MM-DD HH:MM:SS'
    """
    pending = get_pending_count()
    if pending >= 10:
        print(f"FAILED: Buffer Queue is FULL (10/10). Please share or delete some posts.")
        return False

    url = f"{API_BASE}/updates/create.json?access_token={ACCESS_TOKEN}"
    
    payload = {
        "text": text,
        "profile_ids[]": [FB_PROFILE_ID],
        "media[link]": video_url
    }
    
    if thumbnail_url:
        payload["media[picture]"] = thumbnail_url
    if scheduled_at:
        payload["scheduled_at"] = scheduled_at
        
    res = requests.post(url, data=payload)
    if res.status_code == 200:
        print(f"SUCCESS: Post scheduled correctly.")
        return True
    else:
        print(f"ERROR: Buffer API returned {res.status_code} - {res.text}")
        return False

if __name__ == "__main__":
    # This script can be extended to automatically find unposted videos
    print("Buffer Sync Today - Marcello")
    # For manual usage or integration in other workflows
