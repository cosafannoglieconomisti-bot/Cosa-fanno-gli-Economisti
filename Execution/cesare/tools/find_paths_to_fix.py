import os
import re

def find_paths():
    search_dir = 'Execution'
    # Pattern to find absolute paths or old folder structures
    # Examples: /Users/... or [Romolo] ...
    patterns = [
        r'/Users/marcolemoglie_1_2/',
        r'\[Augusto\]',
        r'\[Romolo\]',
        r'\[Enea\]',
        r'\[Marcello\]',
        r'\[Ulisse\]',
        r'\[Mercurio\]',
        r'\[Cesare\]'
    ]
    
    results = []
    for root, dirs, files in os.walk(search_dir):
        for file in files:
            if file.endswith('.py') or file.endswith('.sh'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            for pattern in patterns:
                                if re.search(pattern, line):
                                    results.append(f"{filepath}:{i+1}: {line.strip()}")
                                    break # Only report once per line
                except Exception as e:
                     pass # Ignore binary or encoding issues
                     
    for r in results:
        print(r)

if __name__ == '__main__':
    find_paths()
