import os
import glob
import shutil

def cleanup():
    # 1. Mafia Inc
    mafia_dir = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/Mafia_Inc_restat_2021"
    mafia_v5 = "/Users/marcolemoglie_1_2/.gemini/antigravity/brain/5bc8acda-cbd4-4b83-920f-32154964403a/mafia_inc_inpainted_1774101976444.png"
    
    # Rimuovi vecchie
    for f in glob.glob(os.path.join(mafia_dir, "thumbnail*")):
        try: os.remove(f)
        except: pass
    
    # Copia nuova
    shutil.copy(mafia_v5, os.path.join(mafia_dir, "thumbnail.png"))
    print("Pulizia Mafia completata")
    
    # 2. Archeologia
    arch_dir = "/Users/marcolemoglie_1_2/Desktop/canale/Cleaned/Le_città_perdute_dell_età_del_bronzo_qje_2019"
    arch_v5 = "/Users/marcolemoglie_1_2/.gemini/antigravity/brain/5bc8acda-cbd4-4b83-920f-32154964403a/archeologia_inpainted_1774101993115.png"
    
    # Rimuovi vecchie
    for f in glob.glob(os.path.join(arch_dir, "thumbnail*")):
        try: os.remove(f)
        except: pass
        
    # Copia nuova
    shutil.copy(arch_v5, os.path.join(arch_dir, "thumbnail.png"))
    print("Pulizia Archeologia completata")

if __name__ == "__main__":
    cleanup()
