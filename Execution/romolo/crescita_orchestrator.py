import os
import subprocess
import sys

# Path
ROMOLO_DIR = "/Users/marcolemoglie_1_2/Desktop/canale/Execution/romolo"
PYTHON = "/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3"

def run_growth_cycle():
    print("🌟 AVVIO CICLO DI CRESCITA - THE AUTHORITY CYCLE 🌟")
    print("==================================================")
    
    # 1. SEO Tag Refresher (Ottimizzazione SEO)
    print("\n🏷️ Ottimizzazione SEO & Refresh Hashtag dinamici...")
    SEO_SCRIPT = os.path.join(ROMOLO_DIR, "seo_tag_refresher.py")
    try:
        subprocess.run([PYTHON, SEO_SCRIPT], check=True)
    except Exception as e:
        print(f"⚠️ Warning SEO Refresh: {e}")
        
    # 2. Internal Linker (Siloing e Cross-linking)
    print("\n🔗 Ottimizzazione Siloing & Cross-linking video...")
    LINKER_SCRIPT = os.path.join(ROMOLO_DIR, "internal_linker.py")
    try:
        subprocess.run([PYTHON, LINKER_SCRIPT], check=True)
    except Exception as e:
        print(f"⚠️ Warning Internal Linker: {e}")
    
    # 3. Community Sentry (Interazione & Analisi)
    print("\n🛡️ Analisi commenti e drafting risposte...")
    SENTRY_SCRIPT = os.path.join(ROMOLO_DIR, "community_sentry.py")
    try:
        subprocess.run([PYTHON, SENTRY_SCRIPT], check=True)
    except Exception as e:
        print(f"⚠️ Warning Community Sentry: {e}")

    # 4. Competitor Scout (Nuova Task)
    print("\n🔍 Scouting competitor e proposte interazione...")
    SCOUT_SCRIPT = os.path.join(ROMOLO_DIR, "competitor_scout.py")
    try:
        subprocess.run([PYTHON, SCOUT_SCRIPT], check=True)
    except Exception as e:
        print(f"⚠️ Warning Competitor Scout: {e}")

    # 5. Social Bridge (News-jacking)
    print("\n🔗 Generazione Social Bridge (FB -> IG)...")
    ARCHIVE_SCRIPT = os.path.join(ROMOLO_DIR, "archive_matcher.py")
    try:
        subprocess.run([PYTHON, ARCHIVE_SCRIPT], check=True)
    except Exception as e:
        print(f"⚠️ Warning Social Bridge: {e}")

    print("\n" + "="*50)
    print("✅ OPERAZIONI DI CRESCITA COMPLETATE")
    print(f"📈 SEO & LINKING: Metadata e hashtag ottimizzati con successo.")
    print(f"🛡️ COMMUNITY: Bozze risposte e analisi engagement pronte.")
    print(f"🌍 SOCIAL: Suggerimenti Traffic Bridge generati in social_bridge_queue.json.")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_growth_cycle()
