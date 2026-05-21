import re

path = "/Users/marcolemoglie_1_2/Desktop/canale/.venv/lib/python3.11/site-packages/notebooklm_mcp/cli.py"
with open(path, 'r') as f:
    content = f.read()

# Remove my broken comment markers
content = re.sub(r'^#\s*', '', content, flags=re.MULTILINE)
# This is dangerous because it uncomments EVERYTHING.
# But wait, I can just restore from the original file if I had it.
# I don't.

# Let's try to be more specific.
# Only uncomment if the line looks like it belongs to console.print or Panel
content = re.sub(r'^#\s*(console\.print|Panel\.fit|f"|"\s*|[^#\n]*\))', r'\1', content, flags=re.MULTILINE)

# Fix the specific line 87 thing
content = content.replace("# )", ")")
content = content.replace("#)", ")")

with open(path, 'w') as f:
    f.write(content)
