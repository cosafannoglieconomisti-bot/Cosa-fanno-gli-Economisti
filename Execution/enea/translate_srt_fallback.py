import sys
import os
from deep_translator import GoogleTranslator

def translate_srt(input_file, output_file, target_lang):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        translator = GoogleTranslator(source='it', target=target_lang)
        translated_lines = []
        
        batch = []
        batch_indices = []
        
        def process_batch():
            if not batch: return
            text_to_translate = "\n".join(batch)
            translated_text = translator.translate(text_to_translate)
            translated_chunks = translated_text.split("\n")
            
            # Reconstruct
            for idx, chunk in zip(batch_indices, translated_chunks):
                translated_lines[idx] = chunk + "\n"
            
            batch.clear()
            batch_indices.clear()

        # Initialize translated_lines with original lines
        translated_lines = lines[:]
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            # If it's a number, a timestamp, or empty, leave it as is. Otherwise translate
            if stripped and not stripped.isdigit() and '-->' not in stripped:
                batch.append(stripped)
                batch_indices.append(i)
                if len(batch) >= 20: # Process in small batches
                    process_batch()
        
        process_batch() # remaining
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(translated_lines)
            
        print(f"✅ Translated to {target_lang}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python t.py input output lang")
        sys.exit(1)
    translate_srt(sys.argv[1], sys.argv[2], sys.argv[3])
