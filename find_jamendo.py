
import json
import csv
import urllib.parse
import urllib.request
import time

CLIENT_ID = "709fa152"
API = "https://api.jamendo.com/v3.0/tracks/"

with open("tracks.txt", encoding="utf-8-sig") as file:
    lines = [
        line.strip() for line in file
        if line.strip() and " - " in line
        and not line.startswith(("Плейлист:", "Владелец:", "Треков:"))
    ][:20]

results = []

for number, track in enumerate(lines, 1):
    artist, title = track.rsplit(" - ", 1)

    params = {
        "client_id": CLIENT_ID,
        "format": "json",
        "limit": 5,
        "search": f"{artist} {title}",
        "include": "licenses"
    }

    url = API + "?" + urllib.parse.urlencode(params)

    print(f"\n[{number}/20] {artist} — {title}")

    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "MusicArchiveResearch/1.0"}
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))

        if data.get("headers", {}).get("status") != "success":
            print("Ошибка API:", data.get("headers"))
            continue

        tracks = data.get("results", [])

        if not tracks:
            print("Совпадений нет")

        for item in tracks:
            license_info = item.get("license_ccurl", "")

            row = {
                "original_track": track,
                "found_artist": item.get("artist_name", ""),
                "found_title": item.get("name", ""),
                "license": license_info,
                "download_allowed": item.get("audiodownload_allowed", False),
                "download_url": item.get("audiodownload", ""),
                "jamendo_url": item.get("shareurl", "")
            }

            results.append(row)

            print("  Исполнитель:", row["found_artist"])
            print("  Название:", row["found_title"])
            print("  Лицензия:", row["license"] or "не указана")
            print("  Скачивание разрешено:", row["download_allowed"])

    except Exception as error:
        print("Ошибка:", error)

    time.sleep(1)

with open(
    "jamendo_results_20.csv",
    "w",
    newline="",
    encoding="utf-8-sig"
) as file:
    fields = [
        "original_track", "found_artist", "found_title",
        "license", "download_allowed", "download_url", "jamendo_url"
    ]

    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()
    writer.writerows(results)

print("\nПоиск завершён.")
print("Найдено кандидатов:", len(results))
print("Файл: jamendo_results_20.csv")
