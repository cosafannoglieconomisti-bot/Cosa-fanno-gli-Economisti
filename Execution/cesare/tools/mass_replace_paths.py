import os

# Order Matters: specific files first, then directories
replacements = [
    ('[Romolo] Gestione Canale YouTube/token_youtube.pickle', 'Execution/credentials/token_youtube.pickle'),
    ('[Augusto] Gestione File e Persistenza/client_secrets.json', 'Execution/credentials/client_secrets.json'),
    ('[Romolo] Gestione Canale YouTube/videos_list_updated.json', 'Temp/romolo/videos_list_updated.json'),
    ('[Romolo] Gestione Canale YouTube/videos_list.json', 'Temp/romolo/videos_list_updated.json'),
    ('[Romolo] Gestione Canale YouTube', 'Execution/romolo'),
    ('[Marcello] Gestione Social Media', 'Execution/marcello'),
    ('[Augusto] Gestione File e Persistenza', 'Execution/augusto'),
    ('[Enea] Produzione Video', 'Execution/enea'),
    ('[Ulisse] News e Ricerca', 'Execution/ulisse'),
    ('[Mercurio] Comunicazione', 'Execution/mercurio'),
    ('[Cesare] Telegram Hub', 'Execution/cesare'),
]

def fix_files(dry_run=False):
    search_dir = 'Execution'
    count = 0
    for root, dirs, files in os.walk(search_dir):
        for file in files:
            if file.endswith('.py') or file.endswith('.sh'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    updated_content = content
                    modified = False
                    for old, new in replacements:
                        if old in updated_content:
                            print(f"File: {filepath} -> Sostituzione '{old}' con '{new}'")
                            updated_content = updated_content.replace(old, new)
                            modified = True
                            
                    if modified and not dry_run:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(updated_content)
                        count += 1
                        print(f"Salvato: {filepath}")
                except Exception as e:
                     print(f"Errore nell'elaborazione di {filepath}: {e}")
    print(f"Total files modified: {count}")

if __name__ == '__main__':
    import sys
    dry = '--dry-run' in sys.argv
    if dry:
        print("=== MODALITA' DRY-RUN ===")
    fix_files(dry_run=dry)
