#!/bin/bash
# Spostamento delle copertine finali nelle cartelle locali di Cleaned

BASE_PATH="/Users/marcolemoglie_1_2/.gemini/antigravity/brain/ce80e41e-a34f-4bf0-a896-fc7ebc3680ee"
CLEANED_PATH="/Users/marcolemoglie_1_2/Desktop/canale/Cleaned"

cp "$BASE_PATH/mafia_inc_thumbnail_1773327600074.png" "$CLEANED_PATH/Pinotti_2015/thumbnail.png"
cp "$BASE_PATH/tagliare_aiuti_thumbnail_1773327614560.png" "$CLEANED_PATH/Le_Moglie_Sorrenti_2021/thumbnail.png"
cp "$BASE_PATH/cicala_formica_thumbnail_1773327629495.png" "$CLEANED_PATH/La_Cicala_e_la_Formica/thumbnail.png"
cp "$BASE_PATH/archeologia_economica_thumbnail_1773327644739.png" "$CLEANED_PATH/Le_Città_Perdute_del_Bronzo/thumbnail.png"
cp "$BASE_PATH/stato_crimine_final_thumbnail_1773328916907.png" "$CLEANED_PATH/Sulle_Origini_dello_Stato_JPE_2020/thumbnail.png"
cp "$BASE_PATH/nomi_discriminazione_thumbnail_1773327700997.png" "$CLEANED_PATH/Discriminazione_per_nome_Bertrand_Mullainathan_2004/thumbnail.png"
cp "$BASE_PATH/eco_terremoto_thumbnail_1773327728854.png" "$CLEANED_PATH/Ondate_Sociali/thumbnail.png"
cp "$BASE_PATH/clientelismo_politico_refined_thumbnail_1773328498987.png" "$CLEANED_PATH/Clientelismo_Politico_AER2020/thumbnail.png"
cp "$BASE_PATH/mogano_insanguinato_thumbnail_1773327758479.png" "$CLEANED_PATH/Mogano_insanguinato_il_prezzo_di_una_legge/thumbnail.png"
cp "$BASE_PATH/istituzioni_sviluppo_refined_thumbnail_1773328512911.png" "$CLEANED_PATH/Istituzioni_sviluppo_economico_Michalopoulous_Papaioannou_qje2014/thumbnail.png"

echo "File organizzati con successo."
