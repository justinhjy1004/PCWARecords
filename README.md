# PCWARecords

for f in *.zip; do [ ! -d "${f%.zip}" ] && unzip "$f" -d "${f%.zip}"; done
