import json

def cookies_to_string(cookies_json_path):
    with open(cookies_json_path, 'r') as f:
        cookies = json.load(f)
    
    return "; ".join([f"{c['name']}={c['value']}" for c in cookies])

if __name__ == "__main__":
    cookies_str = cookies_to_string("/Users/marcolemoglie_1_2/.notebooklm-mcp-cli/profiles/default/cookies.json")
    print(cookies_str)
