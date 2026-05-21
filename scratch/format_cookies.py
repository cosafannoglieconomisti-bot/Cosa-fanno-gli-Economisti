import json
import sys

def format_cookies(file_path):
    with open(file_path, 'r') as f:
        cookies = json.load(f)
    
    cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
    print(cookie_str)

if __name__ == "__main__":
    format_cookies(sys.argv[1])
