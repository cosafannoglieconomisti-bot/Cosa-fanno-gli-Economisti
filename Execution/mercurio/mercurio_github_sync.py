import subprocess
import os
import sys
import shutil
import re
import tempfile
from datetime import datetime

# Configurazione Cartelle e File da includere nel backup
ALLOWED_PATHS = [
    ".agents",
    "Directives",
    "Execution",
    "Agents",
    "GEMINI.md",
    "Cleaned",
    ".gitignore",
    "README.md"
]

# Pattern Regex per l'offuscamento (estendibile)
SENSITIVE_PATTERNS = [
    (r"(Token[:\s=]+)[`'\" ]?([A-Za-z0-9_\-\.]{20,})[`'\" ]?", r"\1[REDACTED]"),
    (r"(Profile ID[:\s=]+)[`'\" ]?([a-f0-9]{10,})[`'\" ]?", r"\1[REDACTED]"),
    (r"(App Secret[:\s=]+)[`'\" ]?([A-Za-z0-9]{20,})[`'\" ]?", r"\1[REDACTED]"),
    (r"(API Key[:\s=]+)[`'\" ]?([A-Za-z0-9_\-]{20,})[`'\" ]?", r"\1[REDACTED]"),
    (r"(Password[:\s=]+)[`'\" ]?([^\n'\" `]{6,})[`'\" ]?", r"\1[REDACTED]"),
]

def run_command(command, cwd=None):
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, cwd=cwd)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Errore comando ({' '.join(command)}): {e.stderr}")
        return None

def sanitize_file(file_path):
    """Applica l'offuscamento dei dati sensibili al contenuto del file."""
    if not file_path.endswith(('.md', '.py', '.txt', '.json')):
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        for pattern, replacement in SENSITIVE_PATTERNS:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            # print(f"Sanificato: {os.path.basename(file_path)}")
    except Exception as e:
        print(f"Errore durante la sanificazione di {file_path}: {e}")

def sync_to_github(custom_msg=None):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Inizio backup sicuro su GitHub...")
    
    # 0. Directory radice e URL Remote
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    os.chdir(root_dir)
    
    remote_url = run_command(['git', 'remote', 'get-url', 'origin'])
    if not remote_url:
        print("Errore: Impossibile recuperare l'URL del remote 'origin'.")
        return

    # 1. Creazione Staging Area Temporanea
    staging_dir = os.path.join(root_dir, "Temp", "mercurio", "backup_staging")
    if os.path.exists(staging_dir):
        shutil.rmtree(staging_dir)
    os.makedirs(staging_dir)

    # 2. Copia Selettiva
    print("Preparazione file per il backup...")
    for path in ALLOWED_PATHS:
        src = os.path.join(root_dir, path)
        dst = os.path.join(staging_dir, path)
        if os.path.exists(src):
            if os.path.isdir(src):
                # Escludi file .mp4 da tutte le cartelle per mantenere il repo scarico
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns('*.mp4'))
            else:
                shutil.copy2(src, dst)

    # 3. Offuscamento (Sanificazione)
    print("Offuscamento dati sensibili in corso...")
    for root, dirs, files in os.walk(staging_dir):
        # Escludi cartelle git se presenti (anche se non dovrebbero esserci qui)
        if '.git' in dirs:
            dirs.remove('.git')
        for file in files:
            sanitize_file(os.path.join(root, file))

    # 4. Inizializzazione Git in Staging e Push
    os.chdir(staging_dir)
    run_command(['git', 'init'])
    # Forza il branch a chiamarsi 'main' per coerenza
    run_command(['git', 'checkout', '-b', 'main'])
    run_command(['git', 'remote', 'add', 'origin', remote_url])
    run_command(['git', 'add', '-A'])
    
    # Check if there are changes
    commit_msg = custom_msg or f"Backup sicuro: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    run_command(['git', 'commit', '-m', commit_msg])
    
    print("Invio modifiche offuscate a GitHub...")
    # Usiamo force push perché lo staging non ha la cronologia del remote
    # Garantiamo il push da local main a remote main
    push_result = run_command(['git', 'push', '-f', 'origin', 'main'])

    if push_result is not None:
        print("Sincronizzazione completata! Cronologia GitHub resettata e dati offuscati.")
    else:
        print("Errore durante il push. Verifica le autorizzazioni del token Git o l'URL del remote.")

    # Cleanup staging
    shutil.rmtree(staging_dir)

if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else None
    sync_to_github(msg)
