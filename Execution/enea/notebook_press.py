#!/usr/bin/env python3
import sys
import os
import re
import time
import json
import shutil
import subprocess
import argparse
import requests

# Append system site-packages path to import system-installed notebooklm_tools
sys.path.append("/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages")

try:
    from notebooklm_tools.core.auth import get_auth_manager
    from notebooklm_tools.cli.utils import get_client
except ImportError:
    print("[!] Warning: Could not import notebooklm_tools components. Path configuration might be incorrect.")

# =========================================================================
# Path Detection & Utility Functions
# =========================================================================

def get_drive_papers_dir():
    """Detects and returns the active Google Drive Papers path."""
    paths = [
        "/Users/marcolemoglie_1_2/Library/CloudStorage/GoogleDrive-cosafannoglieconomisti@gmail.com/Il mio Drive/Papers",
        "/Users/marcolemoglie_1_2/Google Drive/Papers"
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None

def get_google_drive_id(filepath, max_wait=45):
    """Polls macOS xattr to resolve the Google Drive File ID for a synced file."""
    print(f"[*] Polling Google Drive File ID for: {filepath}")
    for i in range(max_wait):
        try:
            res = subprocess.check_output(
                ["xattr", "-p", "com.google.drivefs.item-id#S", filepath],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            if res:
                print(f"[+] Google Drive File ID found: {res}")
                return res
        except Exception:
            pass
        time.sleep(1)
    print("[!] Warning: Google Drive ID polling timed out. Syncing might be delayed.")
    return None

def get_video_url(client, notebook_id, artifact_id=None):
    """Helper to extract direct video URL from studio metadata."""
    try:
        artifacts = client._list_raw(notebook_id)
        candidates = []
        for a in artifacts:
            if isinstance(a, list) and len(a) > 4:
                # Type 3 represents STUDIO_TYPE_VIDEO, Status 3 represents completed
                if a[2] == 3 and a[4] == 3:
                    candidates.append(a)
        if not candidates:
            return None
        target = candidates[0]
        if artifact_id:
            target = next((a for a in candidates if a[0] == artifact_id), candidates[0])
            
        metadata = target[8]
        media_list = None
        for item in metadata:
            if (
                isinstance(item, list)
                and len(item) > 0
                and isinstance(item[0], list)
                and len(item[0]) > 0
                and isinstance(item[0][0], str)
                and item[0][0].startswith("http")
            ):
                media_list = item
                break
        if not media_list:
            return None
            
        url = None
        for item in media_list:
            if isinstance(item, list) and len(item) > 2 and item[2] == "video/mp4":
                url = item[0]
                if len(item) > 1 and item[1] == 4:
                    break
        if not url and len(media_list) > 0 and isinstance(media_list[0], list):
            url = media_list[0][0]
        return url
    except Exception as e:
        print(f"[!] Warning extracting video URL: {e}")
        return None

def get_infographic_url(client, notebook_id, artifact_id=None):
    """Helper to extract direct infographic URL from studio metadata."""
    try:
        artifacts = client._list_raw(notebook_id)
        candidates = []
        for a in artifacts:
            if isinstance(a, list) and len(a) > 5:
                # Type 7 represents STUDIO_TYPE_INFOGRAPHIC, Status 3 represents completed
                if a[2] == 7 and a[4] == 3:
                    candidates.append(a)
        if not candidates:
            return None
        target = candidates[0]
        if artifact_id:
            target = next((a for a in candidates if a[0] == artifact_id), candidates[0])
            
        metadata = target[14]
        media_data = metadata[2]
        media_item = media_data[0]
        url_data = media_item[1]
        return url_data[0]
    except Exception as e:
        print(f"[!] Warning extracting infographic URL: {e}")
        return None

def is_valid_binary_file(filepath):
    """Checks if the downloaded file is a valid binary instead of an HTML page."""
    if not os.path.exists(filepath):
        return False
    size = os.path.getsize(filepath)
    if size < 50 * 1024:  # At least 50 KB
        # Check if the file starts with HTML markup
        try:
            with open(filepath, 'rb') as f:
                header = f.read(1024)
                if b'<!DOCTYPE' in header or b'<html' in header or b'<head' in header:
                    return False
        except Exception:
            pass
    return True

def refresh_cookies_from_chrome():
    """Connects to the active Chrome debugger on port 9222 and robustly extracts cookies, CSRF token, and session ID, updating auth.json."""
    import httpx
    import websocket
    from pathlib import Path
    
    def execute_cdp_command(ws, method, params=None, command_id=1):
        command = {
            "id": command_id,
            "method": method,
            "params": params or {}
        }
        ws.send(json.dumps(command))
        while True:
            try:
                msg = ws.recv()
                if not msg:
                    continue
                response = json.loads(msg)
                if response.get("id") == command_id:
                    if "error" in response:
                        print(f"[!] CDP Error for {method}: {response['error']}")
                        return None
                    return response.get("result", {})
            except Exception as e:
                print(f"[!] Error reading CDP response: {e}")
                return None

    print("[*] Connecting to active Chrome window via CDP on port 9222...")
    try:
        r = httpx.get("http://127.0.0.1:9222/json", timeout=3)
        pages = r.json()
    except Exception as e:
        print(f"[!] Active Chrome debug window not found on port 9222: {e}")
        return False

    target = None
    # Prioritize NotebookLM or Google pages
    for p in pages:
        if p.get('webSocketDebuggerUrl') and p.get('type') == 'page' and ('notebooklm.google' in p.get('url', '') or 'google.com' in p.get('url', '')):
            target = p
            break
    if not target:
        for p in pages:
            if p.get('webSocketDebuggerUrl') and p.get('type') == 'page':
                target = p
                break
    if not target:
        for p in pages:
            if p.get('webSocketDebuggerUrl'):
                target = p
                break
            
    if not target:
        print("[!] No active Chrome targets with WebSocket URL.")
        return False
        
    ws_url = target['webSocketDebuggerUrl']
    print(f"[*] Targeting page: {target.get('title', 'Unknown')} ({target.get('url', 'Unknown')})")
    try:
        ws = websocket.create_connection(ws_url, timeout=5, suppress_origin=True)
        
        # Enable network and runtime
        execute_cdp_command(ws, "Network.enable", command_id=1)
        execute_cdp_command(ws, "Runtime.enable", command_id=2)
        
        # Get cookies
        cookies_result = execute_cdp_command(ws, "Network.getAllCookies", command_id=3)
        cookies_list = cookies_result.get("cookies", []) if cookies_result else []
        
        # Get page HTML
        html_result = execute_cdp_command(ws, "Runtime.evaluate", {"expression": "document.documentElement.outerHTML"}, command_id=4)
        html = html_result.get("result", {}).get("value", "") if html_result else ""
        
        ws.close()
        
        if not cookies_list:
            print("[!] No cookies returned from Chrome.")
            return False
            
        cookies_dict = {c["name"]: c["value"] for c in cookies_list}
        
        # Required cookies to validate
        required = ["SID", "HSID", "SSID", "__Secure-1PSID", "__Secure-3PSID"]
        missing = [r for r in required if r not in cookies_dict]
        if missing:
            print(f"[!] Warning: missing required Google cookies: {missing}. Make sure you are logged into Google/NotebookLM.")
            
        # Extract CSRF token
        csrf_token = ""
        csrf_patterns = [
            r'"SNlM0e":"([^"]+)"',  # WIZ_global_data.SNlM0e
            r'at=([^&"]+)',  # Direct at= value
            r'"FdrFJe":"([^"]+)"',  # Alternative location
        ]
        for pattern in csrf_patterns:
            match = re.search(pattern, html)
            if match:
                csrf_token = match.group(1)
                break
                
        # Extract session ID
        session_id = ""
        sid_patterns = [
            r'"FdrFJe":"([^"]+)"',
            r'f\.sid["\s:=]+["\']?(\d+)',
            r'"cfb2h":"([^"]+)"',
        ]
        for pattern in sid_patterns:
            match = re.search(pattern, html)
            if match:
                session_id = match.group(1)
                break
                
        # 1. Update profiles/default files using AuthManager
        try:
            manager = get_auth_manager()
            manager.save_profile(
                cookies=cookies_list,
                csrf_token=csrf_token,
                session_id=session_id,
                force=True
            )
            print("[+] Saved updated tokens to default profile successfully.")
        except Exception as pe:
            print(f"[!] Warning: Could not save to default profile using manager: {pe}")
            
        # 2. Update ~/.notebooklm-mcp/auth.json and ~/.notebooklm-mcp-cli/auth.json
        cache_paths = [
            Path.home() / ".notebooklm-mcp" / "auth.json",
            Path.home() / ".notebooklm-mcp-cli" / "auth.json"
        ]
        
        for cache_path in cache_paths:
            try:
                existing_data = {}
                if cache_path.exists():
                    try:
                        with open(cache_path, 'r') as f:
                            existing_data = json.load(f)
                    except Exception:
                        pass
                        
                existing_data["cookies"] = cookies_dict
                existing_data["extracted_at"] = time.time()
                existing_data["csrf_token"] = csrf_token
                existing_data["session_id"] = session_id
                
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                with open(cache_path, 'w') as f:
                    json.dump(existing_data, f, indent=2)
                print(f"[+] Saved updated tokens to {cache_path}")
            except Exception as fe:
                print(f"[!] Warning: Could not save to legacy cache {cache_path}: {fe}")
                
        print(f"[+] Refreshed and updated {len(cookies_dict)} cookies, CSRF token, and Session ID in all locations.")
        return True
    except Exception as e:
        print(f"[!] Failed to extract tokens from Chrome: {e}")
        return False

# =========================================================================
# Subcommand Execution Functions
# =========================================================================

def cmd_auth(args):
    """Verifies active NotebookLM session status and profile configuration."""
    if getattr(args, "refresh", False):
        if not refresh_cookies_from_chrome():
            print(json.dumps({"status": "error", "message": "Failed to refresh cookies from active Chrome debugger window."}, indent=2))
            sys.exit(1)
            
    try:
        manager = get_auth_manager()
        if not manager.profile_exists():
            print(json.dumps({"status": "error", "message": "No active profile found. Please log in first."}, indent=2))
            sys.exit(1)
        profile = manager.load_profile()
        res = {
            "status": "authenticated",
            "profile_name": profile.name,
            "email": profile.email,
            "last_validated": str(profile.last_validated) if profile.last_validated else None,
            "has_cookies": True
        }
        print(json.dumps(res, indent=2))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}, indent=2))
        sys.exit(1)

def cmd_upload(args):
    """Copies a local PDF to the active Drive folder, waits for sync, and registers it as source."""
    drive_dir = get_drive_papers_dir()
    if not drive_dir:
        print(json.dumps({"status": "error", "message": "No Google Drive Papers folder detected on the system."}, indent=2))
        sys.exit(1)
        
    sanitized = re.sub(r'[:*?"<>|/]', ' ', args.title).strip()
    drive_dest = os.path.join(drive_dir, f"{sanitized}.pdf")
    
    print(f"[*] Copying {args.pdf_path} to {drive_dest}...")
    try:
        shutil.copy2(args.pdf_path, drive_dest)
    except Exception as e:
        print(json.dumps({"status": "error", "message": f"Failed to copy file to Drive folder: {e}"}, indent=2))
        sys.exit(1)
        
    drive_id = get_google_drive_id(drive_dest)
    if not drive_id:
        print(json.dumps({"status": "error", "message": "Google Drive File ID resolution timed out. Make sure Drive is running."}, indent=2))
        sys.exit(1)
        
    notebook_id = args.notebook_id
    created_new = False
    if not notebook_id:
        print(f"[*] Notebook ID not provided. Creating new notebook: {args.title}")
        try:
            res = subprocess.check_output(["nlm", "create", "notebook", args.title], stderr=subprocess.STDOUT).decode()
            match = re.search(r"ID:\s*([a-fA-F0-9-]+)", res)
            if match:
                notebook_id = match.group(1).strip()
            else:
                notebook_id = res.split("ID:")[1].strip().split()[0].replace(')', '')
            created_new = True
            print(f"[+] Notebook created: {notebook_id}")
        except Exception as e:
            print(json.dumps({"status": "error", "message": f"Failed to create notebook: {e}"}, indent=2))
            sys.exit(1)
            
    print(f"[*] Adding Drive source to Notebook {notebook_id}...")
    try:
        # SINTASSI: nlm source add <notebook_id> --drive <drive_id> --type pdf --title <title> --wait
        cmd = ["nlm", "source", "add", notebook_id, "--drive", drive_id, "--type", "pdf", "--title", args.title, "--wait"]
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except Exception as e:
        print(json.dumps({"status": "error", "message": f"Failed to add source: {e}"}, indent=2))
        sys.exit(1)
        
    res = {
        "status": "success",
        "notebook_id": notebook_id,
        "created_new": created_new,
        "drive_file_id": drive_id,
        "drive_path": drive_dest
    }
    print(json.dumps(res, indent=2))

def cmd_generate(args):
    """Triggers generation of the specified studio artifact (video/infographic)."""
    nb_id = args.notebook_id
    asset_type = args.type
    prompt = args.focus
    
    print(f"[*] Triggering {asset_type} generation for Notebook {nb_id}...")
    try:
        if asset_type == "video":
            cmd = ["nlm", "create", "video", nb_id, "--focus", prompt, "--language", "it", "-y"]
        elif asset_type == "infographic":
            cmd = ["nlm", "create", "infographic", nb_id, "--orientation", "square", "--detail", "detailed", "--focus", prompt, "--language", "it", "-y"]
        else:
            print(json.dumps({"status": "error", "message": f"Invalid asset type: {asset_type}"}, indent=2))
            sys.exit(1)
            
        res = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode()
        print(json.dumps({"status": "success", "message": f"Triggered {asset_type} successfully.", "output": res.strip()}, indent=2))
    except Exception as e:
        print(json.dumps({"status": "error", "message": f"Failed to trigger generation: {e}"}, indent=2))
        sys.exit(1)

def get_artifacts_status(nb_id):
    """Directly queries internal API for compact, token-efficient JSON status representation."""
    try:
        client = get_client()
        artifacts = client._list_raw(nb_id)
    except Exception as e:
        return {"status": "error", "message": f"Could not list artifacts: {e}"}
        
    video_status = {"status": "none", "id": None, "updated_at": None}
    info_status = {"status": "none", "id": None, "updated_at": None}
    
    for a in artifacts:
        if isinstance(a, list) and len(a) > 4:
            if a[2] == 3:  # STUDIO_TYPE_VIDEO
                if video_status["status"] == "none":
                    status_str = "completed" if a[4] == 3 else "generating" if a[4] == 2 else "failed" if a[4] == 4 else f"unknown_{a[4]}"
                    video_status = {
                        "id": a[0],
                        "status": status_str,
                        "updated_at": a[6] if len(a) > 6 else None
                    }
            elif a[2] == 7:  # STUDIO_TYPE_INFOGRAPHIC
                if info_status["status"] == "none":
                    status_str = "completed" if a[4] == 3 else "generating" if a[4] == 2 else "failed" if a[4] == 4 else f"unknown_{a[4]}"
                    info_status = {
                        "id": a[0],
                        "status": status_str,
                        "updated_at": a[6] if len(a) > 6 else None
                    }
                
    return {
        "status": "success",
        "notebook_id": nb_id,
        "video": video_status,
        "infographic": info_status
    }

def cmd_status(args):
    """Outputs compact JSON status representing all generated artifacts."""
    res = get_artifacts_status(args.notebook_id)
    print(json.dumps(res, indent=2))

def download_fallback(nb_id, asset_type, output_path):
    """HTTP raw requests stream fallback utilizing session cookies to download media safely."""
    print(f"[*] Launching direct cookie authentication stream download for {asset_type}...")
    try:
        client = get_client()
        manager = get_auth_manager()
        cookies = manager.get_cookies()
        
        cookies_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
        
        url = None
        if asset_type == "video":
            url = get_video_url(client, nb_id)
        elif asset_type == "infographic":
            url = get_infographic_url(client, nb_id)
            
        if not url:
            print(f"[!] Fallback error: Could not extract direct media URL from metadata.")
            return False
            
        print(f"[*] Raw Download URL: {url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Referer": "https://notebooklm.google.com/",
            "Cookie": cookies_str,
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site"
        }
        
        session = requests.Session()
        for name, value in cookies.items():
            session.cookies.set(name, value, domain=".google.com")
            session.cookies.set(name, value, domain=".googleusercontent.com")
            
        with session.get(url, headers=headers, stream=True, allow_redirects=True) as r:
            r.raise_for_status()
            ct = r.headers.get("Content-Type", "")
            print(f"[*] Content-Type: {ct}")
            if "text/html" in ct or "login.yahoo.com" in r.url or "accounts.google.com" in r.url or "InteractiveLogin" in r.url:
                print("[!] Fallback warning: Response contains HTML redirect/login page instead of media payload.")
                print("[*] Automatically attempting self-healing cookie refresh from active Chrome window...")
                if refresh_cookies_from_chrome():
                    print("[*] Retrying fallback download with fresh cookies...")
                    manager = get_auth_manager()
                    cookies = manager.get_cookies()
                    cookies_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
                    
                    # Refresh target URL in case client needed fresh cookies to authenticate list_raw
                    client = get_client()
                    if asset_type == "video":
                        url = get_video_url(client, nb_id)
                    elif asset_type == "infographic":
                        url = get_infographic_url(client, nb_id)
                    
                    if not url:
                        print(f"[!] Fallback retry error: Could not extract direct media URL from metadata.")
                        return False
                        
                    headers["Cookie"] = cookies_str
                    session = requests.Session()
                    for name, value in cookies.items():
                        session.cookies.set(name, value, domain=".google.com")
                        session.cookies.set(name, value, domain=".googleusercontent.com")
                        
                    with session.get(url, headers=headers, stream=True, allow_redirects=True) as r_retry:
                        r_retry.raise_for_status()
                        ct_retry = r_retry.headers.get("Content-Type", "")
                        print(f"[*] Retry Content-Type: {ct_retry}")
                        if "text/html" in ct_retry or "accounts.google.com" in r_retry.url or "InteractiveLogin" in r_retry.url:
                            print("[!] Fallback retry aborted: Response still contains HTML redirect page.")
                            return False
                        r = r_retry
                else:
                    return False
            
            total = int(r.headers.get('content-length', 0))
            downloaded = 0
            with open(output_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total > 0:
                            percent = int(100 * downloaded / total)
                            sys.stdout.write(f"\r[*] Progress: {percent}% ({downloaded}/{total} bytes)")
                            sys.stdout.flush()
            print(f"\n[+] Fallback download successfully saved: {output_path}")
            return True
    except Exception as e:
        print(f"\n[!] Fallback download encountered an error: {e}")
        return False

def cmd_download(args):
    """Downloads the requested asset with direct fallback if standard downloader fails or gets hijacked."""
    nb_id = args.notebook_id
    asset_type = args.type
    output_path = args.output
    
    # Try standard CLI download first
    print(f"[*] Attempting standard download for {asset_type}...")
    try:
        subprocess.run(["nlm", "download", asset_type, nb_id, "--output", output_path], capture_output=True)
        if is_valid_binary_file(output_path):
            print(f"[+] Downloaded successfully using standard downloader: {output_path}")
            print(json.dumps({"status": "success", "method": "standard", "path": output_path}, indent=2))
            return
    except Exception as e:
        print(f"[!] Standard download command crashed: {e}")
        
    # Standard failed, execute fallback
    print("[!] Standard download file is missing or corrupted. Initiating secure direct fallback...")
    if os.path.exists(output_path):
        try:
            os.remove(output_path)
        except Exception:
            pass
            
    success = download_fallback(nb_id, asset_type, output_path)
    if success and is_valid_binary_file(output_path):
        print(json.dumps({"status": "success", "method": "fallback", "path": output_path}, indent=2))
    else:
        print(json.dumps({"status": "error", "message": "Failed to retrieve correct file via both standard and fallback downloaders."}, indent=2))
        sys.exit(1)

def cmd_sync(args):
    """Orchestrates the entire sync pipeline from ingest, generate, poll, to download."""
    print("="*60)
    print(f"[*] STARTING END-TO-END PIPELINE: {args.title}")
    print("="*60)
    
    # Drive sync
    drive_dir = get_drive_papers_dir()
    if not drive_dir:
        print("[!] Sync Error: Drive folder not detected.")
        sys.exit(1)
        
    sanitized = re.sub(r'[:*?"<>|/]', ' ', args.title).strip()
    drive_dest = os.path.join(drive_dir, f"{sanitized}.pdf")
    
    print(f"[*] 1/6 Copying to Google Drive: {drive_dest}")
    try:
        shutil.copy2(args.pdf_path, drive_dest)
    except Exception as e:
        print(f"[!] Copy failed: {e}")
        sys.exit(1)
        
    drive_id = get_google_drive_id(drive_dest)
    if not drive_id:
        sys.exit(1)
        
    # Create notebook
    print(f"[*] 2/6 Creating notebook: {args.title}")
    try:
        res = subprocess.check_output(["nlm", "create", "notebook", args.title], stderr=subprocess.STDOUT).decode()
        match = re.search(r"ID:\s*([a-fA-F0-9-]+)", res)
        nb_id = match.group(1).strip() if match else res.split("ID:")[1].strip().split()[0].replace(')', '')
        print(f"[+] Notebook created: {nb_id}")
    except Exception as e:
        print(f"[!] Failed to create notebook: {e}")
        sys.exit(1)
        
    # Add source
    print(f"[*] 3/6 Adding Drive source...")
    try:
        cmd = ["nlm", "source", "add", nb_id, "--drive", drive_id, "--type", "pdf", "--title", args.title, "--wait"]
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        print("[+] Source ingested successfully.")
    except Exception as e:
        print(f"[!] Failed to add source: {e}")
        sys.exit(1)
        
    # Trigger video
    print(f"[*] 4/6 Triggering Video Overview...")
    v_prompt = args.video_prompt or f"Per favore parla in Italiano. Sei un host di podcast coinvolgente che spiega paper di economia. Sii energico ma accurato. Usa possibilmente le figure del paper senza ritoccarle, esprimi i numeri a parole, usa un linguaggio non roboante. **MANDATORIO: Il TITOLO in sovrimpressione nel video DEVE essere ESATTAMENTE: '{args.title}'. Non riassumere o alterare il titolo.**"
    try:
        subprocess.check_output(["nlm", "create", "video", nb_id, "--focus", v_prompt, "--language", "it", "-y"])
        print("[+] Video Overview triggered.")
    except Exception as e:
        print(f"[!] Video triggering failed: {e}")
        sys.exit(1)
        
    # Trigger infographic
    print(f"[*] 5/6 Triggering Infographic...")
    i_prompt = args.info_prompt or "Lingua: Italiano. Stile: Moderna, pulita. Tono: Divulgativo. FOCUS: 1. IL DILEMMA 2. LA SCOPERTA 3. LA MORALE. REGOLE: Niente muri di testo. Emoji e grafici. Formato: Quadrata."
    info_triggered = False
    try:
        subprocess.check_output(["nlm", "create", "infographic", nb_id, "--orientation", "square", "--detail", "detailed", "--focus", i_prompt, "--language", "it", "-y"])
        print("[+] Infographic triggered.")
        info_triggered = True
    except Exception as e:
        print(f"[!] Warning: Infographic triggering failed: {e}")
        
    # Polling
    print(f"[*] 6/6 Polling asset generation status...")
    video_ready = False
    info_ready = False
    
    out_dir = args.output_dir or os.path.expanduser("~/Downloads")
    clean_t = args.clean_title or args.title.replace(" ", "_")
    
    video_out = os.path.join(out_dir, f"{clean_t}_raw.mp4")
    info_out = os.path.join(out_dir, f"{clean_t}_infografica.png")
    
    for _ in range(60):
        status = get_artifacts_status(nb_id)
        if status.get("status") == "success":
            v_st = status["video"]["status"]
            i_st = status["infographic"]["status"]
            print(f"[*] Polling... Video: {v_st} | Infographic: {i_st}")
            
            if v_st == "completed":
                video_ready = True
            if i_st == "completed":
                info_ready = True
                
        if video_ready and (not info_triggered or info_ready):
            break
        time.sleep(30)
        
    # Downloads
    if video_ready:
        print(f"[*] Video completed. Initiating secure download to: {video_out}")
        mock_args = argparse.Namespace(notebook_id=nb_id, type="video", output=video_out)
        try:
            cmd_download(mock_args)
        except SystemExit:
            pass
    else:
        print("[!] Video generation timed out.")
        
    if info_triggered and info_ready:
        print(f"[*] Infographic completed. Initiating secure download to: {info_out}")
        mock_args = argparse.Namespace(notebook_id=nb_id, type="infographic", output=info_out)
        try:
            cmd_download(mock_args)
        except SystemExit:
            pass
            
    print("="*60)
    print("[*] END-TO-END PIPELINE COMPLETED")
    print("="*60)

# =========================================================================
# Main Argument Parsing Engine
# =========================================================================

def main():
    parser = argparse.ArgumentParser(description="Notebook Press Agent-Native CLI Wrapper for NotebookLM Operations")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Subcommand to execute")
    
    # Auth subcommand
    p_auth = subparsers.add_parser("auth", help="Verify active authenticated session and credentials")
    p_auth.add_argument("--refresh", action="store_true", help="Automatically pull fresh cookies from active Chrome window")
    
    # Upload subcommand
    p_upload = subparsers.add_parser("upload", help="Copy PDF to Google Drive, wait for sync, and register as source")
    p_upload.add_argument("pdf_path", help="Local absolute path to PDF paper")
    p_upload.add_argument("--title", required=True, help="Title for the source and notebook watermark")
    p_upload.add_argument("--notebook-id", help="Optional notebook ID to upload to (creates new if omitted)")
    
    # Generate subcommand
    p_gen = subparsers.add_parser("generate", help="Trigger generation of studio artifacts (video/infographic)")
    p_gen.add_argument("notebook_id", help="Notebook UUID")
    p_gen.add_argument("--type", required=True, choices=["video", "infographic"], help="Asset type to generate")
    p_gen.add_argument("--focus", required=True, help="Focus prompt for generation details")
    
    # Status subcommand
    p_stat = subparsers.add_parser("status", help="Get token-efficient compact status JSON of notebook artifacts")
    p_stat.add_argument("notebook_id", help="Notebook UUID")
    
    # Download subcommand
    p_dl = subparsers.add_parser("download", help="Download asset with direct cookie HTTP stream fallback")
    p_dl.add_argument("notebook_id", help="Notebook UUID")
    p_dl.add_argument("type", choices=["video", "infographic"], help="Asset type to download")
    p_dl.add_argument("--output", required=True, help="Output destination file path")
    
    # Sync subcommand
    p_sync = subparsers.add_parser("sync", help="Orchestrate the entire sync and generation pipeline end-to-end")
    p_sync.add_argument("pdf_path", help="Local absolute path to PDF paper")
    p_sync.add_argument("--title", required=True, help="Watermark and target title")
    p_sync.add_argument("--video-prompt", help="Custom video prompt")
    p_sync.add_argument("--info-prompt", help="Custom infographic prompt")
    p_sync.add_argument("--output-dir", help="Target output directory (defaults to ~/Downloads)")
    p_sync.add_argument("--clean-title", help="Clean alphanumeric title for naming output files")
    
    args = parser.parse_args()
    
    # Route command
    if args.command == "auth":
        cmd_auth(args)
    elif args.command == "upload":
        cmd_upload(args)
    elif args.command == "generate":
        cmd_generate(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "download":
        cmd_download(args)
    elif args.command == "sync":
        cmd_sync(args)

if __name__ == "__main__":
    main()
