import csv
from urllib.parse import quote

with open("tracks.txt", "r", encoding="utf-8") as f:
    tracks = [
        line.strip()
        for line in f
        if " - " in line or " — " in line
    ][:20]

with open("soundcloud_links.csv", "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Трек", "Поиск SoundCloud"])

    for track in tracks:
        url = "https://soundcloud.com/search?q=" + quote(track)
        writer.writerow([track, url])

print(f"Готово. Ссылок создано: {len(tracks)}")
print("Файл: soundcloud_links.csv")