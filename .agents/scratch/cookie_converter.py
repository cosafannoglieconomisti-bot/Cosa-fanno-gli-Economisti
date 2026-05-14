import json
import os

def json_to_netscape(json_path, netscape_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    cookies = data.get('cookies', {})
    
    with open(netscape_path, 'w') as f:
        f.write("# Netscape HTTP Cookie File\n")
        f.write("# http://curl.haxx.se/rfc/cookie_spec.html\n")
        f.write("# This is a generated file!  Do not edit.\n\n")
        
        for name, value in cookies.items():
            # Domain, IncludeSubdomains, Path, Secure, Expiry, Name, Value
            # For simplicity, we'll use .google.com
            domain = ".google.com"
            f.write(f"{domain}\tTRUE\t/\tTRUE\t2147483647\t{name}\t{value}\n")

if __name__ == "__main__":
    json_to_netscape("/Users/marcolemoglie_1_2/.notebooklm-mcp/auth.json", "/Users/marcolemoglie_1_2/Desktop/canale/Temp/cookies.txt")
