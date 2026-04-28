import os
import pickle
import json
from googleapiclient.discovery import build

def get_authenticated_service():
    token_path = '/Users/marcolemoglie_1_2/Desktop/canale/Execution/credentials/token_youtube.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    return build('youtube', 'v3', credentials=creds)

def clean_description(desc_text):
    if not desc_text:
        return ""
    
    lines = desc_text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        l_lower = line.lower().strip()
        stop_markers = ["⏰", "iscriviti", "http", "►►", "▬▬▬▬", "indice contenuti", "fonte"]
        
        if any(marker in l_lower for marker in stop_markers):
            break
            
        if line.strip():
             cleaned_lines.append(line)
             
    return " ".join(cleaned_lines).strip()

def run():
    print("Connessione a Youtube API...")
    youtube = get_authenticated_service()
    
    # Get uploads playlist ID
    channels_response = youtube.channels().list(
        mine=True,
        part="contentDetails"
    ).execute()
    
    uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    print("Recupero video in corso...")
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=uploads_playlist_id,
        maxResults=50
    )
    response = request.execute()

    links_dict = {
        "yrcTPiEV_58": "https://www.youtube.com/watch?v=yrcTPiEV_58", # Ascesa del Male
        "7SeVerAABeg": "https://www.youtube.com/watch?v=7SeVerAABeg", # Ricchi di oggi
        "Tv4znJpN_tk": "https://www.youtube.com/watch?v=Tv4znJpN_tk", # Città pericolose
        "LIgZxg-CMWY": "https://www.youtube.com/watch?v=LIgZxg-CMWY", # Lato oscuro della tv
        "S0ZyZE65BgM": "https://www.youtube.com/watch?v=S0ZyZE65BgM", # Robot rurbano
        "wi8TmC6WRRo": "https://www.youtube.com/watch?v=wi8TmC6WRRo", # Mafia e sviluppo
        "Fa27rfGRweY": "https://www.youtube.com/watch?v=Fa27rfGRweY", # Corruzione ladri
        "hSj0RytzsJQ": "https://www.youtube.com/watch?v=hSj0RytzsJQ", # Mafia inc
        "Rcjwqblw9aI": "https://www.youtube.com/watch?v=Rcjwqblw9aI", # Tagliare aiuti
        "06TeI4ehwBw": "https://www.youtube.com/watch?v=06TeI4ehwBw", # Cicala formica
        "OfLZjHHVhuI": "https://www.youtube.com/watch?v=OfLZjHHVhuI", # Archeologia economica
        "K1mbkAwVfNI": "https://www.youtube.com/watch?v=K1mbkAwVfNI", # due banditi
        "85M2SSwB3V8": "https://www.youtube.com/watch?v=85M2SSwB3V8", # nomi e discrim
        "mkOByDD32Q4": "https://www.youtube.com/watch?v=mkOByDD32Q4", # terremoto
        "BEZV_qvJ3C0": "https://www.youtube.com/watch?v=BEZV_qvJ3C0", # clientelismo
        "sDG-9Olw7Lg": "https://www.youtube.com/watch?v=sDG-9Olw7Lg", # mogano
        "zAwp-Sswzdw": "https://www.youtube.com/watch?v=zAwp-Sswzdw"  # istituzioni
    }

    output_lines = ["=== TESTI CORRETTI DA COPIARE PER FACEBOOK ===\n\n"]
    output_lines.append("NOTA: Le descrizioni ora sono estratte in tempo reale da YouTube e pulite\nda tutti i link spazzatura e indici contenuti.\n\n")

    count = 0
    for item in response.get('items', []):
        snippet = item['snippet']
        v_id = snippet['resourceId']['videoId']
        title = snippet['title']
        full_desc = snippet['description']
        
        cleaned = clean_description(full_desc)
        link = links_dict.get(v_id, f"https://www.youtube.com/watch?v={v_id}")
        
        output_lines.append(f"--- FOTO: {title} ---\n")
        output_lines.append(f"{cleaned}\n\n")
        output_lines.append(f"Link al video: {link}\n")
        output_lines.append("---------------------------------------------------------------------------------\n\n")
        count += 1

    out_path = "/Users/marcolemoglie_1_2/Desktop/TESTI_FACEBOOK_DA_COPIARE.txt"
    with open(out_path, "w", encoding='utf-8') as f:
        f.writelines(output_lines)
        
    print(f"File generato con successo su Desktop ({count} video).")

if __name__ == "__main__":
    run()
