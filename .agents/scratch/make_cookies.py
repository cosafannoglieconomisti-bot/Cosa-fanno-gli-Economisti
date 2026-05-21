import json
import os

# Source
mcp_auth_path = os.path.expanduser('~/.notebooklm-mcp/auth.json')
with open(mcp_auth_path) as f:
    mcp_auth = json.load(f)

# Netscape cookie format:
# domain  domain_specified  path  secure  expires  name  value
with open('/Users/marcolemoglie_1_2/Desktop/canale/.agents/scratch/cookies.txt', 'w') as f:
    f.write("# Netscape HTTP Cookie File\n")
    for name, value in mcp_auth['cookies'].items():
        # Using a long expiration and common flags
        f.write(f".google.com\tTRUE\t/\tTRUE\t2147483647\t{name}\t{value}\n")

print("[SUCCESS] Created cookies.txt in Netscape format.")
