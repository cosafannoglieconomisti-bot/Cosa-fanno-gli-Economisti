import re

def fix_cli(path):
    with open(path, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    in_broken_block = False
    indent = ""
    
    for line in lines:
        # If line starts with '# console.print(' and ends with '('
        if re.match(r'^\s*# console\.print\($', line.rstrip()):
            in_broken_block = True
            new_lines.append(line)
            continue
        
        if in_broken_block:
            # Comment out line until we find the closing parenthesis
            new_lines.append("# " + line.lstrip())
            if line.strip() == ")":
                in_broken_block = False
            elif line.rstrip().endswith(")") or line.rstrip().endswith("),"):
                # Check if it's the end of a multi-line call
                # This is tricky, but usually these calls end with )
                # Let's count parentheses
                if line.count('(') <= line.count(')'):
                     in_broken_block = False
            continue
        
        # Also fix lines like '# console.print(' (without the trailing paren on same line)
        if re.match(r'^\s*# console\.print\($', line.rstrip()):
             # handled above
             pass
        elif re.search(r'^\s*# console\.print\(', line) and not line.rstrip().endswith(')'):
             in_broken_block = True
             new_lines.append(line)
        else:
             new_lines.append(line)

    with open(path, 'w') as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    fix_cli("/Users/marcolemoglie_1_2/Desktop/canale/.venv/lib/python3.11/site-packages/notebooklm_mcp/cli.py")
