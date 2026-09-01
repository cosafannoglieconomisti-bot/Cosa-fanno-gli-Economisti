#!/usr/bin/env python3
import argparse
import glob
import hashlib
import json
import os
import re
import signal
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]
HOME = Path.home()

from dotenv import load_dotenv

sys.path.insert(0, str(REPO_ROOT / "Execution"))
from canale_paths import expand_local_paths
from enea import pipeline_store

try:
    from google import genai
except Exception:
    genai = None

ROOT = REPO_ROOT
PYTHON = ROOT / ".venv/bin/python3"
DOWNLOADS = HOME / "Downloads"
PAPERS_DIR = ROOT / "Papers/Da fare"
CLEANED_DIR = ROOT / "Cleaned"
TEMP_DIR = ROOT / "Temp"
ACTIVE_PIPE = ROOT / "Temp/enea/active_pipeline.json"
TRACKING_PATH = ROOT / "Cleaned/video_tracking.json"
COMMAND_MAP = ROOT / "Execution/cesare/command_map.json"
BRIDGE_LOG = ROOT / "Temp/cesare/telegram_bridge.log"

load_dotenv(ROOT / ".env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
CLIENT = genai.Client(api_key=GEMINI_API_KEY) if genai and GEMINI_API_KEY else None


def tmp_cover_path():
    cover_dir = TEMP_DIR / "enea"
    cover_dir.mkdir(parents=True, exist_ok=True)
    name = "active"
    if ACTIVE_PIPE.exists():
        try:
            with open(ACTIVE_PIPE, "r", encoding="utf-8") as handle:
                pipe = json.load(handle)
            name = pipe.get("clean_title") or "active"
        except Exception:
            pass
    return cover_dir / f"{name}_cover.png"


class WorkflowError(RuntimeError):
    pass


def log(message):
    print(f"[workflow] {message}")


def ensure_parent(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def run_cmd(cmd, cwd=ROOT, check=True, env=None):
    effective_env = os.environ.copy()
    effective_env.setdefault("PYTHONUNBUFFERED", "1")
    effective_env.setdefault("TERM", "dumb")
    effective_env.setdefault("DEBIAN_FRONTEND", "noninteractive")
    if env:
        effective_env.update(env)
    log(f"run: {' '.join(str(part) for part in cmd)}")
    result = subprocess.run(
        [str(part) for part in cmd],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
        env=effective_env,
    )
    if check and result.returncode != 0:
        raise WorkflowError(result.stderr or result.stdout or f"Command failed: {cmd}")
    return result


def load_command_map():
    with open(COMMAND_MAP, "r", encoding="utf-8") as handle:
        raw = handle.read()
    return json.loads(expand_local_paths(raw))


def append_bridge_log(message, source="Workflow"):
    ensure_parent(BRIDGE_LOG)
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(BRIDGE_LOG, "a", encoding="utf-8") as handle:
        handle.write(f"[{timestamp}] {source}: {message}\n")


def prompt_choice(options, label, preselected_index=None):
    if not options:
        raise WorkflowError(f"Nessuna opzione disponibile per {label}.")
    if preselected_index is not None:
        if preselected_index < 1 or preselected_index > len(options):
            raise WorkflowError(f"Indice {preselected_index} fuori range per {label}.")
        return options[preselected_index - 1]
    print(f"\n{label}:")
    for idx, option in enumerate(options, start=1):
        print(f"  {idx}. {option}")
    while True:
        choice = input("> ").strip()
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(options):
                return options[idx - 1]
        print("Indice non valido.")


def discover_pdfs(recursive=True):
    if recursive:
        pattern = str(PAPERS_DIR / "**/*.pdf")
        pdfs = sorted(glob.glob(pattern, recursive=True))
    else:
        pdfs = sorted(str(path) for path in PAPERS_DIR.glob("*.pdf"))
    return [Path(path) for path in pdfs]


def extract_title_from_pdf_layout(pdf_path):
    try:
        import fitz

        doc = fitz.open(pdf_path)
        page = doc[0]
        page_dict = page.get_text("dict")
        candidates = []

        for block in page_dict.get("blocks", []):
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                spans = line.get("spans", [])
                if not spans:
                    continue
                text = " ".join(span.get("text", "").strip() for span in spans).strip()
                if not text:
                    continue
                if len(text) < 8:
                    continue
                if re.fullmatch(r"[\d\W_]+", text):
                    continue
                if text.lower().startswith(("abstract", "introduction", "jel", "keywords")):
                    continue
                avg_size = sum(span.get("size", 0) for span in spans) / len(spans)
                y0 = min(span.get("bbox", [0, 0, 0, 0])[1] for span in spans)
                candidates.append((avg_size, y0, text))

        if not candidates:
            return None

        max_size = max(size for size, _, _ in candidates)
        top_candidates = [
            (size, y0, text)
            for size, y0, text in candidates
            if size >= max_size - 0.5 and y0 < 350
        ]
        top_candidates.sort(key=lambda item: item[1])
        if not top_candidates:
            return None

        title_lines = []
        first_y = top_candidates[0][1]
        for _, y0, text in top_candidates:
            if abs(y0 - first_y) <= 80:
                title_lines.append(text)

        title = " ".join(title_lines).strip()
        title = re.sub(r"\s+", " ", title)
        if title.endswith(":"):
            text_preview = extract_text(pdf_path, 1)
            preview_lines = [re.sub(r"\s+", " ", line).strip() for line in text_preview.splitlines() if line.strip()]
            if len(preview_lines) > 1 and not any(token in preview_lines[1] for token in ["University", "Institute", "@"]):
                title = f"{title} {preview_lines[1].rstrip('*†‡∗')}".strip()
        return title or None
    except Exception:
        return None


def clean_title_candidate(text):
    text = text.replace("\xad", "")
    text = text.rstrip("*†‡∗")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def is_bad_title_candidate(text):
    lower = text.lower()
    if len(text) < 8 or len(text.split()) > 18:
        return True
    if text.endswith(".") and len(text.split()) > 7:
        return True
    if re.fullmatch(r"[\d\W_]+", text):
        return True
    blocked = [
        "http://",
        "https://",
        "doi=",
        "doi.org",
        "copyright",
        "permissions",
        "published by",
        "all rights reserved",
        "volume ",
        "pages ",
        "journal of economic perspectives",
        "american economic review",
        "american economic journal",
        "the economic journal",
        "quarterly journal of economics",
        "forthcoming in",
        "advance access",
        "supplementary materials",
        "corresponding author",
    ]
    if any(token in lower for token in blocked):
        return True
    if lower.startswith(("by ", "abstract", "introduction", "jel", "keywords", "for supplementary")):
        return True
    if any(token in text for token in ["@", "©", "C⃝"]):
        return True
    return False


def is_likely_author_line(text):
    lower = text.lower()
    if any(token in lower for token in ["university", "nber", "cepr", "department", "school", "email", "@"]):
        return True
    words = text.replace(",", " ").split()
    if 2 <= len(words) <= 4 and all(word[:1].isupper() for word in words if word[:1].isalpha()):
        title_tokens = {"States", "Government", "Fertility", "Resources", "Identity", "Identities", "Segregation", "Equity"}
        return not any(word in title_tokens for word in words)
    return False


def extract_title_from_text_content(pdf_text):
    raw_lines = [clean_title_candidate(line) for line in pdf_text.splitlines()]
    lines = [line for line in raw_lines if line]
    candidates = []

    for idx, line in enumerate(lines[:45]):
        if is_bad_title_candidate(line):
            continue
        parts = [line]
        if idx + 1 < len(lines):
            next_line = lines[idx + 1]
            if not is_bad_title_candidate(next_line) and not next_line.lower().startswith("by ") and not is_likely_author_line(next_line):
                parts.append(next_line)

        candidate_options = [(line, False)]
        if len(parts) > 1:
            candidate_options.append((" ".join(parts), True))

        for candidate, is_combined in candidate_options:
            candidate = clean_title_candidate(candidate)
            if is_bad_title_candidate(candidate):
                continue

            words = candidate.split()
            score = 0
            if 2 <= len(words) <= 12:
                score += 8
            if any(char.islower() for char in candidate) and any(char.isupper() for char in candidate):
                score += 4
            if candidate.isupper():
                score += 5
            if idx + 1 < len(lines) and lines[idx + 1].lower().startswith("by "):
                score += 14
            if idx + 2 < len(lines) and lines[idx + 2].lower().startswith("by "):
                score += 10
            if idx + 1 < len(lines) and lines[idx + 1].startswith("■"):
                score += 12
            if idx > 0 and lines[idx - 1].startswith("■"):
                score += 8
            if is_combined and idx + 2 < len(lines) and lines[idx + 2].startswith("■"):
                score += 12
            if idx <= 6:
                score += 3
            if is_combined:
                score += 12
            if any(token in candidate.lower() for token in ["effect", "capital", "fertility", "segregation", "equity", "resources", "states", "government", "industrialization"]):
                score += 4
            if candidate.endswith(":"):
                score -= 5

            candidates.append((score, idx, candidate))

    if not candidates:
        return None

    candidates.sort(key=lambda item: (-item[0], item[1], -len(item[2])))
    return candidates[0][2]


def get_bundle_titles(pdf_paths):
    titles = {}
    sys.path.append(str(ROOT / "Execution/enea"))
    try:
        from paper_downloader import get_academic_title as get_academic_title_impl
    except Exception:
        get_academic_title_impl = None

    for path in pdf_paths:
        extracted_title = None
        try:
            text = extract_text(path, 3)
            if text:
                extracted_title = extract_title_from_text_content(text)
            if text and not extracted_title and get_academic_title_impl:
                extracted_title = get_academic_title_impl(text)
        except Exception:
            extracted_title = None

        titles[path.name] = extracted_title or extract_title_from_pdf_layout(path) or path.stem
    return titles


def extract_text(pdf_path, max_pages=3):
    sys.path.append(str(ROOT / "Execution/enea"))
    from batch_text_extractor import extract_text as extract_text_impl

    return extract_text_impl(str(pdf_path), max_pages)


def parse_metadata_from_text(pdf_text, fallback_title="Paper"):
    title = extract_title_from_text_content(pdf_text) or fallback_title
    preview_lines = [re.sub(r"\s+", " ", line).strip() for line in pdf_text.splitlines() if line.strip()]
    if title == fallback_title and preview_lines:
        candidate_lines = []
        for line in preview_lines[:4]:
            if any(token in line for token in ["University", "Institute", "Department", "@"]):
                break
            if line.lower().startswith(("abstract", "forthcoming", "jel", "keywords")):
                break
            candidate_lines.append(line.rstrip("*†‡∗"))
            if len(candidate_lines) >= 2:
                break
        if candidate_lines:
            title = re.sub(r"\s+", " ", " ".join(candidate_lines)).strip()

    authors = []
    # Many working papers list several authors on one marked line without a
    # "By" prefix. Detect that line before the permissive fallback below.
    for line in preview_lines[:20]:
        if not re.search(r"[*†‡∗]", line) or "," not in line:
            continue
        stripped = clean_title_candidate(line)
        if any(token in stripped.lower() for token in ["university", "institute", "college", "school", "department", "email"]):
            continue
        author_text = re.sub(r"[*†‡∗]+", "", stripped).strip()
        author_parts = [part.strip() for part in author_text.split(",") if part.strip()]
        if len(author_parts) >= 2 and all(2 <= len(part.split()) <= 5 for part in author_parts):
            authors = author_parts[:6]
            break

    if authors:
        author_lines_done = True
    else:
        author_lines_done = False

    for line in preview_lines[:20]:
        if author_lines_done:
            break
        stripped = clean_title_candidate(line)
        if not stripped:
            continue
        byline = re.match(r"^by\s+(.+)$", stripped, flags=re.IGNORECASE)
        if byline:
            author_text = re.sub(r"[*†‡∗]+$", "", byline.group(1)).strip()
            author_parts = re.split(r"\s+and\s+|,\s*", author_text, flags=re.IGNORECASE)
            authors = [part.strip() for part in author_parts if part.strip()]
            break
        lower = stripped.lower()
        if lower.startswith(("abstract", "forthcoming", "published", "journal", "keywords", "jel")):
            break
        if any(token in lower for token in ["university", "institute", "college", "school", "department", "nber", "cepr", "email", "http"]):
            continue
        name_part = stripped.split(",")[0].strip()
        name_part = re.sub(r"[*†‡∗]+$", "", name_part).strip()
        if 2 <= len(name_part.split()) <= 5 and any(char.islower() for char in name_part):
            authors.append(name_part)
        if len(authors) >= 4:
            break

    journal = ""
    journal_patterns = [
        r"The Journal of Politics",
        r"American Economic Review",
        r"Quarterly Journal of Economics",
        r"Journal of Political Economy",
        r"Econometrica",
        r"Review of Economic Studies",
        r"Review of Economics and Statistics",
    ]
    for pattern in journal_patterns:
        if re.search(pattern, pdf_text, re.IGNORECASE):
            journal = pattern
            break

    year = ""
    for pattern in [
        r"Published online .*?\b((?:19|20)\d{2})\b",
        r"The Journal of Politics.*?\b((?:19|20)\d{2})\b",
        r"American Economic Review.*?\b((?:19|20)\d{2})\b",
        r"Quarterly Journal of Economics.*?\b((?:19|20)\d{2})\b",
        r"Journal of Political Economy.*?\b((?:19|20)\d{2})\b",
    ]:
        match = re.search(pattern, pdf_text, re.IGNORECASE | re.DOTALL)
        if match:
            year = match.group(1)
            break
    if not year:
        years = re.findall(r"\b((?:19|20)\d{2})\b", pdf_text)
        if years:
            year = max(years)

    metadata = {
        "real_title": title,
        "authors": ", ".join(dict.fromkeys(authors)),
        "journal": journal,
        "year": year,
    }
    return apply_known_publication_metadata(metadata)


def apply_known_publication_metadata(metadata):
    title = metadata.get("real_title", "").lower()
    if "human capital and industrialization" in title and "age of enlightenment" in title:
        metadata.update(
            {
                "authors": "Mara P. Squicciarini, Nico Voigtländer",
                "journal": "The Quarterly Journal of Economics",
                "year": "2015",
                "doi": "10.1093/qje/qjv025",
                "doi_url": "https://doi.org/10.1093/qje/qjv025",
            }
        )
    return metadata


def fallback_titles_from_metadata(metadata, pdf_text=""):
    real_title = metadata.get("real_title", "")
    lower = f"{real_title}\n{pdf_text[:5000]}".lower()

    if "human capital" in lower and ("industrialization" in lower or "industrial revolution" in lower):
        return [
            "I cervelli accendono le fabbriche?",
            "L'Illuminismo ha acceso l'industria?",
            "Quando il sapere diventa industria",
            "La conoscenza che arricchisce",
            "Chi accese le fabbriche?",
        ]
    if "segregation" in lower and "quality of government" in lower:
        return [
            "La segregazione rovina lo Stato?",
            "Divisioni sociali, cattivo governo?",
            "Perché governare diventa difficile?",
            "La distanza crea corruzione?",
            "Societa divise, istituzioni deboli?",
        ]
    if "artificial states" in lower:
        return [
            "I confini contano davvero?",
            "Chi disegna uno Stato?",
            "Stati artificiali, sviluppo fragile?",
            "L'Africa divisa a tavolino?",
            "Confini sbagliati, stati fragili?",
        ]
    if "equity concerns" in lower or "narrowly framed" in lower:
        return [
            "Siamo giusti solo vicino?",
            "Quanto pesa l'equita?",
            "La giustizia ha confini?",
            "Pensiamo davvero agli altri?",
            "L'equita finisce presto?",
        ]
    if "low fertility" in lower or "continued low fertility" in lower:
        return [
            "Meno figli, meno benessere?",
            "La natalita ci impoverisce?",
            "Il crollo demografico pesa?",
            "Siamo troppo pochi?",
            "Chi paga la denatalita?",
        ]
    if "mineral resources" in lower and "ethnic identities" in lower:
        return [
            "Le risorse dividono?",
            "Quando i minerali creano identita?",
            "L'etnia segue la ricchezza?",
            "Le miniere cambiano politica?",
            "Chi accende l'identita?",
        ]
    if "rage against the machines" in lower or ("labor-saving technology" in lower and "unrest" in lower):
        return [
            "Le macchine scatenano rivolte?",
            "Quando la tecnologia fa rabbia?",
            "L'automazione crea disordini?",
            "Lavoratori contro le macchine?",
            "Il progresso accende proteste?",
        ]
    if "corruption" in lower and "populism" in lower:
        return [
            "La corruzione crea populisti?",
            "Lo scandalo ti cambia?",
            "La sfiducia dura decenni?",
            "Perché nasce il populismo?",
            "La corruzione non si scorda?",
        ]
    if "fertility" in lower:
        return [
            "Meno figli, meno benessere?",
            "La natalita ci impoverisce?",
            "Il crollo delle nascite pesa?",
            "Siamo troppo pochi?",
            "Chi paga la bassa fertilita?",
        ]
    if "ethnic" in lower or "segregation" in lower:
        return [
            "Le divisioni ci impoveriscono?",
            "Conta piu l'etnia?",
            "Perche gli Stati si spaccano?",
            "La segregazione rovina tutto?",
            "Quanto pesa l'identita?",
        ]
    if "nazi" in lower:
        return [
            "L'indottrinamento resta per sempre?",
            "Il nazismo ti cambia davvero?",
            "Quanto dura la propaganda?",
            "Si eredita l'odio?",
            "La propaganda non muore?",
        ]

    keywords = []
    keyword_patterns = [
        ("human capital", "capitale umano"),
        ("industrialization", "industria"),
        ("industrial revolution", "rivoluzione industriale"),
        ("fertility", "natalita"),
        ("segregation", "segregazione"),
        ("ethnic", "identita"),
        ("resources", "risorse"),
        ("government", "governo"),
        ("equity", "equita"),
        ("state", "Stato"),
        ("corruption", "corruzione"),
        ("populism", "populismo"),
    ]
    for source, italian in keyword_patterns:
        if source in lower and italian not in keywords:
            keywords.append(italian)

    if keywords:
        pivot = keywords[0]
        second = keywords[1] if len(keywords) > 1 else "crescita"
        return [
            f"{pivot.capitalize()} o {second}?",
            f"Quanto conta {pivot}?",
            f"{pivot.capitalize()} cambia tutto?",
            f"Perche' {pivot} pesa?",
            f"Il dato su {pivot}?",
        ]

    short_title = real_title[:60].strip() if real_title else "Questo paper cosa dice?"
    return [
        short_title if len(short_title.split()) <= 5 else "Che cosa cambia davvero?",
        "Qual e' il meccanismo?",
        "Il risultato regge?",
        "Dove nasce l'effetto?",
        "Perche' questo conta?",
    ]


def curated_titles_from_metadata(metadata, pdf_text=""):
    real_title = metadata.get("real_title", "")
    lower = f"{real_title}\n{pdf_text[:5000]}".lower()

    if "empowering adolescents to transform schools" in lower:
        return [
            "Quando gli studenti diventano insegnanti: meno violenza, piu opportunita",
            "Dare responsabilita ai ragazzi puo cambiare una scuola?",
            "La scuola cambia dal basso: il potere degli studenti piu influenti",
            "Piu status, meno comportamenti antisociali",
            "Educare i leader della classe per spezzare lo svantaggio",
        ]

    if "human capital" in lower and ("industrialization" in lower or "industrial revolution" in lower):
        return [
            "I cervelli accendono le fabbriche?",
            "L'Illuminismo ha acceso l'industria?",
            "Quando il sapere diventa industria",
            "Chi accese le fabbriche?",
            "Le menti che fecero l'industria",
        ]
    return []


def build_editorial_brief(metadata, pdf_text):
    real_title = metadata.get("real_title", "")
    lower = f"{real_title}\n{pdf_text[:5000]}".lower()

    if "human capital" in lower and ("industrialization" in lower or "industrial revolution" in lower):
        return (
            "Nel Settecento francese, le città con più abbonati all'Encyclopédie "
            "crescono di più dopo l'avvio dell'industrializzazione. Il punto del paper "
            "è che non basta l'alfabetizzazione media: conta la conoscenza tecnica e "
            "scientifica nelle élite locali, cioè il capitale umano di fascia alta."
        )
    return ""


def title_rejected_by_sop(title, metadata, pdf_text):
    lower_title = title.lower()
    context = f"{metadata.get('real_title', '')}\n{pdf_text[:5000]}".lower()

    if any(token in lower_title for token in ["alfabeti", "fece esplodere", "solo l'élite", "solo elite"]):
        return True
    if "human capital" in context and ("industrialization" in context or "industrial revolution" in context):
        if any(token in lower_title for token in ["enciclop", "scuola non basta", "basta leggere", "alfabet"]):
            return True
    return False


def generate_titles_with_llm(metadata, pdf_text):
    if not CLIENT:
        return [], True, "GEMINI_API_KEY mancante o client non disponibile"

    title = metadata.get("real_title", "")
    journal = metadata.get("journal", "")
    year = metadata.get("year", "")
    editorial_brief = build_editorial_brief(metadata, pdf_text)
    prompt = f"""
Sei l'editor del canale YouTube italiano "Cosa fanno gli economisti".

Devi proporre 5 titoli video per un paper accademico.

SOP obbligatorie:
- pubblico generale, non addetti ai lavori;
- tono divulgativo e accattivante;
- massimo 5 parole per titolo;
- stile domanda o hook clicky;
- centrati sull'aspetto economico/sociale principale del paper;
- no clickbait speculativo;
- non incollare parole a caso dal paper;
- non usare titoli nominali con due punti;
- non usare titoli vaghi come "La scuola non basta?", "Le idee fanno crescere?", "La scintilla della Rivoluzione Industriale".
- il titolo deve sintetizzare il claim del paper, non solo citare il metodo o il proxy empirico.

Titolo accademico:
{title}

Rivista/anno:
{journal} {year}

Claim editoriale da usare come centro del titolo:
{editorial_brief or "Estrai dall'abstract la domanda di ricerca, il risultato principale e il meccanismo economico/sociale."}

Estratto del paper:
{pdf_text[:4500]}

Rispondi solo con un JSON array di 5 stringhe. Nessuna introduzione, nessuna spiegazione, nessun markdown.
"""

    def call_model(model):
        class Timeout(Exception):
            pass

        def handler(_signum, _frame):
            raise Timeout()

        previous_handler = signal.signal(signal.SIGALRM, handler)
        signal.alarm(25)
        try:
            return CLIENT.models.generate_content(model=model, contents=prompt)
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, previous_handler)

    best_titles = []
    last_error = None
    models = [GEMINI_MODEL]
    if GEMINI_MODEL != "gemini-flash-latest":
        models.append("gemini-flash-latest")
    for model in models:
        try:
            response = call_model(model)
            text = response.text if response and response.text else ""
        except Exception as exc:
            last_error = str(exc)
            log(f"Generazione titoli LLM fallita con {model}: {exc}")
            continue

        titles = []
        try:
            parsed = json.loads(text.strip().replace("```json", "").replace("```", ""))
            if isinstance(parsed, list):
                raw_items = [str(item) for item in parsed]
            else:
                raw_items = text.splitlines()
        except Exception:
            raw_items = text.splitlines()

        for raw_line in raw_items:
            cleaned = raw_line.strip()
            cleaned = re.sub(r"^\s*\d+[\).\-\s]+", "", cleaned).strip()
            cleaned = cleaned.strip("[],")
            cleaned = cleaned.strip('"“”')
            cleaned = cleaned.rstrip(".")
            if not cleaned:
                continue
            if any(token in cleaned.lower() for token in ["proposte", "titoli video", "ecco"]):
                continue
            if ":" in cleaned:
                continue
            if title_rejected_by_sop(cleaned, metadata, pdf_text):
                continue
            word_count = len(re.findall(r"\b[\wÀ-ÿ']+\b", cleaned))
            if word_count <= 5:
                titles.append(cleaned)
        if len(titles) >= 5:
            return titles[:5], False, None
        if len(titles) > len(best_titles):
            best_titles = titles

    if len(best_titles) >= 3:
        for fallback in fallback_titles_from_metadata(metadata, pdf_text):
            if fallback not in best_titles:
                best_titles.append(fallback)
            if len(best_titles) >= 5:
                return best_titles[:5], True, last_error
    return [], True, last_error


def generate_titles_and_metadata(pdf_path):
    text = extract_text(pdf_path, 3)
    if not text:
        raise WorkflowError(f"Impossibile leggere il PDF: {pdf_path}")
    text_title = extract_title_from_text_content(text)
    layout_title = extract_title_from_pdf_layout(pdf_path) or pdf_path.stem
    metadata = parse_metadata_from_text(text, fallback_title=text_title or layout_title)
    if text_title:
        metadata["real_title"] = text_title

    curated = curated_titles_from_metadata(metadata, text)
    if curated:
        return curated[:5], metadata, False, None

    llm_titles, llm_fallback, llm_error = generate_titles_with_llm(metadata, text)
    if llm_titles:
        return llm_titles[:5], metadata, llm_fallback, llm_error

    return fallback_titles_from_metadata(metadata, text)[:5], metadata, True, llm_error or "LLM non disponibile"


def slugify_title(title):
    return re.sub(r"[^a-zA-Z0-9]+", "_", title).strip("_")


def write_active_pipeline(data):
    pipeline_store.write_pipeline(data)


def read_active_pipeline():
    try:
        return pipeline_store.read_pipeline()
    except FileNotFoundError as exc:
        raise WorkflowError(str(exc)) from exc


def generate_cover(title):
    cover_path = tmp_cover_path()
    result = run_cmd(
        [PYTHON, ROOT / "Execution/enea/generate_cover.py", title, cover_path],
        check=False,
    )
    if result.returncode != 0 or not cover_path.exists():
        raise WorkflowError(
            "Generazione copertina fallita. Genera la cover in Codex/GPT e salvala in Temp/assets/override_cover.png."
        )
    if not cover_path.exists():
        raise WorkflowError("Copertina non generata.")
    return cover_path


def register_external_cover(source_path):
    source = Path(source_path)
    if not source.exists():
        raise WorkflowError(f"Copertina esterna non trovata: {source}")
    cover_path = tmp_cover_path()
    shutil.copy(source, cover_path)
    return cover_path


def choose_cover_action(auto_approve=False):
    cover_path = tmp_cover_path()
    if auto_approve:
        return "approve"
    print(f"\nCopertina generata: {cover_path}")
    print("Azioni: [a]pprove  [r]egenerate  [x] reject")
    while True:
        choice = input("> ").strip().lower()
        if choice in {"a", "approve"}:
            return "approve"
        if choice in {"r", "regenerate"}:
            return "regenerate"
        if choice in {"x", "reject"}:
            return "reject"
        print("Scelta non valida.")


def approve_cover_from_pipeline(move_pdf=True):
    pipeline = read_active_pipeline()
    title = pipeline.get("title")
    if not title:
        raise WorkflowError("Titolo mancante in active_pipeline.json.")

    clean_title = pipeline.get("clean_title") or slugify_title(title)
    target_dir = Path(pipeline.get("target_dir") or (CLEANED_DIR / clean_title))
    target_dir.mkdir(parents=True, exist_ok=True)

    pipeline["clean_title"] = clean_title
    pipeline["target_dir"] = str(target_dir)
    write_active_pipeline(pipeline)

    cover_path = tmp_cover_path()
    if not cover_path.exists():
        raise WorkflowError("Copertina temporanea non trovata.")
    shutil.copy(cover_path, target_dir / "copertina.png")

    metadata = pipeline.get("metadata", {})
    paper_name = pipeline.get("paper")
    paper_path = pipeline.get("paper_path")
    if move_pdf and paper_name and paper_path and Path(paper_path).exists():
        academic_title = metadata.get("real_title") or pipeline.get("academic_title") or title
        safe_academic_title = re.sub(r'[\\/:"*?<>|]+', "", academic_title).strip()
        destination = target_dir / f"{safe_academic_title}.pdf"
        shutil.move(paper_path, destination)
        pipeline["paper_path"] = str(destination)
        write_active_pipeline(pipeline)

    meta_file = target_dir / "video_metadata.md"
    source_url = metadata.get("doi") or metadata.get("doi_url") or ""
    if source_url and not str(source_url).startswith("http"):
        source_url = f"https://doi.org/{source_url}"
    with open(meta_file, "w", encoding="utf-8") as handle:
        handle.write(f"# Metadati Video - {title}\n\n")
        handle.write("## Descrizione YouTube\n\n")
        handle.write(
            f'Lo studio "{metadata.get("real_title", "N/A")}" di {metadata.get("authors", "N/A")}, '
            f'pubblicato su {metadata.get("journal", "N/A")} nel {metadata.get("year", "N/A")}, '
            "analizza [DESCRIZIONE DA COMPLETARE CON /PULIZIA].\n\n"
        )
        handle.write(f"⏰ Fonte: ►► {source_url}\n\n")
        handle.write("⏰ISCRIVITI al canale ►► https://www.youtube.com/@cosafannoglieconomisti26?sub_confirmation=1\n\n")
        handle.write("▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n")
        handle.write("⏰ INDICE CONTENUTI ⏰\n")
        handle.write("▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n")
        handle.write("00:00 | Intro\n\n")
        handle.write("#CosaFannoGliEconomisti #RicercaAccademica\n\n")
        handle.write("## Tag\n")
        handle.write("CosaFannoGliEconomisti, RicercaAccademica\n")

    append_bridge_log(f"Copertina approvata e asset preparati per {title}")
    log(f"Cartella pronta: {target_dir}")
    return target_dir


def run_simple_command(key, extra_args=None, report_path=None):
    commands = load_command_map()
    if key not in commands:
        raise WorkflowError(f"Workflow '{key}' non trovato nella command_map.")
    cmd = list(commands[key])
    if extra_args:
        cmd.extend(extra_args)
    if report_path and Path(report_path).exists():
        Path(report_path).unlink()
    result = run_cmd(cmd, check=False)
    if report_path and Path(report_path).exists():
        print(Path(report_path).read_text(encoding="utf-8"))
        return result.returncode
    print((result.stdout or result.stderr).strip())
    if result.returncode != 0:
        raise WorkflowError(result.stderr or result.stdout or f"Workflow '{key}' fallito.")
    return result.returncode


def choose_cleaned_folder(predicate):
    folders = []
    for folder in sorted(CLEANED_DIR.iterdir()):
        if folder.is_dir() and predicate(folder):
            folders.append(folder.name)
    return prompt_choice(folders, "Seleziona cartella")


def setup_pipeline_for_cleaned_folder(folder_name):
    folder_path = CLEANED_DIR / folder_name
    pdfs = sorted(folder_path.glob("*.pdf"))

    if ACTIVE_PIPE.exists():
        try:
            pipe = json.loads(ACTIVE_PIPE.read_text(encoding="utf-8"))
        except Exception:
            pipe = {}
        paper_path = pipe.get("paper_path")
        if (
            pipe.get("clean_title") == folder_name
            and paper_path
            and Path(paper_path).exists()
        ):
            pipe["target_dir"] = str(folder_path)
            write_active_pipeline(pipe)
            return pipe

    if not pdfs:
        raise WorkflowError(f"Nessun PDF in {folder_path} e nessun paper_path valido in active_pipeline.json")

    title = folder_name.replace("_", " ")
    metadata_files = [path for path in folder_path.glob("*.md") if "metadata" in path.name.lower()]
    if metadata_files:
        first_line = metadata_files[0].read_text(encoding="utf-8").splitlines()[0]
        if "Metadati Video - " in first_line:
            title = first_line.split("Metadati Video - ", 1)[1].strip()

    data = {
        "title": title,
        "clean_title": folder_name,
        "target_dir": str(folder_path),
        "paper": pdfs[0].name,
        "paper_path": str(pdfs[0]),
    }
    write_active_pipeline(data)
    return data


def workflow_backup(args):
    extra_args = [args.message] if args.message else None
    return run_simple_command("backup", extra_args=extra_args)


def workflow_download(_args):
    result = run_cmd([PYTHON, ROOT / "Execution/enea/paper_downloader.py"], check=False)
    print((result.stdout or result.stderr).strip())
    if result.returncode != 0:
        raise WorkflowError(result.stderr or result.stdout or "Download fallito.")
    return 0


def workflow_gmail(_args):
    report_path = ROOT / "Temp/mercurio/gmail_report.txt"
    return run_simple_command("gmail", report_path=report_path)


def workflow_report(_args):
    report_path = ROOT / f"Temp/romolo/analytics_reports/analytics_report_{time.strftime('%d_%m_%Y')}.txt"
    return run_simple_command("report", report_path=report_path)


def workflow_competitor(_args):
    report_path = ROOT / "Temp/romolo/competitor_engagement.md"
    return run_simple_command("competitor", report_path=report_path)


def workflow_articoli(args):
    if args.tags:
        cmd = [
            PYTHON,
            ROOT / "Execution/ulisse/verify_paper.py",
            "--tags",
            args.tags,
        ]
        if args.query:
            cmd.extend(["--query", args.query])
        cmd.extend(["--year", str(args.year)])
        result = run_cmd(cmd, check=False)
        print((result.stdout or result.stderr).strip())
        if result.returncode != 0:
            raise WorkflowError(result.stderr or result.stdout or "verify_paper fallito.")
        return 0

    raise WorkflowError("La modalita' automatica /articoli basata su LLM e' disattivata. Usa /articoli con --tags oppure verify_paper direttamente.")


def workflow_paper(args):
    pdf_paths = discover_pdfs(recursive=True)
    if not pdf_paths:
        raise WorkflowError("Nessun PDF trovato in Papers/Da fare.")

    titles_map = get_bundle_titles(pdf_paths)
    options = [f"{titles_map.get(path.name, path.stem)}" for path in pdf_paths]
    selected_label = prompt_choice(options, "Seleziona paper", preselected_index=args.paper_index)
    selected_idx = options.index(selected_label)
    selected_pdf = pdf_paths[selected_idx]

    titles, metadata, titles_fallback, titles_error = generate_titles_and_metadata(selected_pdf)
    print("\nMetadati rilevati:")
    print(json.dumps(metadata, indent=2, ensure_ascii=False))
    if titles_fallback:
        reason = titles_error or "modello AI non disponibile"
        print(f"\n⚠️ TITOLI DI RIPIEGO — l'AI non ha risposto (motivo: {reason}).")
        confirm = input("Continuo con titoli di ripiego? [s/N] ").strip().lower()
        if confirm not in {"s", "si", "y", "yes"}:
            raise WorkflowError("Selezione titolo annullata.")
    selected_title = prompt_choice(titles, "Seleziona titolo catchy", preselected_index=args.title_index)

    clean_title = slugify_title(selected_title)
    target_dir = CLEANED_DIR / clean_title
    pipeline = {
        "title": selected_title,
        "clean_title": clean_title,
        "target_dir": str(target_dir),
        "paper": selected_pdf.name,
        "paper_path": str(selected_pdf),
        "metadata": metadata,
        "academic_title": metadata.get("real_title", "Paper"),
        "status": "cover_pending_approval",
    }
    write_active_pipeline(pipeline)

    generate_cover(selected_title)
    if args.approve_cover:
        approve_cover_from_pipeline(move_pdf=True)
        return 0

    print(f"\nCopertina generata in: {tmp_cover_path()}")
    print("Approvala esplicitamente prima di archiviare il paper.")
    return 0


def workflow_copertina(args):
    if args.folder:
        setup_pipeline_for_cleaned_folder(args.folder)
    pipeline = read_active_pipeline()
    title = pipeline.get("title")
    if not title:
        raise WorkflowError("Titolo mancante in active_pipeline.json.")
    while True:
        generate_cover(title)
        action = choose_cover_action(auto_approve=args.approve_cover)
        if action == "approve":
            approve_cover_from_pipeline(move_pdf=True)
            break
        if action == "reject":
            log("Copertina rifiutata.")
            break
    return 0


def produzione_ready(folder):
    if any(folder.glob("*.mp4")):
        return False
    if any(folder.glob("*.pdf")):
        return True
    if ACTIVE_PIPE.exists():
        try:
            pipe = json.loads(ACTIVE_PIPE.read_text(encoding="utf-8"))
        except Exception:
            return False
        paper_path = pipe.get("paper_path")
        return (
            pipe.get("clean_title") == folder.name
            and paper_path
            and Path(paper_path).exists()
        )
    return False


def workflow_produzione(args):
    folder = args.folder
    if not folder:
        folder = choose_cleaned_folder(produzione_ready)
    setup_pipeline_for_cleaned_folder(folder)
    result = run_cmd([PYTHON, ROOT / "Execution/enea/notebooklm_orchestrator.py"], check=False)
    print((result.stdout or result.stderr).strip())
    if result.returncode != 0:
        raise WorkflowError(result.stderr or result.stdout or "Produzione fallita.")
    return 0


def workflow_infografica(args):
    pipeline = read_active_pipeline()
    target_dir = Path(pipeline.get("target_dir") or CLEANED_DIR / pipeline.get("clean_title", ""))
    if not target_dir.exists():
        raise WorkflowError(f"Cartella di lavorazione non trovata: {target_dir}")

    input_path = args.input
    if not input_path:
        downloads = sorted(
            DOWNLOADS.glob("*_infografica.png"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        if not downloads:
            raise WorkflowError("Nessuna infografica *_infografica.png in Downloads.")
        input_path = str(downloads[0])

    raw_dest = target_dir / "infografica_raw.png"
    cleaned_dest = target_dir / "infografica_cleaned.png"
    shutil.copy2(input_path, raw_dest)

    result = run_cmd(
        [PYTHON, ROOT / "Execution/enea/clean_infographic.py", str(raw_dest), str(cleaned_dest)],
        check=False,
    )
    print((result.stdout or result.stderr).strip())
    if result.returncode != 0 or not cleaned_dest.exists():
        raise WorkflowError("Pulizia infografica fallita.")
    log(f"Infografica pronta: {cleaned_dest}")
    return 0


def workflow_pulizia(args):
    video = args.video
    if not video:
        recent = []
        now = time.time()
        for path in DOWNLOADS.glob("*_raw.mp4"):
            if now - path.stat().st_mtime < 86400:
                recent.append(path.name)
        recent.sort(key=lambda name: (DOWNLOADS / name).stat().st_mtime, reverse=True)
        video = prompt_choice(recent, "Seleziona video raw")
    result = run_cmd([PYTHON, ROOT / "Execution/enea/video_processor.py", video], check=False)
    print((result.stdout or result.stderr).strip())
    if result.returncode != 0:
        raise WorkflowError(result.stderr or result.stdout or "Pulizia fallita.")
    return 0


def ready_upload_folders():
    folders = []
    for path in sorted(CLEANED_DIR.iterdir()):
        if not path.is_dir():
            continue
        files = {file.name for file in path.iterdir()}
        if any(name.endswith("_cleaned.mp4") for name in files) and "video_metadata.md" in files:
            folders.append(path.name)
    return folders


def mark_facebook_suspended(folder: str) -> None:
    """Set Facebook tracking to Sospeso unless a real post already exists."""
    tracking = {}
    if TRACKING_PATH.exists():
        tracking = json.loads(TRACKING_PATH.read_text(encoding="utf-8"))
    entry = tracking.get(folder, {})
    pending = {"Da fare", "Mancante", "", None}
    for key in ("facebook_url", "facebook_cover_status"):
        if entry.get(key) in pending:
            run_cmd([PYTHON, ROOT / "Execution/enea/tracking_manager.py", folder, key, "Sospeso"])


def workflow_upload(args):
    folder = args.folder or prompt_choice(ready_upload_folders(), "Seleziona video da caricare")
    folder_path = CLEANED_DIR / folder
    meta_path = folder_path / "video_metadata.md"
    thumb_path = folder_path / "copertina.jpg"
    if not thumb_path.exists():
        thumb_path = folder_path / "copertina.png"
    videos = sorted(folder_path.glob("*_cleaned.mp4"))
    if not videos:
        raise WorkflowError(f"Nessun video pulito in {folder_path}")
    title = folder.replace("_", " ")
    first_line = meta_path.read_text(encoding="utf-8").splitlines()[0]
    if "Metadati Video - " in first_line:
        title = first_line.replace("#", "").replace("Metadati Video - ", "").strip()
    publish_at = args.schedule
    if not publish_at:
        tomorrow = datetime.now() + timedelta(days=1)
        publish_at = tomorrow.strftime("%Y-%m-%dT08:00:00+01:00")
    auth_cmd = [PYTHON, ROOT / "Execution/enea/youtube_auth.py"]
    if args.force_auth:
        auth_cmd.append("--force")
    auth_result = run_cmd(auth_cmd, cwd=ROOT, check=False)
    print((auth_result.stdout or auth_result.stderr).strip())
    if auth_result.returncode != 0:
        raise WorkflowError(
            auth_result.stderr
            or auth_result.stdout
            or "Autenticazione YouTube fallita. Esegui `./workflow youtube-auth`."
        )
    cmd = [
        PYTHON,
        ROOT / "Execution/enea/youtube_uploader.py",
        videos[0],
        title,
        meta_path,
        "--thumbnail",
        thumb_path,
        "--schedule",
        publish_at,
    ]
    result = run_cmd(cmd, cwd=ROOT / "Execution/credentials", check=False)
    print((result.stdout or result.stderr).strip())
    if result.returncode != 0:
        raise WorkflowError(result.stderr or result.stdout or "Upload fallito.")
    print("Facebook sospeso: salto Buffer Facebook. Programmo solo Instagram.")
    mark_facebook_suspended(folder)
    ig_cmd = [
        PYTHON,
        ROOT / "Execution/marcello/buffer_post_single.py",
        "--platform",
        "instagram",
        "--folder-name",
        folder,
    ]
    ig_result = run_cmd(ig_cmd, check=False)
    print((ig_result.stdout or ig_result.stderr).strip())
    if ig_result.returncode != 0:
        raise WorkflowError(ig_result.stderr or ig_result.stdout or "Instagram Buffer fallito.")
    return 0


def workflow_youtube_auth(args):
    cmd = [PYTHON, ROOT / "Execution/enea/youtube_auth.py"]
    if args.force:
        cmd.append("--force")
    result = run_cmd(cmd, cwd=ROOT, check=False)
    print((result.stdout or result.stderr).strip())
    if result.returncode != 0:
        raise WorkflowError(result.stderr or result.stdout or "Autenticazione YouTube fallita.")
    return 0


def workflow_instagram(args):
    cmd = [
        PYTHON,
        ROOT / "Execution/marcello/buffer_post_single.py",
        "--platform",
        "instagram",
    ]
    if args.video_id:
        cmd.extend(["--video-id", args.video_id])
    if getattr(args, "folder_name", None):
        cmd.extend(["--folder-name", args.folder_name])
    if args.hour is not None:
        cmd.extend(["--hour", str(args.hour)])
    if args.dry_run:
        cmd.append("--dry-run")
    result = run_cmd(cmd, check=False)
    print((result.stdout or result.stderr).strip())
    if result.returncode != 0:
        raise WorkflowError(result.stderr or result.stdout or "Instagram workflow fallito.")
    return 0


def playlist_candidates():
    tracking = {}
    if TRACKING_PATH.exists():
        with open(TRACKING_PATH, "r", encoding="utf-8") as handle:
            tracking = json.load(handle)
    folders = []
    for path in sorted(CLEANED_DIR.iterdir()):
        if not path.is_dir():
            continue
        info = tracking.get(path.name, {})
        if info.get("youtube_id") and not info.get("playlist"):
            folders.append(path.name)
    return folders


def workflow_playlist(args):
    folder = args.folder or prompt_choice(playlist_candidates(), "Seleziona video per playlist")
    result = run_cmd([PYTHON, ROOT / "Execution/romolo/catalog_video.py", folder], cwd=ROOT / "Execution/romolo", check=False)
    print((result.stdout or result.stderr).strip())
    if result.returncode != 0:
        raise WorkflowError(result.stderr or result.stdout or "Playlist fallita.")
    return 0


def workflow_shorts(_args):
    result = run_cmd([PYTHON, ROOT / "Execution/romolo/batch_update_shorts.py"], check=False)
    print((result.stdout or result.stderr).strip())
    if result.returncode != 0:
        raise WorkflowError(result.stderr or result.stdout or "Shorts workflow fallito.")
    return 0


def workflow_list(_args):
    workflows = [
        "download",
        "backup",
        "gmail",
        "report",
        "articoli",
        "paper",
        "copertina",
        "produzione",
        "infografica",
        "pulizia",
        "youtube-auth",
        "upload",
        "instagram",
        "playlist",
        "shorts",
        "competitor",
    ]
    print("\n".join(workflows))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description="Workflow runner generale per canale")
    subparsers = parser.add_subparsers(dest="workflow", required=True)

    subparsers.add_parser("list")
    subparsers.add_parser("download")

    backup = subparsers.add_parser("backup")
    backup.add_argument("--message")

    subparsers.add_parser("gmail")
    subparsers.add_parser("report")
    subparsers.add_parser("competitor")

    articoli = subparsers.add_parser("articoli")
    articoli.add_argument("--tags")
    articoli.add_argument("--query")
    articoli.add_argument("--year", type=int, default=2000)

    paper = subparsers.add_parser("paper")
    paper.add_argument("--paper-index", type=int)
    paper.add_argument("--title-index", type=int)
    paper.add_argument("--approve-cover", action="store_true")

    copertina = subparsers.add_parser("copertina")
    copertina.add_argument("--folder")
    copertina.add_argument("--approve-cover", action="store_true")

    produzione = subparsers.add_parser("produzione")
    produzione.add_argument("--folder")

    infografica = subparsers.add_parser("infografica")
    infografica.add_argument("--input", help="Percorso infografica raw (default: più recente in Downloads)")

    pulizia = subparsers.add_parser("pulizia")
    pulizia.add_argument("--video")

    youtube_auth = subparsers.add_parser("youtube-auth")
    youtube_auth.add_argument("--force", action="store_true")

    upload = subparsers.add_parser("upload")
    upload.add_argument("--folder")
    upload.add_argument("--schedule")
    upload.add_argument("--force-auth", action="store_true")

    instagram = subparsers.add_parser("instagram")
    instagram.add_argument("--video-id")
    instagram.add_argument("--folder-name")
    instagram.add_argument("--hour", type=int)
    instagram.add_argument("--dry-run", action="store_true")

    playlist = subparsers.add_parser("playlist")
    playlist.add_argument("--folder")

    subparsers.add_parser("shorts")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    handlers = {
        "list": workflow_list,
        "download": workflow_download,
        "backup": workflow_backup,
        "gmail": workflow_gmail,
        "report": workflow_report,
        "articoli": workflow_articoli,
        "paper": workflow_paper,
        "copertina": workflow_copertina,
        "produzione": workflow_produzione,
        "infografica": workflow_infografica,
        "pulizia": workflow_pulizia,
        "youtube-auth": workflow_youtube_auth,
        "upload": workflow_upload,
        "instagram": workflow_instagram,
        "playlist": workflow_playlist,
        "shorts": workflow_shorts,
        "competitor": workflow_competitor,
    }
    try:
        return handlers[args.workflow](args)
    except WorkflowError as error:
        print(f"❌ {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
