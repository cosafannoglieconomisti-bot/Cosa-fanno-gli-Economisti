
import json

shorts_data = [
    ("DSucrUBXJws", "gzk8eMmJVfs", "L'aratro ha creato il patriarcato? 🚜", "Lo sapevi che la disuguaglianza di genere ha radici profonde nell'agricoltura antica? Scoprilo in questo video."),
    ("TE2601I7Y1c", "BFW6hmE5WiQ", "Dio blocca la democrazia? ⛪️🗳️", "Può un terremoto fermare la democrazia? Lo studio svela come i disastri naturali abbiano rallentato la nascita dei comuni."),
    ("TkBdxKizXBw", "mnhpTOSPmig", "I prof sono davvero razzisti? 🏫", "Un esperimento shock rivela i pregiudizi nascosti nelle nostre scuole."),
    ("U3GRvQR612Q", "62iBwcGX1TU", "Il comunismo ti cambia la mente?", "Cosa succede alla psicologia di chi vive sotto un regime autoritario?"),
    ("D-j41dR110M", "vPkL50z6lgQ", "Meno carceri, più sicurezza? 🚔", "Perché regolarizzare gli immigrati riduce i reati meglio della prigione."),
    ("1qdybzlRfCc", "-7p7vUYoYtE", "Perché i giornali spariscono? 📰", "La verità economica dietro la crisi delle edicole e dell'informazione."),
    ("rcHDZvJ91Pg", "WfXcr8ocXYo", "Stadi vuoti, meno razzismo? ⚽", "Cosa è successo negli stadi durante la pandemia? Un esperimento naturale."),
    ("6VVXlgYa7jo", "wFKvwckvMHI", "Perché l'Africa non si fida? 🌍", "L'eredità drammatica della tratta degli schiavi sulla fiducia oggi."),
    ("Og-odPugBgQ", "kdFA7y9TGYo", "Il costo dell'aborto negato 🏥", "Le conseguenze economiche e sociali devastanti per chi non può scegliere."),
    ("PR3IQI-eybg", "8b19n79qxXo", "Il petrolio causa le guerre? 🛢️", "Tutti pensano di sì, ma la scienza cosa dice davvero? Ecco i dati."),
    ("-YELM0HZQ40", "QcRPngnWScQ", "Figli o Pensione: il dilemma 👵", "Perché in Italia fare figli è diventato un calcolo economico impossibile."),
    ("_g_BKiot5_0", "KyA_Pu8BPhE", "Chiesa vs Integrazione ⛪", "Come la Chiesa ha influenzato l'accoglienza degli immigrati a fine '800."),
    ("_D02ygxnHGk", "9zwAeofGwKE", "La Mafia al Nord: come avviene? 📈", "Non solo Sud: ecco come il crimine organizzato colonizza l'economia ricca."),
    ("16GHafTZ5-4", "vPkL50z6lgQ", "Regolarizzare riduce il crimine", "Lo status legale è la chiave per la sicurezza urbana. Ecco perché."),
    ("M_4e4I_ql8U", "HamA2uwPAGU", "Perché l'Italia non cresce? 📉", "Il mistero della produttività italiana risolto da questo studio shock."),
    ("GdFZMvtHLbo", "CkMiVsvnP0U", "Talento e Genere nelle Orchestre", "Le audizioni 'al buio' hanno cambiato la storia della musica classica."),
    ("-LJwjNCwqbc", "y4zWdljXoPY", "Il calcio può fermare le guerre?", "Il potere incredibile dello sport nel ridurre i conflitti civili."),
    ("k4qDIQIPtBo", "9zwAeofGwKE", "Sciascia aveva ragione? 🖋️", "L'intuizione dello scrittore sulla 'linea della palma' e la Mafia al Nord."),
    ("pgAn6mnOoxA", "HDMbeJ9ITc0", "Trump aumenta il razzismo? 🚔", "Uno studio analizza l'effetto della retorica politica sui crimini d'odio."),
    ("J3Vj4cAL4cE", "Fa27rfGRweY", "La corruzione è contagiosa? ☣️", "Perché vedere gli altri rubare ci rende più propensi a farlo anche noi."),
    ("Hi5IYPlJmkY", "lNN7bgKDe70", "Dai Narcos al Petrolio 🛢️", "Perché i cartelli della droga ora rubano greggio? Business e violenza."),
    ("jxrA4RvsaPc", "7sNESUojy0w", "Folklore e Ricchezza 📜", "Le storie che leggiamo ai bambini influenzano l'economia del futuro?"),
    ("SpgBjx6hiH4", "69QiFXrPghY", "Socialismo e Fascismo: il legame", "Le radici storiche inaspettate del regime che ha segnato l'Italia."),
    ("2soQGo7N-_k", "LIgZxg-CMWY", "La TV ha manipolato il voto? 🗳️", "L'effetto Mediaset sulla politica italiana analizzato dagli economisti."),
    ("eO0DCsYr6PA", "N4LxEfdrzUw", "Germania vs Grecia: l'odio 🇪🇺", "Dalle crisi del debito ai boicottaggi: l'ombra del passato non scompare."),
    ("RCcIxMaYmIw", "tnVy81nzx5s", "Stato Assente, Mafia Presente", "Dove lo Stato non arriva, il crimine prospera. Ecco come è iniziato."),
    ("RCfHNwxZYv4", "7SeVerAABeg", "Ricchi dal 1400: il caso Firenze", "Incredibile: le famiglie più ricche oggi sono le stesse del Rinascimento."),
    ("O7SpDhbLKZo", "mgl1pjzW8Uc", "La Peste Nera ha creato l'Europa?", "Come una tragedia globale ha gettato le basi per lo sviluppo moderno."),
    ("U_ZEqCF-wbw", "TKw-6Jm7C9g", "Hitler e le Grandi Aziende 🏭", "Chi ha finanziato l'ascesa del male? Un'analisi economica inquietante."),
    ("tGEsjsvVGiM", "S0ZyZE65BgM", "I Robot ci rubano il lavoro? 🤖", "Cosa dicono davvero i dati sull'automazione e l'occupazione oggi.")
]

final_list = []
for sid, lid, title, hook in shorts_data:
    desc = f"{hook}\n\nVideo completo qui: https://youtu.be/{lid}\n\n#shorts #economia #ricerca #scienza"
    final_list.append({
        "id": sid,
        "title": title,
        "description": desc
    })

with open('/Users/marcolemoglie_1_2/Desktop/canale/Temp/romolo/shorts_list.json', 'w') as f:
    json.dump(final_list, f, indent=4)
