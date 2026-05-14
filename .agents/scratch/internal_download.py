import asyncio
import os
import json
import sys

# Ensure we can import notebooklm_tools
sys.path.append('/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages')

from notebooklm_tools.core.client import NotebookLMClient
from notebooklm_tools.services.downloads import download_async

async def main():
    mcp_auth_path = os.path.expanduser('~/.notebooklm-mcp/auth.json')
    if not os.path.exists(mcp_auth_path):
        print(f"Auth file not found at {mcp_auth_path}")
        return

    with open(mcp_auth_path) as f:
        auth = json.load(f)
    
    # Create client with cookies and csrf
    client = NotebookLMClient(
        cookies=auth['cookies'],
        csrf_token=auth['csrf_token'],
        session_id=auth.get('session_id', '')
    )
    
    notebook_id = "e7fb498e-5f32-4f35-976f-4b356c7e34cc"
    
    # Video
    video_id = "a1012550-432a-436c-80bb-7b696545c884"
    video_path = "/Users/marcolemoglie_1_2/Downloads/Poveri_in_Pensione_raw.mp4"
    
    print(f"Downloading video {video_id}...")
    try:
        res = await download_async(
            client,
            notebook_id,
            "video",
            video_path,
            artifact_id=video_id
        )
        print(f"Video downloaded successfully to {res['path']}")
    except Exception as e:
        print(f"Video download failed: {str(e)}")
        
    # Infographic
    info_id = "7256ce5e-4d20-491e-8458-163bd95570e2"
    info_path = "/Users/marcolemoglie_1_2/Downloads/infografica_raw.png"
    
    print(f"Downloading infographic {info_id}...")
    try:
        res = await download_async(
            client,
            notebook_id,
            "infographic",
            info_path,
            artifact_id=info_id
        )
        print(f"Infographic downloaded successfully to {res['path']}")
    except Exception as e:
        print(f"Infographic download failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
