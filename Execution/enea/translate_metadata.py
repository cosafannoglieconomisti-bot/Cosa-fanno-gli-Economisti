import os
import re
import sys

from deep_translator import GoogleTranslator


LANGUAGE_NAMES = {
    "en": "english",
    "es": "spanish",
    "fr": "french",
    "de": "german",
}


def translate_preserving_markdown(text, target_lang):
    translator = GoogleTranslator(source="it", target=target_lang)
    output = []

    def safe_translate(value):
        translated = translator.translate(value)
        return translated if translated is not None else value

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            output.append("")
            continue
        if stripped.startswith("#") or stripped.startswith("http"):
            output.append(line)
            continue
        if re.match(r"^\d{2}:\d{2}", stripped):
            parts = line.split("|", 1)
            if len(parts) == 2:
                left, right = parts
                translated = safe_translate(right.strip())
                output.append(f"{left.strip()} | {translated}")
                continue
        if "https://doi.org/" in line or "youtube.com/" in line or "youtu.be/" in line:
            output.append(line)
            continue
        translated = safe_translate(stripped)
        output.append(translated)
    return "\n".join(output)


def translate_metadata(input_path, output_dir, target_langs):
    with open(input_path, "r", encoding="utf-8") as handle:
        it_content = handle.read()

    overall_success = True
    for lang in target_langs:
        print(f"🌍 Traduzione metadati in {lang}...")
        try:
            translated = translate_preserving_markdown(it_content, lang)
            translated = translated.replace(
                "# Metadati Video -", f"# Video Metadata -"
            )
            if lang != "en":
                translated = re.sub(
                    r"^# Video Metadata - (.+)$",
                    lambda match: f"# Video Metadata - {match.group(1)} ({lang.upper()})",
                    translated,
                    count=1,
                    flags=re.MULTILINE,
                )
            else:
                translated = re.sub(
                    r"^# Video Metadata - (.+)$",
                    lambda match: f"# Video Metadata - {match.group(1)} (EN)",
                    translated,
                    count=1,
                    flags=re.MULTILINE,
                )
            lang_dir = os.path.join(output_dir, lang)
            os.makedirs(lang_dir, exist_ok=True)
            out_path = os.path.join(lang_dir, f"metadata_{lang}.md")
            with open(out_path, "w", encoding="utf-8") as handle:
                handle.write(translated)
            print(f"✅ Metadati {lang} salvati in {out_path}")
        except Exception as exc:
            overall_success = False
            print(f"❌ Errore traduzione {lang}: {exc}")
    return overall_success


if __name__ == "__main__":
    input_file = sys.argv[1]
    out_root = sys.argv[2]
    langs = ["en", "es", "fr", "de"]
    success = translate_metadata(input_file, out_root, langs)
    if not success:
        sys.exit(1)
