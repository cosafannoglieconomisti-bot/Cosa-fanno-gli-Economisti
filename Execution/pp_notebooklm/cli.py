import argparse
import sys
import os
from .client import NotebookLMClient
from .db import init_db, upsert_notebook, upsert_source, upsert_asset, get_notebooks, get_assets
from .models import Notebook, Source, Asset

def cmd_sync(args):
    print("[*] Sincronizzazione con NotebookLM...")
    client = NotebookLMClient()
    notebooks = client.list_notebooks()
    
    for nb in notebooks:
        print(f"  [+] Notebook: {nb.title}")
        print(f"      ID: {nb.id}")
        upsert_notebook(nb)
        
        # Sync sources for each notebook
        try:
            sources = client.get_notebook_sources(nb.id)
            for source in sources:
                print(f"      - Source: [{source.type}] {source.title}")
                upsert_source(source)
        except Exception as e:
            print(f"      [!] Errore sincronizzazione sources: {e}")
            
        # Poll assets for each notebook to update mirror
        try:
            assets = client.poll_studio(nb.id)
            for asset in assets:
                print(f"      - Asset: [{asset.type}] {asset.status}")
                upsert_asset(asset)
        except Exception as e:
            print(f"      [!] Errore sincronizzazione assets: {e}")
            
    print("[+] Sincronizzazione completata.")

def cmd_status(args):
    notebooks = get_notebooks()
    if args.id:
        notebooks = [n for n in notebooks if n.id == args.id or args.id in n.title]
        
    for nb in notebooks:
        print(f"\nNotebook: {nb.title}")
        print(f"ID: {nb.id}")
        print(f"Sources: {nb.source_count}")
        
        assets = get_assets(nb.id)
        if assets:
            print("Assets:")
            for a in assets:
                print(f"  - [{a.type}] {a.status} (URL: {a.url or 'N/A'})")
        else:
            print("Assets: Nessuno")

def cmd_download(args):
    client = NotebookLMClient()
    assets = get_assets(args.notebook_id)
    
    # Filter by type
    target_assets = [a for a in assets if a.type == args.type and a.status == "completed"]
    if not target_assets:
        print(f"[!] Errore: Nessun asset di tipo '{args.type}' trovato o completato per questo notebook.")
        return

    asset = target_assets[0] # Take the first/latest
    ext = "mp4" if asset.type == "video" else "png"
    filename = f"{args.notebook_id}_{asset.type}.{ext}"
    output_path = os.path.join(args.output, filename)
    
    print(f"[*] Scaricamento {asset.type} da: {asset.url}")
    client.download_file(asset.url, output_path)
    print(f"[+] Salvato in: {output_path}")

def cmd_generate(args):
    client = NotebookLMClient()
    
    # First fetch source IDs live
    print(f"[*] Recupero sorgenti per il notebook {args.notebook_id}...")
    try:
        sources = client.get_notebook_sources(args.notebook_id)
    except Exception as e:
        print(f"[!] Errore nel recupero delle sorgenti: {e}")
        return
        
    if not sources:
        print("[!] Errore: Nessuna sorgente trovata in questo notebook. Impossibile generare asset.")
        return
        
    source_ids = [s.id for s in sources]
    print(f"[+] Trovate {len(source_ids)} sorgenti: {source_ids}")
    
    if args.type == "video":
        print(f"[*] Avvio generazione Video Overview (lingua: {args.language})...")
        focus = args.focus_prompt
        if not focus:
            title_val = args.title or "La famiglia ostacola l'economia?"
            focus = f"MANDATORIO: Il TITOLO in sovrimpressione deve essere: {title_val}"
        try:
            res = client.create_video_overview(
                notebook_id=args.notebook_id,
                source_ids=source_ids,
                language=args.language,
                focus_prompt=focus
            )
            print(f"[+] Richiesta inviata con successo!")
            print(f"    Risultato: {res}")
        except Exception as e:
            print(f"[!] Errore durante la richiesta di generazione video: {e}")
            
    elif args.type == "infographic":
        print(f"[*] Avvio generazione Infografica (lingua: {args.language})...")
        try:
            res = client.create_infographic(
                notebook_id=args.notebook_id,
                source_ids=source_ids,
                orientation_code=3,  # square
                detail_level_code=3,  # detailed
                language=args.language,
                focus_prompt=args.focus_prompt or ""
            )
            print(f"[+] Richiesta inviata con successo!")
            print(f"    Risultato: {res}")
        except Exception as e:
            print(f"[!] Errore durante la richiesta di generazione infografica: {e}")

def main():
    parser = argparse.ArgumentParser(description="pp-notebooklm: Agent-Native NotebookLM CLI")
    subparsers = parser.add_subparsers(dest="command", help="Comandi disponibili")

    # Sync
    subparsers.add_parser("sync", help="Sincronizza mirror locale con NotebookLM")

    # Status
    parser_status = subparsers.add_parser("status", help="Mostra lo stato locale")
    parser_status.add_argument("--id", help="Filtra per ID o Titolo")

    # Download
    parser_dl = subparsers.add_parser("download", help="Scarica asset completati")
    parser_dl.add_argument("notebook_id", help="ID del notebook")
    parser_dl.add_argument("--type", choices=["video", "infographic", "audio"], default="video", help="Tipo di asset")
    parser_dl.add_argument("--output", default=".", help="Directory di destinazione")

    # Generate
    parser_gen = subparsers.add_parser("generate", help="Genera nuovi asset (video, infografica, etc.)")
    parser_gen.add_argument("notebook_id", help="ID del notebook")
    parser_gen.add_argument("--type", choices=["video", "infographic"], required=True, help="Tipo di asset da generare")
    parser_gen.add_argument("--title", help="Titolo in sovrimpressione per il video (opzionale)")
    parser_gen.add_argument("--focus-prompt", help="Prompt personalizzato di focus (opzionale)")
    parser_gen.add_argument("--language", default="it", help="Lingua per l'asset (default: it)")

    args = parser.parse_args()
    
    init_db()
    
    if args.command == "sync":
        cmd_sync(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "download":
        cmd_download(args)
    elif args.command == "generate":
        cmd_generate(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
