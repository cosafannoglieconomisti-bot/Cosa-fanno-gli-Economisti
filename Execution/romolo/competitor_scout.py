from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]

import html
import json
import os
import pickle
import random
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone

REPO_ROOT = str(REPO_ROOT)
SCOUT_FILE = os.path.join(REPO_ROOT, "Temp/romolo/competitor_engagement.md")
TRACKING_FILE = os.path.join(REPO_ROOT, "Cleaned/video_tracking.json")
HISTORY_FILE = os.path.join(REPO_ROOT, "Temp/romolo/competitor_comment_history.json")
PROPOSALS_JSON = os.path.join(REPO_ROOT, "Temp/romolo/competitor_proposals.json")

# DECISIONS 2026-06-05: commentare solo video pubblicati al massimo 30 giorni fa.
MAX_VIDEO_AGE_DAYS = 30
# Costo stimato in unita' quota YouTube Data API v3 (search.list = 100).
SEARCH_LIST_COST = 100
QUOTA_USED = {"search.list": 0}

# Token OAuth YouTube: path canonico + legacy sincronizzato da `./workflow youtube-auth`.
PRIMARY_TOKEN = os.path.join(REPO_ROOT, "Execution/credentials/token.pickle")
LEGACY_TOKEN = os.path.join(REPO_ROOT, "Execution/romolo/.tmp/tokens/token_youtube.pickle")

# Channel ID verificati il 2026-10-08 (feed RSS youtube.com/feeds/videos.xml?channel_id=... -> 200,
# titolo canale coincidente e ultimo video recente). Non aggiungere ID non verificati.
TARGET_CHANNELS_MAP = {
    "Will Media": "UCZM5aON36Iw0o0ngTaQSWVA",
    "I podcast di Will Media": "UCFg4BxczDuIRtBeuo46DE8g",
    "Geopop": "UCx7EWheHmjCW3vX8K2d09vg",
    "Starting Finance": "UCBahpZUV9wGy0ZdiVL2rqCA",
    "Factanza Media": "UCBdiMDTxwgNXz4PQa0uUhGw",
    "Breaking Italy": "UC4V3oCikXeSqYQr0hBMARwg",
    "LiberiOltre": "UCrdEJmK5bgFte04-UF7o29Q",
    "Nova Lectio": "UCRCWJCFoZUvkkWzIqzfBy6g",
    "Michele Boldrin": "UCMOiTfbUXxUFqJJtCQGHrrA",
    "ORA!": "UCJ1kdZmbCGxMVnWIahisqjA",
    "Mr. RIP": "UCBOtZaVafz_5OmUrqJAVStQ",
    "Limes Rivista Italiana di Geopolitica": "UCgG9BnqkGnU-ouYa5eAOdEw",
    "WesaChannel": "UCaM-zH6ji5kWncFMaBBc7Yg",
    "Scacchiere Globale": "UC8_OU41iCKb6Ri847Ea4JTQ",
    "What's up Economy": "UCnE113MJbg0sY5Ji0ZOOtcw",
    "Il Post": "UCGe1EHmk2SHt9fnpIRchvqg",
    "Osservatorio CPI": "UCEKOjs5vHu9pZoV2jR0NGlQ",
}

THEMATIC_KEYWORDS = [
    "evasione fiscale italia",
    "immigrazione criminalita italia",
    "regolarizzazione immigrati italia",
    "robot lavoro italia",
    "intelligenza artificiale lavoro italia",
    "patriarcato economia",
    "populismo italia",
    "corruzione politica italia",
    "mafia economia italia",
    "natalita italia",
    "tasse cultura civica",
    "industrializzazione storia economica",
]

KEYWORD_TO_PLAYLIST = {
    "evasione fiscale italia": "Economia Pubblica, Welfare e Demografia",
    "immigrazione criminalita italia": "Economia del Crimine e Mafie",
    "regolarizzazione immigrati italia": "Economia del Crimine e Mafie",
    "robot lavoro italia": "Economia del Lavoro, Discriminazione e Disuguaglianze",
    "intelligenza artificiale lavoro italia": "Economia del Lavoro, Discriminazione e Disuguaglianze",
    "patriarcato economia": "Economia della Cultura, Società e Religione",
    "populismo italia": "Economia Politica e Istituzioni",
    "corruzione politica italia": "Economia Politica e Istituzioni",
    "mafia economia italia": "Economia del Crimine e Mafie",
    "natalita italia": "Economia Pubblica, Welfare e Demografia",
    "tasse cultura civica": "Economia Pubblica, Welfare e Demografia",
    "industrializzazione storia economica": "Storia Economica e Sviluppo",
}

PLAYLIST_KEYWORDS = {
    "Economia del Crimine e Mafie": {
        "mafia", "mafie", "criminalita", "crimine", "corruzione", "violenza",
        "carcere", "migranti", "immigrazione", "sicurezza", "reati", "illegalita",
    },
    "Economia Politica e Istituzioni": {
        "stato", "governo", "istituzioni", "politica", "partiti", "corruzione",
        "democrazia", "populismo", "elezioni", "voto", "riforme", "fiducia",
    },
    "Storia Economica e Sviluppo": {
        "storia", "sviluppo", "industria", "industrializzazione", "urbanizzazione",
        "illuminismo", "citta", "agricoltura", "rivoluzione", "migrazione", "storica",
    },
    "Economia della Cultura, Società e Religione": {
        "cultura", "religione", "patriarcato", "famiglia", "societa", "media",
        "televisione", "norme", "valori", "chiesa",
    },
    "Economia del Lavoro, Discriminazione e Disuguaglianze": {
        "lavoro", "robot", "automazione", "salari", "occupazione", "disuguaglianza",
        "aborto", "genere", "razzismo", "discriminazione", "talento",
    },
    "Economia Pubblica, Welfare e Demografia": {
        "tasse", "evasione", "welfare", "pensioni", "natalita", "fertilita",
        "spesa", "demografia", "famiglia", "imposte",
    },
    "Economia dei Media e dello Sport": {
        "sport", "calcio", "media", "giornali", "televisione", "razzismo",
    },
}


def get_authenticated_service():
    """Auth non interattiva (routine schedulata): niente browser OAuth.

    Usa il token canonico `Execution/credentials/token.pickle` (fallback: legacy
    sincronizzato). Se nessun token e' valido/rinnovabile, fallisce subito con
    l'istruzione di eseguire `./workflow youtube-auth`.
    """
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    last_error = None
    for token_path in (PRIMARY_TOKEN, LEGACY_TOKEN):
        if not os.path.exists(token_path):
            continue
        try:
            with open(token_path, "rb") as handle:
                creds = pickle.load(handle)
            if not creds.valid and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            if creds.valid:
                return build("youtube", "v3", credentials=creds, static_discovery=False)
        except Exception as exc:  # token corrotto o refresh fallito: prova il successivo
            last_error = exc
    raise RuntimeError(
        "Token YouTube non valido o non rinnovabile. Esegui `./workflow youtube-auth` "
        f"(ultimo errore: {last_error})"
    )


def published_after_iso(days=MAX_VIDEO_AGE_DAYS):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    return cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")


def is_recent(published_at, days=MAX_VIDEO_AGE_DAYS):
    if not published_at:
        return False
    try:
        published = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    return published >= datetime.now(timezone.utc) - timedelta(days=days)


def load_comment_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as handle:
                data = json.load(handle)
                return data if isinstance(data, list) else []
        except Exception:
            return []
    return []


def normalize_tokens(text):
    text = (text or "").lower()
    text = (
        text.replace("criminalità", "criminalita")
        .replace("società", "societa")
        .replace("più", "piu")
        .replace("città", "citta")
        .replace("natalità", "natalita")
    )
    tokens = re.findall(r"[a-z0-9àèéìòù]+", text)
    stopwords = {
        "della", "delle", "degli", "dello", "del", "dell", "alla", "alle", "agli",
        "con", "come", "sono", "video", "economia", "paper", "cosa", "fanno", "gli",
        "nostro", "nostra", "questa", "quello", "quella", "italia", "parte",
    }
    return {token for token in tokens if len(token) > 3 and token not in stopwords}


def parse_metadata(path):
    with open(path, "r", encoding="utf-8") as handle:
        content = handle.read()

    description = ""
    if "## Descrizione YouTube" in content:
        description = content.split("## Descrizione YouTube", 1)[1]
        for sep in ["⏰ Fonte", "## Tag", "## Status Pipeline", "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"]:
            if sep in description:
                description = description.split(sep, 1)[0]
        description = description.strip()

    paper_title = ""
    match = re.search(r'Lo studio "([^"]+)"', description)
    if match:
        paper_title = match.group(1).strip()

    tags = []
    tag_match = re.search(r"## Tag\s*(.+)", content, re.DOTALL)
    if tag_match:
        first_line = tag_match.group(1).splitlines()[0]
        tags = [part.strip(" #,") for part in first_line.split(",") if part.strip()]

    return {
        "paper_title": paper_title,
        "description": description,
        "tags": tags,
        "raw": content,
    }


def extract_video_title(path, fallback_key):
    with open(path, "r", encoding="utf-8") as handle:
        first_line = handle.readline().strip()
    if first_line.startswith("#"):
        cleaned = first_line.lstrip("#").strip()
        if " - " in cleaned:
            return cleaned.split(" - ", 1)[1].strip()
        if cleaned:
            return cleaned
    return fallback_key.replace("_", " ")


def build_our_catalog():
    with open(TRACKING_FILE, "r", encoding="utf-8") as handle:
        tracking = json.load(handle)

    catalog = []
    for our_title, meta in tracking.items():
        youtube_url = meta.get("youtube_url")
        if not youtube_url or youtube_url == "Da fare":
            continue
        metadata_path = os.path.join(REPO_ROOT, "Cleaned", our_title, "video_metadata.md")
        if not os.path.exists(metadata_path):
            continue
        parsed = parse_metadata(metadata_path)
        playlist = meta.get("playlist", "")
        title_text = our_title.replace("_", " ")
        search_text = " ".join(
            [
                title_text,
                parsed["paper_title"],
                parsed["description"],
                " ".join(parsed["tags"]),
                playlist,
            ]
        )
        catalog.append(
            {
                "key": our_title,
                "video_title": extract_video_title(metadata_path, our_title),
                "title_text": title_text,
                "paper_title": parsed["paper_title"],
                "description": parsed["description"],
                "tags": parsed["tags"],
                "playlist": playlist,
                "youtube_url": youtube_url,
                "tokens": normalize_tokens(search_text),
            }
        )
    return catalog


def infer_candidate_theme(text):
    tokens = normalize_tokens(text)
    best_playlist = ""
    best_score = 0
    for playlist, keywords in PLAYLIST_KEYWORDS.items():
        score = len(tokens & keywords)
        if score > best_score:
            best_score = score
            best_playlist = playlist
    return best_playlist, best_score


def score_match(candidate, ours):
    candidate_text = " ".join([candidate["title"], candidate.get("description", ""), candidate.get("query", "")])
    candidate_tokens = normalize_tokens(candidate_text)
    overlap = len(candidate_tokens & ours["tokens"])
    candidate_theme, theme_score = infer_candidate_theme(candidate_text)
    expected_theme = candidate.get("expected_playlist", "")

    score = overlap * 5
    if expected_theme and ours["playlist"] != expected_theme:
        score -= 25
    if expected_theme and candidate_theme and candidate_theme != expected_theme:
        score -= 12
    if candidate_theme and candidate_theme == ours["playlist"]:
        score += 8
    if any(tag.lower() in candidate_text.lower() for tag in ours["tags"]):
        score += 3
    if ours["paper_title"] and any(tok in candidate_tokens for tok in normalize_tokens(ours["paper_title"])):
        score += 3
    score += min(theme_score, 3)

    title_lower = (candidate["title"] or "").lower()
    ours_key_lower = ours["key"].lower()
    if any(x in title_lower for x in ["natalit", "fertilit", "culle", "nascite"]):
        if any(x in ours_key_lower for x in ["figli", "natalita", "fertilit"]):
            score += 8
        if "pensione" in ours_key_lower:
            score += 3
    if any(x in title_lower for x in ["calcio", "mondial", "football", "fifa"]):
        if any(x in ours_key_lower for x in ["pallone", "calcio", "nazioni"]):
            score += 12
    if any(x in title_lower for x in ["corruzion", "populism", "vannacci"]):
        if any(x in ours_key_lower for x in ["corruzione", "popul"]):
            score += 6
    return score


# Frasi gia' usate in questo giro (e nell'ultimo report): evita aperture/chiusure ripetute.
USED_PHRASES = set()

GENERIC_OPENINGS = [
    "Bella puntata.",
    "Discussione interessante.",
    "Video fatto bene.",
    "Tema che merita, e qui è trattato con cura.",
    "Ottimo spunto.",
]


def load_recent_phrases():
    """Aperture e chiusure dell'ultimo report, per non ripeterle nel giro successivo."""
    if not os.path.exists(PROPOSALS_JSON):
        return
    try:
        with open(PROPOSALS_JSON, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        for item in data.get("proposals", []):
            first_sentence = (item.get("comment") or "").split(". ")[0].strip()
            if first_sentence:
                USED_PHRASES.add(first_sentence.rstrip(".") + ".")
    except Exception:
        pass


def pick_fresh(options):
    """Sceglie a caso una frase non ancora usata; se sono finite, una qualsiasi."""
    fresh = [option for option in options if option not in USED_PHRASES]
    choice = random.choice(fresh or options)
    USED_PHRASES.add(choice)
    return choice


def build_comment(candidate, ours):
    paper = ours["paper_title"] or ours["title_text"]
    our_url = ours["youtube_url"]
    title_lower = (candidate["title"] or "").lower()
    channel = candidate["channel"]

    openings = {
        "Economia del Crimine e Mafie": [
            f"Bel video, {channel}.",
            "Tema tosto, ma affrontato bene.",
            "Questo è uno di quei temi in cui il dettaglio conta parecchio.",
        ],
        "Economia Politica e Istituzioni": [
            "Spunto molto forte.",
            "Discussione centrata, soprattutto per come la mettete sul piano politico concreto.",
            f"Video interessante, {channel}.",
        ],
        "Storia Economica e Sviluppo": [
            "Molto bello questo taglio.",
            "Qui secondo noi c'è un punto davvero interessante.",
            "Bella ricostruzione, soprattutto perché evita il tono da riassunto scolastico.",
        ],
        "Economia della Cultura, Società e Religione": [
            "Tema super interessante.",
            "Questo è un ottimo esempio di come un tema culturale apra anche una domanda economica vera.",
            "Bella discussione, e secondo noi il punto merita parecchio.",
        ],
        "Economia del Lavoro, Discriminazione e Disuguaglianze": [
            "Qui il rischio di semplificare troppo è altissimo, quindi bene averlo messo sul tavolo.",
            "Argomento molto forte, soprattutto per come tocca questioni concrete.",
            "Video utile, perché su questi temi si va spesso di slogan.",
        ],
        "Economia Pubblica, Welfare e Demografia": [
            "Tema molto concreto, e si vede.",
            "Video utile, soprattutto perché entra in un dibattito che di solito resta superficiale.",
            "Qui il punto interessante è proprio separare percezioni e incentivi reali.",
        ],
        "Economia dei Media e dello Sport": [
            "Bella chiave di lettura.",
            "Questo taglio funziona molto bene.",
            "Tema interessante, anche perché di solito viene trattato solo come cronaca.",
        ],
    }

    bodies = {
        "Economia del Crimine e Mafie": [
            "La parte che ci convince di più è quando si passa dal racconto generale al meccanismo: incentivi, rischio di reato, effetti della legalità o della repressione.",
            "Su criminalità e sicurezza la differenza la fa quasi sempre il tipo di incentivo che crei, non solo la durezza del messaggio politico.",
            "Su questi temi la ricerca economica è utile proprio perché prova a misurare effetti causali, non solo impressioni.",
        ],
        "Economia Politica e Istituzioni": [
            "Secondo noi il punto più interessante è il pezzo di lungo periodo: fiducia, selezione della classe politica, memoria degli scandali.",
            "Qui la parte forte è il legame tra incentivi politici e comportamento degli elettori, che spesso nel dibattito pubblico resta sullo sfondo.",
            "La cosa che ci colpisce sempre è quanto questi shock politici lascino effetti persistenti, molto oltre la cronaca del momento.",
        ],
        "Storia Economica e Sviluppo": [
            "La cosa bella della storia economica è che spesso ribalta intuizioni molto diffuse con dati e confronti seri.",
            "Qui secondo noi ha senso portare dentro un po' di evidenza storica, perché il meccanismo vero emerge bene solo nel lungo periodo.",
            "Su questi temi ci aiuta molto guardare come cambiano incentivi e sviluppo nel tempo, non solo l'episodio storico singolo.",
        ],
        "Economia della Cultura, Società e Religione": [
            "Il bello di questi temi è che sembrano solo culturali, ma poi hanno effetti economici molto concreti su lavoro, famiglia e scelte individuali.",
            "Qui secondo noi entra in gioco proprio il pezzo più interessante: norme sociali e valori che poi cambiano comportamenti osservabili.",
            "La parte forte è quando si capisce che cultura e incentivi non sono mondi separati, anzi si rinforzano a vicenda.",
        ],
        "Economia del Lavoro, Discriminazione e Disuguaglianze": [
            "Su lavoro e tecnologia il punto è quasi sempre distinguere chi perde, chi guadagna e in quali territori si vede davvero l'effetto.",
            "Qui secondo noi conta molto andare oltre il titolo e guardare ai dati: non tutti i lavoratori subiscono lo stesso impatto.",
            "La parte utile della ricerca è che separa l'effetto sulla produttività da quello su salari, occupazione e composizione dei lavori.",
        ],
        "Economia Pubblica, Welfare e Demografia": [
            "Su tasse, welfare e demografia il punto vero è quasi sempre negli incentivi, più che negli annunci.",
            "Qui secondo noi è utile tenere insieme la parte politica e quella comportamentale: la reazione delle persone cambia molto il risultato finale.",
            "La parte che spesso manca nel dibattito è proprio questa: le politiche non producono solo costi o benefici, ma cambiano comportamenti.",
        ],
        "Economia dei Media e dello Sport": [
            "Qui i dati aiutano parecchio, perché molte intuizioni sembrano ovvie ma poi cambiano appena guardi gli incentivi.",
            "Secondo noi il valore aggiunto è proprio spostare il discorso dalla superficie ai meccanismi.",
            "Su questi temi la ricerca serve soprattutto a evitare letture troppo facili.",
        ],
    }

    bridges = [
        f"Noi su questo abbiamo fatto un video che si chiama \"{ours['video_title']}\" {our_url}",
        f"Se vi può interessare, il nostro video collegato è \"{ours['video_title']}\" {our_url}",
        f"Per chi vuole il lato più basato sui dati, il video da cui partire è \"{ours['video_title']}\" {our_url}",
        f"Ne abbiamo parlato in \"{ours['video_title']}\" {our_url}",
        f"Noi su un tema vicino abbiamo fatto \"{ours['video_title']}\" {our_url}",
    ]

    playlist = ours["playlist"]
    opening = pick_fresh(openings.get(playlist, []) + GENERIC_OPENINGS)
    body = pick_fresh(bodies.get(playlist, ["Secondo noi qui il valore aggiunto arriva quando il tema viene letto con dati e meccanismi causali."]))
    bridge = pick_fresh(bridges)

    if "immigra" in title_lower:
        body = "Su immigrazione e criminalità il punto delicato è quasi sempre distinguere percezioni, slogan e risultati empirici veri."
    elif "corruzion" in title_lower:
        body = "Su corruzione e politica il pezzo più interessante, secondo noi, è l'effetto di lungo periodo su fiducia, voto e selezione della classe dirigente."
    elif "mafia" in title_lower or "riciclag" in title_lower:
        body = "Qui secondo noi il punto forte è mostrare che la criminalità organizzata non è solo violenza, ma anche allocazione distorta di risorse e reti di potere."
    elif "robot" in title_lower or "intelligenza artificiale" in title_lower:
        body = "Su robot e IA il rischio è dire tutto o il contrario di tutto: la ricerca serve proprio a capire chi viene colpito davvero e con quali tempi."

    return f"{opening} {body} {bridge}"


def search_fixed_channels(youtube, history):
    candidates = []
    for channel_name, channel_id in TARGET_CHANNELS_MAP.items():
        try:
            QUOTA_USED["search.list"] += 1
            response = youtube.search().list(
                channelId=channel_id,
                part="snippet",
                type="video",
                maxResults=3,
                order="date",
                publishedAfter=published_after_iso(),
                relevanceLanguage="it",
            ).execute()
            for item in response.get("items", []):
                video_id = item["id"]["videoId"]
                if video_id in history:
                    continue
                if not is_recent(item["snippet"].get("publishedAt", "")):
                    continue
                channel_title = html.unescape(item["snippet"]["channelTitle"])
                if channel_title.strip().lower() == "cosa fanno gli economisti":
                    continue
                candidates.append(
                    {
                        "source": "fixed_channel",
                        "channel": channel_title,
                        "title": html.unescape(item["snippet"]["title"]),
                        "description": html.unescape(item["snippet"]["description"]),
                        "published_at": item["snippet"].get("publishedAt", ""),
                        "video_id": video_id,
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                    }
                )
        except Exception as exc:
            print(f"⚠️ Errore scansione canale {channel_name}: {exc}")
    return candidates


def search_semantic_keywords(youtube, history):
    candidates = []
    selected_keywords = random.sample(THEMATIC_KEYWORDS, min(6, len(THEMATIC_KEYWORDS)))
    for keyword in selected_keywords:
        try:
            QUOTA_USED["search.list"] += 1
            response = youtube.search().list(
                q=keyword,
                part="snippet",
                type="video",
                maxResults=4,
                publishedAfter=published_after_iso(),
                relevanceLanguage="it",
                regionCode="IT",
                order="relevance",
            ).execute()
            for item in response.get("items", []):
                video_id = item["id"]["videoId"]
                if video_id in history:
                    continue
                if not is_recent(item["snippet"].get("publishedAt", "")):
                    continue
                channel_title = html.unescape(item["snippet"]["channelTitle"])
                if channel_title.strip().lower() == "cosa fanno gli economisti":
                    continue
                candidates.append(
                    {
                        "source": "semantic_search",
                        "query": keyword,
                        "expected_playlist": KEYWORD_TO_PLAYLIST.get(keyword, ""),
                        "channel": channel_title,
                        "title": html.unescape(item["snippet"]["title"]),
                        "description": html.unescape(item["snippet"]["description"]),
                        "published_at": item["snippet"].get("publishedAt", ""),
                        "video_id": video_id,
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                    }
                )
        except Exception as exc:
            print(f"⚠️ Errore ricerca per '{keyword}': {exc}")
    return candidates


def dedupe_candidates(candidates):
    unique = []
    seen_ids = set()
    for candidate in candidates:
        if candidate["video_id"] in seen_ids:
            continue
        seen_ids.add(candidate["video_id"])
        unique.append(candidate)
    return unique


def rank_proposals(candidates, catalog):
    proposals = []
    for candidate in candidates:
        best_match = None
        best_score = 0
        for ours in catalog:
            if candidate.get("expected_playlist") and ours["playlist"] != candidate["expected_playlist"]:
                continue
            score = score_match(candidate, ours)
            if score > best_score:
                best_score = score
                best_match = ours
        candidate_theme, theme_score = infer_candidate_theme(
            " ".join([candidate["title"], candidate.get("description", ""), candidate.get("query", "")])
        )
        if not best_match or best_score < 12:
            continue
        if candidate.get("expected_playlist") and best_match["playlist"] != candidate["expected_playlist"]:
            continue
        if candidate.get("expected_playlist") and candidate_theme and candidate_theme != candidate["expected_playlist"] and theme_score > 0:
            continue
        if not candidate.get("expected_playlist") and candidate_theme and theme_score >= 2 and best_match["playlist"] != candidate_theme:
            continue
        proposals.append(
            {
                "candidate": candidate,
                "ours": best_match,
                "score": best_score,
                "comment": None,
            }
        )

    proposals.sort(key=lambda item: item["score"], reverse=True)

    diversified = []
    used_channels = set()
    used_ours = defaultdict(int)
    for proposal in proposals:
        channel = proposal["candidate"]["channel"]
        ours_key = proposal["ours"]["key"]
        if channel in used_channels:
            continue
        if used_ours[ours_key] >= 1:
            continue
        diversified.append(proposal)
        used_channels.add(channel)
        used_ours[ours_key] += 1
        if len(diversified) >= 5:
            break
    # I commenti si generano solo per le proposte finali, cosi' aperture e chiusure non si ripetono.
    for proposal in diversified:
        proposal["comment"] = build_comment(proposal["candidate"], proposal["ours"])
    return diversified


def write_report(proposals, stats=None):
    os.makedirs(os.path.dirname(SCOUT_FILE), exist_ok=True)
    stats = stats or {}
    with open(SCOUT_FILE, "w", encoding="utf-8") as handle:
        handle.write(f"# 🔍 Scouting Competitor & Proposte Commenti ({len(proposals)})\n\n")
        handle.write("> [!IMPORTANT]\n")
        handle.write("> Queste sono solo proposte da approvare o modificare. Nessun commento va pubblicato senza approvazione esplicita di Marco in chat.\n\n")
        handle.write(
            f"_Generato: {datetime.now().strftime('%Y-%m-%d %H:%M')} (ora locale) · "
            f"finestra video: ultimi {MAX_VIDEO_AGE_DAYS} giorni (publishedAfter {stats.get('published_after', '')}) · "
            f"candidati: {stats.get('candidates', 0)} · "
            f"quota stimata: {stats.get('quota', 0)} unita' ({stats.get('searches', 0)} search.list)_\n\n"
        )
        if not proposals:
            handle.write("Nessuna proposta con qualita' sufficiente in questo giro.\n")
        for index, proposal in enumerate(proposals, 1):
            candidate = proposal["candidate"]
            ours = proposal["ours"]
            handle.write(f"## {index}. Video: [{candidate['title']}]({candidate['url']})\n")
            handle.write(f"**Canale**: {candidate['channel']}\n")
            if candidate.get("published_at"):
                handle.write(f"**Pubblicato**: {candidate['published_at'][:10]}\n")
            if candidate.get("query"):
                handle.write(f"**Query di scoperta**: `{candidate['query']}`\n")
            handle.write(f"**Il nostro video correlato**: [{ours['video_title']}]({ours['youtube_url']})\n")
            handle.write(f"**Paper collegato**: {ours['paper_title'] or ours['title_text']}\n")
            handle.write(f"**Area tematica**: {ours['playlist']}\n")
            handle.write(f"**PROPOSTA COMMENTO**:\n> {proposal['comment']}\n\n---\n\n")
    write_proposals_json(proposals, stats)


def write_proposals_json(proposals, stats):
    """Proposte in formato macchina per `post_youtube_comment.py --batch` (solo dopo approvazione)."""
    items = []
    for index, proposal in enumerate(proposals, 1):
        candidate = proposal["candidate"]
        ours = proposal["ours"]
        items.append(
            {
                "index": index,
                "video_id": candidate["video_id"],
                "url": candidate["url"],
                "channel": candidate["channel"],
                "title": candidate["title"],
                "published_at": candidate.get("published_at", ""),
                "source": candidate.get("source", ""),
                "query": candidate.get("query", ""),
                "our_video_title": ours["video_title"],
                "our_video_url": ours["youtube_url"],
                "score": proposal["score"],
                "comment": proposal["comment"],
                "approved": False,
            }
        )
    with open(PROPOSALS_JSON, "w", encoding="utf-8") as handle:
        json.dump({"generated_at": datetime.now().isoformat(timespec="seconds"), "stats": stats, "proposals": items}, handle, ensure_ascii=False, indent=2)


def scout_competitors():
    print("🔍 Scouting competitor e video rilevanti...")
    youtube = get_authenticated_service()
    history = set(load_comment_history())
    load_recent_phrases()
    catalog = build_our_catalog()

    candidates = []
    candidates.extend(search_fixed_channels(youtube, history))
    candidates.extend(search_semantic_keywords(youtube, history))
    candidates = dedupe_candidates(candidates)

    stats = {
        "published_after": published_after_iso(),
        "candidates": len(candidates),
        "searches": QUOTA_USED["search.list"],
        "quota": QUOTA_USED["search.list"] * SEARCH_LIST_COST,
    }
    print(
        f"📊 Candidati (<= {MAX_VIDEO_AGE_DAYS} giorni, non gia' commentati): {len(candidates)} · "
        f"search.list: {stats['searches']} · quota stimata: {stats['quota']} unita'"
    )

    proposals = rank_proposals(candidates, catalog) if candidates else []
    if not candidates:
        print("⚠️ Nessun video candidato idoneo trovato.")
    elif not proposals:
        print("⚠️ Nessuna proposta con qualita' sufficiente.")

    write_report(proposals, stats)
    print(f"✅ Report salvato in: {SCOUT_FILE} ({len(proposals)} proposte)")


if __name__ == "__main__":
    scout_competitors()
