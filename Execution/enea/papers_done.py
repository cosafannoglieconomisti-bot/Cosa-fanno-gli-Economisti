#!/usr/bin/env python3
"""Registro unico dei paper già trattati + controllo anti-doppione (obbligatorio).

Nato dall'incidente 2026-10-08: «Il sindacato spezza il caporalato?» era lo stesso
paper (Dipoppa, APSR 2025, DOI 10.1017/S0003055424001138) già uscito come
«Denunciare aiuta l'integrazione?» a fine settembre. Un PDF duplicato era rimasto in
Papers/Da fare e la pipeline lo ha riproposto.

Fonti del registro (rigenerato a ogni controllo, quindi mai stantio):
  - Cleaned/*/video_metadata.md (+ README.md): titolo accademico, DOI, autori
  - Cleaned/*/*.pdf: DOI in prima pagina
  - Cleaned/video_tracking.json: academic_title, youtube_id
  - Non_pubblicati/*/: paper prodotti ma da NON pubblicare (es. Tracking Inequality)
  - Cleaned/papers_done_seed.json: autori/titoli curati (da coda outreach) + voci manuali

Uso:
  python3 Execution/enea/papers_done.py build            # scrive Cleaned/papers_done.json
  python3 Execution/enea/papers_done.py check FILE.pdf   # exit 0 nuovo | 2 GIÀ FATTO | 3 probabile (verifica a mano)
  python3 Execution/enea/papers_done.py check --doi 10.x/y --title "..." --authors "A; B"
  python3 Execution/enea/papers_done.py scan [--move]    # controlla Papers/Da fare; --move sposta i GIÀ FATTI in Papers/Gia_fatti
  ./workflow papers-done [scan|build|check ...]          # stesso, dal runner
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import shutil
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CLEANED_DIR = REPO_ROOT / "Cleaned"
NON_PUB_DIR = REPO_ROOT / "Non_pubblicati"
PAPERS_DIR = REPO_ROOT / "Papers" / "Da fare"
DONE_DIR = REPO_ROOT / "Papers" / "Gia_fatti"
TRACKING_PATH = CLEANED_DIR / "video_tracking.json"
REGISTRY_PATH = CLEANED_DIR / "papers_done.json"
SEED_PATH = CLEANED_DIR / "papers_done_seed.json"

DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"'<>()\[\]{},;]+", re.IGNORECASE)
NBER_RE = re.compile(r"(?:nber\.org/papers/|NBER\s+Working\s+Paper\s+(?:No\.?\s*)?)w?(\d{4,6})", re.IGNORECASE)
STOP = set(
    "a an the of and or in on at to for from by with without into over under than as is are was were be "
    "do does did can could should would will evidence study studies new paper analysis case effect effects "
    "when how what why who which whose role impact impacts".split()
)
SKIP_DIRS = {"__pycache__"}
HEADER_RE = re.compile(r"journal|review|doi|©|copyright|cambridge|elsevier|oxford|published|available online|"
                       r"licen[cs]e|downloaded|working paper|\bvol\b|\bno\.|pp\.|\b(19|20)\d\d\b", re.IGNORECASE)


# ── normalizzazione ─────────────────────────────────────────────────────────
def strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def norm_text(text: str) -> str:
    text = strip_accents(text or "").lower()
    text = text.replace("ﬁ", "fi").replace("ﬂ", "fl").replace("ﬀ", "ff")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def norm_title(title: str) -> str:
    t = norm_text(title)
    return re.sub(r"^(the|a|an) ", "", t)


def norm_doi(doi: str) -> str:
    doi = (doi or "").strip().lower()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
    doi = doi.rstrip(".,;:)]}'\"")
    return doi


def surnames(authors) -> list[str]:
    if isinstance(authors, str):
        parts = re.split(r";|,|\band\b|\bed\b|\be\b|&", authors)
    else:
        parts = list(authors or [])
    out = []
    for p in parts:
        p = norm_text(p)
        if not p or p in {"et al", "al"}:
            continue
        p = re.sub(r"\bet al\b", "", p).strip()
        toks = p.split()
        if not toks:
            continue
        # cognomi composti: "di lonardo", "de la croix", "londono velez"
        if len(toks) >= 2 and toks[-2] in {"di", "de", "la", "van", "von", "del", "da", "der", "le", "dal", "dell"}:
            sn = " ".join(toks[-2:])
            if len(toks) >= 3 and toks[-3] in {"de", "van"}:
                sn = " ".join(toks[-3:])
        else:
            sn = toks[-1]
        if len(sn) >= 3 and sn not in out:
            out.append(sn)
    return out


def sig_tokens(title: str) -> list[str]:
    return [t for t in norm_title(title).split() if t not in STOP and len(t) > 2]


# ── estrazione da file ──────────────────────────────────────────────────────
def pdf_front_text(pdf: Path, pages: int = 2) -> tuple[str, str]:
    """(testo prime pagine, titolo metadata)"""
    try:
        import fitz  # PyMuPDF
    except Exception:
        return "", ""
    try:
        doc = fitz.open(str(pdf))
        txt = "\n".join(doc[i].get_text() for i in range(min(pages, len(doc))))
        meta_title = (doc.metadata or {}).get("title") or ""
        return txt, meta_title
    except Exception:
        return "", ""


def find_dois(text: str) -> list[str]:
    out = []
    for m in DOI_RE.findall(text or ""):
        d = norm_doi(m)
        if d.count("/") >= 1 and len(d) > 8 and d not in out and not d.startswith("10.7910/dvn"):  # dataverse != paper
            out.append(d)
    return out


def find_ids(text: str) -> list[str]:
    return sorted({f"nber:w{n}" for n in NBER_RE.findall(text or "")})


TITLE_PATTERNS = [
    r"\*\*Titolo accademico:\*\*\s*(.+)",
    r"(?:Lo studio|L[’']articolo|Il paper|Questo working paper)\s+[\"“«]([^\"”»]{6,300})[\"”»]",
    r"^-\s*Paper:\s*\*([^*]{6,300})\*",
]


def parse_metadata_md(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {}
    titles = []
    for pat in TITLE_PATTERNS:
        for m in re.findall(pat, text, flags=re.MULTILINE):
            t = m.strip().strip("*").strip()
            if t and t not in titles:
                titles.append(t)
    authors = ""
    m = re.search(r"\*\*Autori:\*\*\s*(.+)", text)
    if m:
        authors = m.group(1).strip()
    title_it = ""
    m = re.search(r"^#+\s*Metadati Video\s*[-–—]\s*(.+)$", text, flags=re.MULTILINE)
    if m:
        title_it = m.group(1).strip()
    return {
        "titles": titles,
        "dois": find_dois(text),
        "ids": find_ids(text),
        "authors": authors,
        "title_it": title_it,
        "never_publish": "NON PUBBLICARE" in text.upper(),
    }


# ── costruzione registro ────────────────────────────────────────────────────
def _new_entry(slug: str, source: str) -> dict:
    return {
        "slugs": [slug],
        "sources": [source],
        "title_it": "",
        "academic_titles": [],
        "dois": [],
        "ids": [],
        "authors": "",
        "surnames": [],
        "youtube_ids": [],
        "status": "fatto",
    }


def _merge(dst: dict, src: dict) -> None:
    for k in ("slugs", "sources", "academic_titles", "dois", "ids", "surnames", "youtube_ids"):
        for v in src.get(k, []):
            if v and v not in dst[k]:
                dst[k].append(v)
    for k in ("title_it", "authors"):
        if not dst.get(k) and src.get(k):
            dst[k] = src[k]
    if src.get("status") == "non_pubblicato_mai_pubblicare":
        dst["status"] = "non_pubblicato_mai_pubblicare"


def _scan_folder(folder: Path, source: str) -> dict:
    e = _new_entry(folder.name, source)
    for md_name in ("video_metadata.md", "README.md"):
        md = folder / md_name
        if md.exists():
            info = parse_metadata_md(md)
            for t in info.get("titles", []):
                if t not in e["academic_titles"]:
                    e["academic_titles"].append(t)
            for d in info.get("dois", []):
                if d not in e["dois"]:
                    e["dois"].append(d)
            for i in info.get("ids", []):
                if i not in e["ids"]:
                    e["ids"].append(i)
            e["authors"] = e["authors"] or info.get("authors", "")
            if md_name == "video_metadata.md":
                e["title_it"] = e["title_it"] or info.get("title_it", "")
            if info.get("never_publish"):
                e["status"] = "non_pubblicato_mai_pubblicare"
    for pdf in sorted(folder.glob("*.pdf")):
        txt, meta_title = pdf_front_text(pdf, pages=1)
        for d in find_dois(txt)[:2]:
            if d not in e["dois"]:
                e["dois"].append(d)
        for i in find_ids(txt):
            if i not in e["ids"]:
                e["ids"].append(i)
    # DOI in metadata: tieni solo quelli "propri" (Fonte/Bibliografia), scarta link a dataset ecc.
    e["surnames"] = surnames(e["authors"])
    return e


def build_registry(write: bool = True) -> dict:
    entries: list[dict] = []

    def add(entry: dict) -> None:
        nt = {norm_title(t) for t in entry["academic_titles"] if len(norm_title(t)) > 3}
        nd = set(entry["dois"])
        ni = set(entry["ids"])
        for ex in entries:
            ex_t = {norm_title(t) for t in ex["academic_titles"] if len(norm_title(t)) > 3}
            if (nd & set(ex["dois"])) or (ni & set(ex["ids"])) or (nt & ex_t) or (set(entry["slugs"]) & set(ex["slugs"])):
                _merge(ex, entry)
                return
        entries.append(entry)

    if CLEANED_DIR.exists():
        for folder in sorted(p for p in CLEANED_DIR.iterdir() if p.is_dir() and p.name not in SKIP_DIRS):
            add(_scan_folder(folder, "Cleaned"))
    if NON_PUB_DIR.exists():
        for folder in sorted(p for p in NON_PUB_DIR.iterdir() if p.is_dir()):
            e = _scan_folder(folder, "Non_pubblicati")
            e["status"] = "non_pubblicato_mai_pubblicare"
            add(e)

    tracking = {}
    if TRACKING_PATH.exists():
        try:
            tracking = json.loads(TRACKING_PATH.read_text(encoding="utf-8"))
        except Exception:
            tracking = {}
    for slug, v in tracking.items():
        if not isinstance(v, dict) or slug.startswith("--"):
            continue
        e = _new_entry(slug, "video_tracking")
        if v.get("academic_title"):
            e["academic_titles"].append(v["academic_title"])
        e["title_it"] = v.get("title", "")
        for k in ("youtube_id", "previous_youtube_id"):
            if v.get(k):
                e["youtube_ids"].append(v[k])
        add(e)

    if SEED_PATH.exists():
        seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))
        for s in seed.get("papers", []):
            e = _new_entry(s["slug"], s.get("source", "seed"))
            e["academic_titles"] = [t for t in s.get("academic_titles", []) if t]
            e["dois"] = [norm_doi(d) for d in s.get("dois", []) if d]
            e["ids"] = s.get("ids", [])
            e["authors"] = s.get("authors", "")
            e["title_it"] = s.get("title_it", "")
            e["surnames"] = surnames(e["authors"])
            if s.get("status"):
                e["status"] = s["status"]
            add(e)

    # voci vuote (es. chiave tracking senza dati) già coperte da un'altra voce con lo stesso slug
    all_slugs = {}
    for e in entries:
        for sl in e["slugs"]:
            all_slugs[sl] = all_slugs.get(sl, 0) + 1
    entries = [e for e in entries if e["academic_titles"] or e["dois"] or e["ids"]
               or not any(all_slugs[sl] > 1 for sl in e["slugs"])]

    for e in entries:
        if not e["surnames"] and e["authors"]:
            e["surnames"] = surnames(e["authors"])
        else:
            for sn in surnames(e["authors"]):
                if sn not in e["surnames"]:
                    e["surnames"].append(sn)

    registry = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "generated_by": "Execution/enea/papers_done.py build",
        "note": "Registro paper già trattati. Generato automaticamente: non modificare a mano, usa Cleaned/papers_done_seed.json.",
        "count": len(entries),
        "papers": entries,
    }
    if write:
        REGISTRY_PATH.write_text(json.dumps(registry, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return registry


# ── controllo ───────────────────────────────────────────────────────────────
def check_candidate(text: str = "", meta_title: str = "", dois=None, ids=None, title: str = "",
                    authors: str = "", registry: dict | None = None, allow_slugs=()) -> list[dict]:
    """Ritorna lista di match: {'level': 'certo'|'probabile', 'reason', 'slugs', 'title'}"""
    registry = registry or build_registry(write=False)
    front = norm_text(" ".join([title or "", meta_title or "", (text or "")[:6000]]))
    head = norm_text(" ".join([title or "", meta_title or "", (text or "")[:2500]]))
    cand_dois = {norm_doi(d) for d in (dois or [])} | set(find_dois((text or "")[:6000]))
    cand_ids = set(ids or []) | set(find_ids((text or "")[:6000]))
    cand_title = norm_title(title or meta_title or "")
    cand_surn = set(surnames(authors)) if authors else set()
    matches = []
    for e in registry["papers"]:
        if set(e["slugs"]) & set(allow_slugs):
            continue
        reason, level = None, None
        if cand_dois & set(e["dois"]):
            reason, level = f"DOI {sorted(cand_dois & set(e['dois']))[0]}", "certo"
        elif cand_ids & set(e["ids"]):
            reason, level = f"ID {sorted(cand_ids & set(e['ids']))[0]}", "certo"
        else:
            surn_hits = [s for s in e["surnames"] if (s in cand_surn) or re.search(rf"\b{re.escape(s)}\b", head)]
            need = min(2, len(e["surnames"])) if e["surnames"] else 99
            authors_ok = len(surn_hits) >= need
            for t in e["academic_titles"]:
                nt = norm_title(t)
                if not nt:
                    continue
                words = nt.split()
                ratio = difflib.SequenceMatcher(None, cand_title, nt).ratio() if cand_title else 0
                sub_ok = len(cand_title.split()) >= 4 and (f" {cand_title} " in f" {nt} " or f" {nt} " in f" {cand_title} ")
                if (len(words) >= 3 and f" {nt} " in f" {front} ") or ratio >= 0.9 or sub_ok or \
                   (len(words) < 3 and f" {nt} " in f" {head} " and authors_ok):
                    reason, level = f"titolo «{t}»", "certo"
                    break
                toks = sig_tokens(t)
                if toks and authors_ok:
                    hit = sum(1 for tk in toks if re.search(rf"\b{re.escape(tk)}", front))
                    if hit / len(toks) >= 0.6:
                        reason, level = f"autori {', '.join(surn_hits)} + titolo simile «{t}» ({hit}/{len(toks)} parole)", "probabile"
        if reason:
            matches.append({
                "level": level,
                "reason": reason,
                "slugs": e["slugs"],
                "title": (e["academic_titles"] or [""])[0],
                "status": e["status"],
            })
    matches.sort(key=lambda m: 0 if m["level"] == "certo" else 1)
    return matches


def check_pdf(pdf: Path, registry: dict | None = None, allow_slugs=()) -> list[dict]:
    text, meta_title = pdf_front_text(pdf, pages=2)
    if re.match(r"^(PSR_|untitled|microsoft word)", meta_title or "", re.IGNORECASE):
        meta_title = ""
    return check_candidate(text=text, meta_title=meta_title, registry=registry, allow_slugs=allow_slugs)


def filter_new_pdfs(pdf_paths, verbose: bool = True):
    """Usato da ./workflow paper: esclude i PDF già fatti (match certo)."""
    registry = build_registry(write=True)
    keep, excluded = [], []
    for p in pdf_paths:
        ms = check_pdf(Path(p), registry)
        certain = [m for m in ms if m["level"] == "certo"]
        if certain:
            excluded.append((Path(p), certain[0]))
            if verbose:
                print(f"⛔ GIÀ FATTO, escluso: {Path(p).name} → {', '.join(certain[0]['slugs'])} ({certain[0]['reason']})")
            continue
        if ms and verbose:
            print(f"⚠️ PROBABILE DOPPIONE (verifica prima di proporlo): {Path(p).name} → {', '.join(ms[0]['slugs'])} ({ms[0]['reason']})")
        keep.append(Path(p))
    return keep, excluded


def assert_new(pdf: Path, allow_slugs=()) -> None:
    ms = [m for m in check_pdf(Path(pdf), allow_slugs=allow_slugs) if m["level"] == "certo"]
    if ms:
        m = ms[0]
        raise RuntimeError(f"Paper GIÀ FATTO: {Path(pdf).name} = {', '.join(m['slugs'])} ({m['reason']}). Stop.")


def _unique_dest(dest_dir: Path, name: str) -> Path:
    dest = dest_dir / name
    i = 2
    while dest.exists():
        dest = dest_dir / f"{Path(name).stem} ({i}){Path(name).suffix}"
        i += 1
    return dest


def scan(move: bool = False) -> int:
    registry = build_registry(write=True)
    pdfs = sorted(PAPERS_DIR.rglob("*.pdf")) if PAPERS_DIR.exists() else []
    found = 0
    log_lines = []
    for pdf in pdfs:
        ms = check_pdf(pdf, registry)
        if not ms:
            continue
        m = ms[0]
        found += 1
        tag = "GIÀ FATTO" if m["level"] == "certo" else "PROBABILE"
        print(f"[{tag}] {pdf.relative_to(PAPERS_DIR)} → {', '.join(m['slugs'])} ({m['reason']})")
        if move and m["level"] == "certo":
            DONE_DIR.mkdir(parents=True, exist_ok=True)
            dest = _unique_dest(DONE_DIR, pdf.name)
            shutil.move(str(pdf), str(dest))
            log_lines.append(f"- {datetime.now():%Y-%m-%d %H:%M} `{pdf.name}` → `{dest.name}` — già fatto come {', '.join(m['slugs'])} ({m['reason']})")
            print(f"    spostato in {dest.relative_to(REPO_ROOT)}")
    # doppioni interni a Da fare (stesso paper in due versioni/file)
    fronts = []
    for pdf in pdfs:
        if not pdf.exists():
            continue
        txt, _ = pdf_front_text(pdf, pages=1)
        body = [ln for ln in txt.splitlines() if ln.strip() and not HEADER_RE.search(ln)]
        fronts.append((pdf, norm_text(" ".join(body))[:160], set(find_dois(txt[:6000]))))
    for i in range(len(fronts)):
        for j in range(i + 1, len(fronts)):
            a, b = fronts[i], fronts[j]
            same_doi = bool(a[2] & b[2])
            sim = difflib.SequenceMatcher(None, a[1], b[1]).ratio() if a[1] and b[1] else 0
            if same_doi or (sim >= 0.88 and min(len(a[1]), len(b[1])) >= 80):
                found += 1
                print(f"[DOPPIONE INTERNO] {a[0].name} ≈ {b[0].name} ({'DOI' if same_doi else f'inizio testo {sim:.2f}'}) — tieni la versione più recente")
    if log_lines:
        log = DONE_DIR / "SPOSTATI.md"
        head = "" if log.exists() else "# Paper spostati fuori da Papers/Da fare perché già trattati\n\n"
        with open(log, "a", encoding="utf-8") as fh:
            fh.write(head + "\n".join(log_lines) + "\n")
    print(f"Registro: {REGISTRY_PATH.relative_to(REPO_ROOT)} ({registry['count']} paper). PDF in Da fare: {len(pdfs)}; doppioni/probabili: {found}.")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Registro paper già fatti + controllo anti-doppione")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    c = sub.add_parser("check")
    c.add_argument("pdf", nargs="?")
    c.add_argument("--doi", action="append", default=[])
    c.add_argument("--title", default="")
    c.add_argument("--authors", default="")
    s = sub.add_parser("scan")
    s.add_argument("--move", action="store_true", help="sposta i GIÀ FATTI (match certo) in Papers/Gia_fatti")
    a = ap.parse_args(argv)
    if a.cmd == "build":
        r = build_registry(write=True)
        print(f"Registro scritto: {REGISTRY_PATH} ({r['count']} paper)")
        return 0
    if a.cmd == "scan":
        return scan(move=a.move)
    if a.cmd == "check":
        if a.pdf:
            ms = check_pdf(Path(a.pdf))
        else:
            ms = check_candidate(dois=a.doi, title=a.title, authors=a.authors)
        if not ms:
            print("OK: paper nuovo, nessun match nel registro.")
            return 0
        for m in ms:
            print(f"[{m['level'].upper()}] {', '.join(m['slugs'])} — {m['reason']} — stato: {m['status']}")
        return 2 if ms[0]["level"] == "certo" else 3
    return 1


if __name__ == "__main__":
    sys.exit(main())
