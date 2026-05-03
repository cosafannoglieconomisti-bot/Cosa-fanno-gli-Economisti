import subprocess
import os
import sys
import shutil
import re
from datetime import datetime

# Configurazione Cartelle CORE
CORE_PATHS = [
    ".agents",
    "Directives",
    "Execution",
    "Agents",
    "GEMINI.md",
    ".gitignore",
    "README.md"
]

# Progetti SPECIFICI da includere in Cleaned/
TARGETED_PROJECTS = [
    "Perche_l_Africa_non_si_fida",
    "Razzismo_in_campo_colpa_dei_tifosi",
    "Figli_o_Pensione_La_Scelta",
    "La_Chiesa_frena_l_integrazione",
    "Le_città_perdute_dell_età_del_bronzo_qje_2019",
    "Perche_scacciare_la_Mafia_paga",
    "Quando_la_Chiesa_fermo_l_Italia",
    "Regolarizzare_gli_immigrati_riduce_il_crimine",
    "Socialismo_la_causa_del_Fascismo",
    "Tagliare_gli_aiuti_ai_diciottenni_AER_2016"
]

# Pattern Regex per l'offuscamento
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
    except Exception as e:
        print(f"Errore durante la sanificazione di {file_path}: {e}")

def sync_targeted():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Inizio TARGETED SYNC su GitHub...")
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    os.chdir(root_dir)
    
    remote_url = run_command(['git', 'remote', 'get-url', 'origin'])
    if not remote_url:
        print("Errore remote url.")
        return

    staging_dir = os.path.join(root_dir, "Temp", "mercurio", "targeted_staging")
    if os.path.exists(staging_dir):
        shutil.rmtree(staging_dir)
    os.makedirs(staging_dir)

    # 1. Copia Core
    print("Copia cartelle core...")
    for path in CORE_PATHS:
        src = os.path.join(root_dir, path)
        dst = os.path.join(staging_dir, path)
        if os.path.exists(src):
            if os.path.isdir(src):
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns('*.mp4'))
            else:
                shutil.copy2(src, dst)

    # 2. Copia Mirata Cleaned
    print("Copia progetti mirati in Cleaned/...")
    cleaned_dst_base = os.path.join(staging_dir, "Cleaned")
    os.makedirs(cleaned_dst_base, exist_ok=True)
    
    # Copia video_tracking.json (fondamentale)
    tracking_src = os.path.join(root_dir, "Cleaned", "video_tracking.json")
    if os.path.exists(tracking_src):
        shutil.copy2(tracking_src, cleaned_dst_base)

    for project in TARGETED_PROJECTS:
        src = os.path.join(root_dir, "Cleaned", project)
        dst = os.path.join(cleaned_dst_base, project)
        if os.path.exists(src):
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns('*.mp4'))
            print(f"  + {project}")

    # 3. Sanificazione
    print("Offuscamento in corso...")
    for root, dirs, files in os.walk(staging_dir):
        for file in files:
            sanitize_file(os.path.join(root, file))

    # 4. Push
    os.chdir(staging_dir)
    run_command(['git', 'init'])
    run_command(['git', 'checkout', '-b', 'main'])
    run_command(['git', 'remote', 'add', 'origin', remote_url])
    run_command(['git', 'add', '-A'])
    run_command(['git', 'commit', '-m', f"Targeted Backup: {datetime.now().strftime('%H:%M:%S')}"])
    
    print("Invio a GitHub (Targeted)...")
    push_result = run_command(['git', 'push', '-f', 'origin', 'main'])

    if push_result is not None:
        print("✅ TARGETED SYNC COMPLETATO!")
    else:
        print("❌ Errore durante il push.")

if __name__ == "__main__":
    sync_targeted()
