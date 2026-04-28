import os

maps = [
    {
        'file': 'Directives/romolo/gestione_canale.md',
        'sections': [
            ('## SOP: Generazione Indice (Whisper)', '## SOP: Upload Video e Metadati', '- `Execution/romolo/generate_index_whisper.py`'),
            ('## SOP: Upload Video e Metadati', '---', '- `Execution/romolo/youtube_uploader.py`'),
        ]
    },
    {
        'file': 'Directives/enea/produzione_video.md',
        'sections': [
            ('## SOP: Video Cleaning (FFmpeg)', '---', '- `Execution/enea/video_cleaner.py`'),
        ]
    },
    {
        'file': 'Directives/mercurio/regole_agente.md',
        'sections': [
            ('## SOP: Report Giornaliero Gmail', '---', '- `Execution/mercurio/mercurio_gmail_manager.py`'),
        ]
    },
    {
        'file': 'Directives/mercurio/backup.md',
        'sections': [
            ('## SOP: Backup su GitHub', '---', '- `Execution/mercurio/mercurio_github_sync.py`'),
        ]
    },
    {
        'file': 'Directives/cesare/regole_agente.md',
        'sections': [
            ('## SOP: Hub Notifiche e Approvazioni', '---', '- `Execution/cesare/telegram_bot.py`'),
        ]
    },
    {
        'file': 'Directives/ulisse/news_rules.md',
        'sections': [
            ('## 3. Procedura di Matching Accademico', '## 4. Archivio e Formattazione', '- `Execution/ulisse/verify_paper.py` (Verifica News/Paper)'),
        ]
    }
]

def update_file(filepath, sections):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 1. Remove general list at the bottom if present
    if "## 📋 File Python Utilizzati" in content:
        # Avoid removing if it's already inside a section we care about?
        # Let's remove the LAST occurrence or anything after it
        content = content.split("## 📋 File Python Utilizzati")[0].strip() + "\n"
        print(f"Removed general list from {filepath}")
        
    # 2. Process sections
    for current_hdr, next_hdr_anchor, list_text in sections:
        if current_hdr in content:
            parts = content.split(current_hdr)
            before_current = parts[0]
            after_current = parts[1]
            
            # Find boundary (next_hdr_anchor or end)
            if next_hdr_anchor in after_current:
                # Split at next anchor
                sub_parts = after_current.split(next_hdr_anchor)
                section_body = sub_parts[0].strip()
                after_section = next_hdr_anchor + sub_parts[1]
                
                # Append list to section body
                if "## 📋 File Python Utilizzati" not in section_body:
                    section_body += "\n\n## 📋 File Python Utilizzati\n" + list_text
                    
                # Reassemble
                content = before_current + current_hdr + "\n\n" + section_body + "\n\n" + after_section
                print(f"Updated section '{current_hdr}' in {filepath}")
            else:
                 # It's the last section in the file (or anchor not found)
                 section_body = after_current.strip()
                 if "## 📋 File Python Utilizzati" not in section_body:
                     section_body += "\n\n## 📋 File Python Utilizzati\n" + list_text
                 content = before_current + current_hdr + "\n\n" + section_body + "\n"
                 print(f"Updated last section '{current_hdr}' in {filepath}")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    for item in maps:
        update_file(item['file'], item['sections'])
