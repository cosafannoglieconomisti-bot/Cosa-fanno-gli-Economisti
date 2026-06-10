import json
import os

# Source
mcp_auth_path = os.path.expanduser('~/.notebooklm-mcp/auth.json')
with open(mcp_auth_path) as f:
    mcp_auth = json.load(f)

# Target profile paths
profile_dir = os.path.expanduser('~/.notebooklm-mcp-cli/profiles/default')
cookies_path = os.path.join(profile_dir, 'cookies.json')
metadata_path = os.path.join(profile_dir, 'metadata.json')

# 1. Update metadata.json
if os.path.exists(metadata_path):
    with open(metadata_path) as f:
        metadata = json.load(f)
else:
    metadata = {}

metadata['csrf_token'] = mcp_auth['csrf_token']
metadata['session_id'] = mcp_auth.get('session_id', '')
# build_label is often part of the session ID or separate
if 'boq_labs' in metadata.get('csrf_token', ''):
     pass # already there maybe

with open(metadata_path, 'w') as f:
    json.dump(metadata, f, indent=2)

# 2. Update cookies.json
cookies_list = []
for name, value in mcp_auth['cookies'].items():
    cookies_list.append({
        "name": name,
        "value": value,
        "domain": ".google.com",
        "path": "/",
        "secure": True,
        "httpOnly": False
    })
with open(cookies_path, 'w') as f:
    json.dump(cookies_list, f, indent=2)

print("[SUCCESS] Credentials synced to nlm CLI profile.")
