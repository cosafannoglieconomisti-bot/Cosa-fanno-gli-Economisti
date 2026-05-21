import json

def extract_cookies_from_mcp(mcp_auth_path):
    with open(mcp_auth_path, 'r') as f:
        data = json.load(f)
    
    cookies = data.get('cookies', {})
    return "; ".join([f"{name}={value}" for name, value in cookies.items()])

if __name__ == "__main__":
    mcp_path = "/Users/marcolemoglie_1_2/.notebooklm-mcp/auth.json"
    cookies_str = extract_cookies_from_mcp(mcp_path)
    print(cookies_str)
