import re
import os

def fix_file(path):
    with open(path, 'r') as f:
        content = f.read()
    
    # Remove the partial comments I made that broke syntax
    # Pattern 1: # console.print( followed by lines then )
    # This is hard with regex. 
    # Let's just remove the # from # console.print and # Panel.fit
    # and then at the top of the file, redefine console to use stderr.
    
    content = content.replace("# console.print", "console.print")
    content = content.replace("# Panel.fit", "Panel.fit")
    content = content.replace("# f\"", "f\"") # common for multi-line f-strings
    content = content.replace("# \"", "\"") 
    
    # Also fix config.py prints
    content = content.replace("# print(", "import sys; sys.stderr.write(")
    
    with open(path, 'w') as f:
        f.write(content)

# Fix cli.py
fix_file("/Users/marcolemoglie_1_2/Desktop/canale/.venv/lib/python3.11/site-packages/notebooklm_mcp/cli.py")
# Fix config.py
fix_file("/Users/marcolemoglie_1_2/Desktop/canale/.venv/lib/python3.11/site-packages/notebooklm_mcp/config.py")
