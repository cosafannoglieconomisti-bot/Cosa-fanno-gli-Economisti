#!/usr/bin/env python3
import sys
import os
import json
import asyncio
import httpx
import websocket
from pathlib import Path

# Force standard non-buffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# Main async function to test the new notebooklm-py SDK with Italian Cinematic Video
async def main():
    print("[*] Starting Cinematic Video scratch test...")
    
    # 1. Connect to active Chrome via CDP on port 9222 to get cookies
    print("[*] Extracting cookies from active Chrome window via CDP on port 9222...")
    try:
        r = httpx.get("http://127.0.0.1:9222/json", timeout=5)
        pages = r.json()
    except Exception as e:
        print(f"[!] Chrome debug window not found on port 9222: {e}")
        print("[!] Please make sure Chrome is running with remote debugging enabled:")
        print("    /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222")
        return

    target = None
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
        print("[!] No active Chrome targets found with a WebSocket debugging URL.")
        return
        
    ws_url = target['webSocketDebuggerUrl']
    print(f"[+] Targeted page: '{target.get('title')}' ({target.get('url')})")
    
    try:
        ws = websocket.create_connection(ws_url, timeout=10, suppress_origin=True)
        
        # Enable network domain
        ws.send(json.dumps({"id": 1, "method": "Network.enable", "params": {}}))
        ws.recv()
        
        # Fetch all cookies
        ws.send(json.dumps({"id": 2, "method": "Network.getAllCookies", "params": {}}))
        cookies_result = None
        while True:
            msg = ws.recv()
            response = json.loads(msg)
            if response.get("id") == 2:
                cookies_result = response.get("result", {})
                break
                
        ws.close()
    except Exception as e:
        print(f"[!] Failed to communicate with Chrome over WebSocket: {e}")
        return
        
    cookies_list = cookies_result.get("cookies", []) if cookies_result else []
    if not cookies_list:
        print("[!] No cookies returned from active Chrome session.")
        return
        
    print(f"[+] Successfully extracted {len(cookies_list)} cookies from Chrome.")
    
    # 2. Package cookies into Playwright storage_state format and set env var
    storage_state = {
        "cookies": cookies_list,
        "origins": []
    }
    
    os.environ["NOTEBOOKLM_AUTH_JSON"] = json.dumps(storage_state)
    print("[+] Formatted cookies set in NOTEBOOKLM_AUTH_JSON environment variable.")
    
    # Import NotebookLMClient inside so environment variable is picked up
    from notebooklm import NotebookLMClient
    
    print("[*] Initializing NotebookLMClient from storage state...")
    async with await NotebookLMClient.from_storage() as client:
        print(f"[+] Client initialized! Connected: {client.is_connected}")
        
        # 3. Create a temporary test notebook
        notebook_title = "Test Cinematic Python IT"
        print(f"[*] Creating temporary notebook: '{notebook_title}'...")
        notebook = await client.notebooks.create(notebook_title)
        print(f"[+] Notebook created successfully! ID: {notebook.id}")
        
        try:
            # 4. Upload a small text source
            source_title = "Documento di Prova"
            source_text = (
                "L'economia comportamentale studia come i fattori cognitivi, sociali, emotivi "
                "e culturali influenzano le decisioni economiche delle persone. A differenza "
                "dell'economia classica, che presuppone che gli agenti siano perfettamente "
                "razionali ed egoisti, l'economia comportamentale mostra che le persone deviano "
                "sistematicamente dalla razionalità perfetta a causa di euristiche, bias cognitivi "
                "e preferenze sociali come l'equità e la reciprocità."
            )
            print(f"[*] Uploading text source: '{source_title}'...")
            source = await client.sources.add_text(notebook.id, source_title, source_text)
            print(f"[+] Source added! ID: {source.id}")
            
            # Wait for source to be processed (usually instantaneous for text)
            print("[*] Waiting for source to be ready...")
            await client.sources.wait_until_ready(notebook.id, source.id)
            print("[+] Source is ready.")
            
            # 5. Generate Italian Cinematic Video Overview
            print("[*] Triggering generation of Italian Cinematic Video Overview...")
            instructions = (
                "Genera il video interamente in lingua italiana. Entrambi i conduttori "
                "devono dialogare in un italiano fluido, naturale e grammaticalmente corretto, "
                "senza alcuna parola o cadenza in inglese."
            )
            
            # Generate the video
            status = await client.artifacts.generate_cinematic_video(
                notebook_id=notebook.id,
                language="it",
                instructions=instructions
            )
            task_id = status.task_id
            print(f"[+] Generation triggered! Task ID: {task_id}")
            
            # Polling status
            print("[*] Polling generation status (this might take several minutes)...")
            await client.artifacts.wait_for_completion(notebook.id, task_id, poll_interval=10, timeout=600)
            print("[+] Cinematic video generation completed successfully!")
            
            # 6. Download the generated video
            output_dir = Path("/Users/marcolemoglie_1_2/Desktop/canale/scratch")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / "test_cinematic.mp4"
            
            print(f"[*] Downloading generated video to {output_path}...")
            # We can pass artifact_id or download_video will download the latest video
            downloaded_file = await client.artifacts.download_video(notebook.id, str(output_path))
            print(f"[+] Video successfully downloaded to: {downloaded_file}")
            
            if os.path.exists(downloaded_file) and os.path.getsize(downloaded_file) > 100 * 1024:
                print(f"[+] Verification: File exists and is valid ({os.path.getsize(downloaded_file)} bytes).")
            else:
                print("[!] Verification failed: File is missing or too small.")
                
        except Exception as e:
            print(f"[!] Error occurred during test workflow: {e}")
            raise e
        finally:
            # 7. Clean up by deleting the temporary notebook
            print(f"[*] Cleaning up: deleting temporary notebook {notebook.id}...")
            await client.notebooks.delete(notebook.id)
            print("[+] Temporary notebook deleted.")

if __name__ == "__main__":
    asyncio.run(main())
