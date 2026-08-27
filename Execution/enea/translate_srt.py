import os
import re
import sys

from deep_translator import GoogleTranslator


def translate_text_line(translator, line):
    if not line.strip():
        return line
    if line.strip().isdigit():
        return line
    if "-->" in line:
        return line
    return translator.translate(line)


def translate_srt(input_path, output_path, target_lang):
    if not os.path.exists(input_path):
        print(f"❌ Error: File not found {input_path}")
        return False

    print(f"🌍 Translating {input_path} to {target_lang}...")
    translator = GoogleTranslator(source="it", target=target_lang)
    with open(input_path, "r", encoding="utf-8") as handle:
        lines = handle.read().splitlines()

    translated_lines = []
    for line in lines:
        try:
            translated_lines.append(translate_text_line(translator, line))
        except Exception:
            translated_lines.append(line)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(translated_lines) + "\n")
    print(f"🎉 SUCCESS: {target_lang} SRT saved to {output_path}")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python translate_srt.py <input.srt> <output.srt> <target_language>")
        sys.exit(1)

    inp, out, lang = sys.argv[1], sys.argv[2], sys.argv[3]
    success = translate_srt(inp, out, lang)
    if not success:
        sys.exit(1)
