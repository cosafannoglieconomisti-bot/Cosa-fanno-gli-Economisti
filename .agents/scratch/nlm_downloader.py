#!/usr/bin/env python3
"""
Download deterministico usando direttamente il modulo notebooklm_tools.
Estrae l'URL fresco via _list_raw() poi scarica con _download_url().
"""
import asyncio
import sys
import json
import os

PROFILE_DIR = "/Users/marcolemoglie_1_2/.notebooklm-mcp-cli/profiles/default"
COOKIES_PATH = f"{PROFILE_DIR}/cookies.json"
META_PATH = f"{PROFILE_DIR}/metadata.json"

NOTEBOOK_ID = "a03e52a7-2725-4e35-9fe0-7e6f32ff7145"
INFOGRAPHIC_ID = "6124c3c8-ae20-42d2-899b-771a3c7ca88e"
VIDEO_ID = "87c04d5c-a14b-4ac8-8715-95c7be26cb97"
OUTPUT_INFOGRAPHIC = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/enea/infografica_raw.png"
OUTPUT_VIDEO = "/Users/marcolemoglie_1_2/Desktop/canale/Temp/enea/Poveri_in_Pensione_raw.mp4"


def load_credentials():
    with open(COOKIES_PATH) as f:
        cookies_list = json.load(f)
    with open(META_PATH) as f:
        meta = json.load(f)
    return cookies_list, meta["csrf_token"], meta["session_id"], meta.get("email")


def inspect_artifacts(client):
    """Ispeziona la struttura raw degli artifact per debug."""
    artifacts = client._list_raw(NOTEBOOK_ID)
    print(f"[*] Trovati {len(artifacts)} artifact")
    
    for i, a in enumerate(artifacts):
        if isinstance(a, list) and len(a) > 2:
            art_id = a[0] if len(a) > 0 else "?"
            art_type = a[2] if len(a) > 2 else "?"
            art_status = a[4] if len(a) > 4 else "?"
            print(f"  [{i}] ID={art_id} type={art_type} status={art_status} len={len(a)}")
            
            if art_id in (INFOGRAPHIC_ID, VIDEO_ID):
                print(f"       -> TARGET ARTIFACT")
                # Salva struttura completa per debug
                with open(f"/tmp/artifact_{art_id[:8]}.json", "w") as f:
                    json.dump(a, f, indent=2, default=str)
                print(f"       -> Struttura salvata in /tmp/artifact_{art_id[:8]}.json")
    
    return artifacts


async def download_infographic(client):
    print(f"\n[*] Download infografica...")
    path = await client.download_infographic(
        notebook_id=NOTEBOOK_ID,
        output_path=OUTPUT_INFOGRAPHIC,
        artifact_id=INFOGRAPHIC_ID,
    )
    size = os.path.getsize(path)
    print(f"[+] Infografica: {path} ({size:,} bytes)")
    return path


async def download_video(client):
    print(f"\n[*] Download video...")
    path = await client.download_video(
        notebook_id=NOTEBOOK_ID,
        output_path=OUTPUT_VIDEO,
        artifact_id=VIDEO_ID,
    )
    size = os.path.getsize(path)
    print(f"[+] Video: {path} ({size:,} bytes)")
    return path


async def main():
    from notebooklm_tools.core.client import NotebookLMClient

    cookies_list, csrf_token, session_id, email = load_credentials()
    print(f"[*] Account: {email}")

    client = NotebookLMClient(
        cookies=cookies_list,
        csrf_token=csrf_token,
        session_id=session_id,
    )

    action = sys.argv[1] if len(sys.argv) > 1 else "inspect"

    if action == "inspect":
        inspect_artifacts(client)
    
    elif action == "infographic":
        try:
            await download_infographic(client)
        except Exception as e:
            print(f"[!] Errore: {e}")
            print("[*] Ispezione artifact per debug...")
            inspect_artifacts(client)
    
    elif action == "video":
        try:
            await download_video(client)
        except Exception as e:
            print(f"[!] Errore: {e}")
            inspect_artifacts(client)
    
    elif action == "both":
        for fn in (download_infographic, download_video):
            try:
                await fn(client)
            except Exception as e:
                print(f"[!] Errore: {e}")


if __name__ == "__main__":
    asyncio.run(main())
