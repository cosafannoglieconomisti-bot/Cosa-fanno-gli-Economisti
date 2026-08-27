from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]

import json
import os
import random
import re
from collections import defaultdict

REPO_ROOT = str(REPO_ROOT)
SCOUT_FILE = os.path.join(REPO_ROOT, "Temp/romolo/competitor_engagement.md")
TRACKING_FILE = os.path.join(REPO_ROOT, "Cleaned/video_tracking.json")
HISTORY_FILE = os.path.join(REPO_ROOT, "Temp/romolo/competitor_comment_history.json")

TARGET_CHANNELS_MAP = {
    "Will Media": "UC9tN-R6R1_63m8J9N_oR_Fg",
    "Geopop": "UC64-M_yD1GZ9u3-E9nZ0W8A",
    "Starting Finance": "UCi1g6eK4qXU1M1t5M_s0o2A",
    "Factanza": "UCt9u1Vv_4m8q_mO7U2hV1XQ",
    "Breaking Italy": "UCg9xR8fE-9b7F-VqR0k1n_A",
    "Liberi Oltre": "UCrdEJmK5bgFte04-UF7o29Q",
    "Nova Lectio": "UCRCWJCFoZUvkkWzIqzfBy6g",
    "Michele Boldrin": "UCFN2gwHc86xWbV4pZ7d6fWA",
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
    from romolo_manage_channel import get_authenticated_service as auth
    return auth("youtube", "v3", ["https://www.googleapis.com/auth/youtube.force-ssl"])


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


def build_comment(candidate, ours):
    paper = ours["paper_title"] or ours["title_text"]
    our_url = ours["youtube_url"]
    title_lower = (candidate["title"] or "").lower()
    channel = candidate["channel"]

    openings = {
        "Economia del Crimine e Mafie": [
            f"Bel video, {channel}.",
            "Tema tosto, ma affrontato bene.",
            "Questo e' uno di quei temi in cui il dettaglio conta parecchio.",
        ],
        "Economia Politica e Istituzioni": [
            "Spunto molto forte.",
            "Discussione centrata, soprattutto per come la mettete sul piano politico concreto.",
            f"Video interessante, {channel}.",
        ],
        "Storia Economica e Sviluppo": [
            "Molto bello questo taglio.",
            "Qui secondo noi c'e' un punto davvero interessante.",
            "Bella ricostruzione, soprattutto perche' evita il tono da riassunto scolastico.",
        ],
        "Economia della Cultura, Società e Religione": [
            "Tema super interessante.",
            "Questo e' un ottimo esempio di come un tema culturale apra anche una domanda economica vera.",
            "Bella discussione, e secondo noi il punto merita parecchio.",
        ],
        "Economia del Lavoro, Discriminazione e Disuguaglianze": [
            "Qui il rischio di semplificare troppo e' altissimo, quindi bene averlo messo sul tavolo.",
            "Argomento molto forte, soprattutto per come tocca questioni concrete.",
            "Video utile, perche' su questi temi si va spesso di slogan.",
        ],
        "Economia Pubblica, Welfare e Demografia": [
            "Tema molto concreto, e si vede.",
            "Video utile, soprattutto perche' entra in un dibattito che di solito resta superficiale.",
            "Qui il punto interessante e' proprio separare percezioni e incentivi reali.",
        ],
        "Economia dei Media e dello Sport": [
            "Bella chiave di lettura.",
            "Questo taglio funziona molto bene.",
            "Tema interessante, anche perche' di solito viene trattato solo come cronaca.",
        ],
    }

    bodies = {
        "Economia del Crimine e Mafie": [
            "La parte che ci convince di piu' e' quando si passa dal racconto generale al meccanismo: incentivi, rischio di reato, effetti della legalita' o della repressione.",
            "Su criminalita' e sicurezza la differenza la fa quasi sempre il tipo di incentivo che crei, non solo la durezza del messaggio politico.",
            "Su questi temi la ricerca economica e' utile proprio perche' prova a misurare effetti causali, non solo impressioni.",
        ],
        "Economia Politica e Istituzioni": [
            "Secondo noi il punto piu' interessante e' il pezzo di lungo periodo: fiducia, selezione della classe politica, memoria degli scandali.",
            "Qui la parte forte e' il legame tra incentivi politici e comportamento degli elettori, che spesso nel dibattito pubblico resta sullo sfondo.",
            "La cosa che ci colpisce sempre e' quanto questi shock politici lascino effetti persistenti, molto oltre la cronaca del momento.",
        ],
        "Storia Economica e Sviluppo": [
            "La cosa bella della storia economica e' che spesso ribalta intuizioni molto diffuse con dati e confronti seri.",
            "Qui secondo noi ha senso portare dentro un po' di evidenza storica, perche' il meccanismo vero emerge bene solo nel lungo periodo.",
            "Su questi temi ci aiuta molto guardare come cambiano incentivi e sviluppo nel tempo, non solo l'episodio storico singolo.",
        ],
        "Economia della Cultura, Società e Religione": [
            "Il bello di questi temi e' che sembrano solo culturali, ma poi hanno effetti economici molto concreti su lavoro, famiglia e scelte individuali.",
            "Qui secondo noi entra in gioco proprio il pezzo piu' interessante: norme sociali e valori che poi cambiano comportamenti osservabili.",
            "La parte forte e' quando si capisce che cultura e incentivi non sono mondi separati, anzi si rinforzano a vicenda.",
        ],
        "Economia del Lavoro, Discriminazione e Disuguaglianze": [
            "Su lavoro e tecnologia il punto e' quasi sempre distinguere chi perde, chi guadagna e in quali territori si vede davvero l'effetto.",
            "Qui secondo noi conta molto andare oltre il titolo e guardare ai dati: non tutti i lavoratori subiscono lo stesso impatto.",
            "La parte utile della ricerca e' che separa l'effetto sulla produttivita' da quello su salari, occupazione e composizione dei lavori.",
        ],
        "Economia Pubblica, Welfare e Demografia": [
            "Su tasse, welfare e demografia il punto vero e' quasi sempre negli incentivi, piu' che negli annunci.",
            "Qui secondo noi e' utile tenere insieme la parte politica e quella comportamentale: la reazione delle persone cambia molto il risultato finale.",
            "La parte che spesso manca nel dibattito e' proprio questa: le politiche non producono solo costi o benefici, ma cambiano comportamenti.",
        ],
        "Economia dei Media e dello Sport": [
            "Qui i dati aiutano parecchio, perche' molte intuizioni sembrano ovvie ma poi cambiano appena guardi gli incentivi.",
            "Secondo noi il valore aggiunto e' proprio spostare il discorso dalla superficie ai meccanismi.",
            "Su questi temi la ricerca serve soprattutto a evitare letture troppo facili.",
        ],
    }

    bridges = [
        f"Noi su questo abbiamo fatto un video che si chiama \"{ours['video_title']}\": {our_url}",
        f"Se vi puo' interessare, il nostro video collegato e' \"{ours['video_title']}\" -> {our_url}",
        f"Per chi vuole il lato piu' data-driven, il video da cui partire e' \"{ours['video_title']}\" {our_url}",
    ]

    playlist = ours["playlist"]
    opening = random.choice(openings.get(playlist, ["Video interessante."]))
    body = random.choice(bodies.get(playlist, ["Secondo noi qui il valore aggiunto arriva quando il tema viene letto con dati e meccanismi causali."]))
    bridge = random.choice(bridges)

    if "immigra" in title_lower:
        body = "Su immigrazione e criminalita' il punto delicato e' quasi sempre distinguere percezioni, slogan e risultati empirici veri."
    elif "corruzion" in title_lower:
        body = "Su corruzione e politica il pezzo piu' interessante, secondo noi, e' l'effetto di lungo periodo su fiducia, voto e selezione della classe dirigente."
    elif "mafia" in title_lower or "riciclag" in title_lower:
        body = "Qui secondo noi il punto forte e' mostrare che la criminalita' organizzata non e' solo violenza, ma anche allocazione distorta di risorse e reti di potere."
    elif "robot" in title_lower or "intelligenza artificiale" in title_lower:
        body = "Su robot e IA il rischio e' dire tutto o il contrario di tutto: la ricerca serve proprio a capire chi viene colpito davvero e con quali tempi."

    return f"{opening} {body} {bridge}"


def search_fixed_channels(youtube, history):
    candidates = []
    for channel_name, channel_id in TARGET_CHANNELS_MAP.items():
        try:
            response = youtube.search().list(
                channelId=channel_id,
                part="snippet",
                type="video",
                maxResults=3,
                order="date",
                relevanceLanguage="it",
            ).execute()
            for item in response.get("items", []):
                video_id = item["id"]["videoId"]
                if video_id in history:
                    continue
                channel_title = item["snippet"]["channelTitle"]
                if channel_title.strip().lower() == "cosa fanno gli economisti":
                    continue
                candidates.append(
                    {
                        "source": "fixed_channel",
                        "channel": channel_title,
                        "title": item["snippet"]["title"],
                        "description": item["snippet"]["description"],
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
            response = youtube.search().list(
                q=keyword,
                part="snippet",
                type="video",
                maxResults=4,
                relevanceLanguage="it",
                order="relevance",
            ).execute()
            for item in response.get("items", []):
                video_id = item["id"]["videoId"]
                if video_id in history:
                    continue
                channel_title = item["snippet"]["channelTitle"]
                if channel_title.strip().lower() == "cosa fanno gli economisti":
                    continue
                candidates.append(
                    {
                        "source": "semantic_search",
                        "query": keyword,
                        "expected_playlist": KEYWORD_TO_PLAYLIST.get(keyword, ""),
                        "channel": channel_title,
                        "title": item["snippet"]["title"],
                        "description": item["snippet"]["description"],
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
                "comment": build_comment(candidate, best_match),
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
    return diversified


def write_report(proposals):
    os.makedirs(os.path.dirname(SCOUT_FILE), exist_ok=True)
    with open(SCOUT_FILE, "w", encoding="utf-8") as handle:
        handle.write(f"# 🔍 Scouting Competitor & Proposte Commenti ({len(proposals)})\n\n")
        handle.write("> [!IMPORTANT]\n")
        handle.write("> Queste sono solo proposte da approvare o modificare. Nessun commento va pubblicato senza approvazione esplicita.\n\n")
        for index, proposal in enumerate(proposals, 1):
            candidate = proposal["candidate"]
            ours = proposal["ours"]
            handle.write(f"## {index}. Video: [{candidate['title']}]({candidate['url']})\n")
            handle.write(f"**Canale**: {candidate['channel']}\n")
            if candidate.get("query"):
                handle.write(f"**Query di scoperta**: `{candidate['query']}`\n")
            handle.write(f"**Il nostro video correlato**: [{ours['video_title']}]({ours['youtube_url']})\n")
            handle.write(f"**Paper collegato**: {ours['paper_title'] or ours['title_text']}\n")
            handle.write(f"**Area tematica**: {ours['playlist']}\n")
            handle.write(f"**PROPOSTA COMMENTO**:\n> {proposal['comment']}\n\n---\n\n")


def scout_competitors():
    print("🔍 Scouting competitor e video rilevanti...")
    youtube = get_authenticated_service()
    history = set(load_comment_history())
    catalog = build_our_catalog()

    candidates = []
    candidates.extend(search_fixed_channels(youtube, history))
    candidates.extend(search_semantic_keywords(youtube, history))
    candidates = dedupe_candidates(candidates)

    if not candidates:
        print("⚠️ Nessun video candidato idoneo trovato.")
        return

    proposals = rank_proposals(candidates, catalog)
    if not proposals:
        print("⚠️ Nessuna proposta con qualita' sufficiente.")
        return

    write_report(proposals)
    print(f"✅ Proposte salvate in: {SCOUT_FILE}")


if __name__ == "__main__":
    scout_competitors()
