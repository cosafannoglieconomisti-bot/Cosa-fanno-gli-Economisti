import asyncio
import os
import json
import sys

# Ensure we can import notebooklm_tools
sys.path.append('/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages')

from notebooklm_tools.core.client import NotebookLMClient

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
    
    print("Fetching notebooks...")
    notebooks = await client.get_notebooks()
    for nb in notebooks:
        print(f"[{nb['id']}] {nb['title']}")

if __name__ == "__main__":
    asyncio.run(main())
