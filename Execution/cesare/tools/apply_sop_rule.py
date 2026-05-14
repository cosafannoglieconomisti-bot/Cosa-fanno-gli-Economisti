import os

rule_text = """4.  **Tracciabilità File nelle SOP**: Ogni SOP deve riportare alla fine l'elenco dei file Python utilizzati nell'ultima esecuzione riuscita, nell'ordine esatto di esecuzione. Questa lista deve essere aggiornata automaticamente ogni volta che i file vengono modificati, aggiornati, eliminati o aggiunti per garantire la massima deterministicità."""

lists = {
    'enea': """
## 📋 File Python Utilizzati
- `Execution/enea/batch_text_extractor.py` (Analisi e Metadati)
- `Execution/enea/video_cleaner.py` (Video Cleaning)
- `Execution/enea/generate_index_whisper.py` (Generazione Indice)
- `Execution/enea/youtube_uploader.py` (Upload YouTube)
""",
    'romolo': """
## 📋 File Python Utilizzati
- `Execution/romolo/romolo_manage_channel.py` (Analytics e Monitoraggio)
""",
    'marcello': """
## 📋 File Python Utilizzati
- `Execution/marcello/facebook_sync_today_local.py` (Post Facebook/Social)
""",
    'ulisse': """
## 📋 File Python Utilizzati
- `Execution/ulisse/verify_paper.py` (Verifica News/Paper)
""",
    'mercurio': """
## 📋 File Python Utilizzati
- `Execution/mercurio/mercurio_gmail_manager.py` (Gmail Report)
- `Execution/mercurio/mercurio_github_sync.py` (Backup GitHub)
""",
    'cesare': """
## 📋 File Python Utilizzati
- `Execution/cesare/telegram_bot.py` (Hub Notifiche / Bot)
"""
}

def update_gemini():
    filepath = 'Gemini.md'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    lines = content.split('\n')
    
    # 1. Add General Rule
    if "4.  **Tracciabilità File nelle SOP**" not in content:
        for i, line in enumerate(lines):
            if "3.  Miglioramento Continuo" in line:
                # Add after this item
                lines.insert(i + 1, rule_text)
                print("Added general rule to Gemini.md")
                break
                
    # 2. Add lists to agent parts (Best effort insert before the next part)
    updated_content = '\n'.join(lines)
    
    # Map section boundaries
    sections = [
        ('## PARTE 4: Enea', '## SOP: Enea — Template Descrizione Video', 'enea'),
        ('## SOP: Enea — Template Descrizione Video', '## PARTE 5: Romolo', 'enea'),
        ('## PARTE 5: Romolo', '## PARTE 6: Marcello', 'romolo'),
        ('## PARTE 6: Marcello', '## PARTE 7: Ulisse', 'marcello'),
        ('## PARTE 7: Ulisse', '## PARTE 8: Mercurio', 'ulisse'),
        ('## PARTE 8: Mercurio', '## PARTE 9: Cesare', 'mercurio'),
        ('## PARTE 9: Cesare', '## PARTE 10: Augusto', 'cesare')
    ]
    
    for start_hdr, end_hdr, agent_key in sections:
        if start_hdr in updated_content and end_hdr in updated_content:
            part_content = updated_content.split(start_hdr)[1].split(end_hdr)[0]
            if "## 📋 File Python Utilizzati" not in part_content:
                # Insert list before end_hdr
                list_to_append = lists[agent_key].strip() + "\n\n"
                # Locate position
                pos = updated_content.find(end_hdr)
                # Backup a bit for formatting if needed, but simple insert before header is fine
                updated_content = updated_content[:pos] + list_to_append + updated_content[pos:]
                print(f"Added list for {agent_key} to Gemini.md")
                
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(updated_content)

def update_directives():
    directives_dir = 'Directives'
    for agent, list_content in lists.items():
        agent_dir = os.path.join(directives_dir, agent)
        if os.path.exists(agent_dir):
            for file in os.listdir(agent_dir):
                if file.endswith('.md'):
                    filepath = os.path.join(agent_dir, file)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        fc = f.read()
                    if "## 📋 File Python Utilizzati" not in fc:
                        fc = fc.strip() + "\n\n" + list_content.strip() + "\n"
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(fc)
                        print(f"Updated {filepath}")

if __name__ == '__main__':
    update_gemini()
    update_directives()
