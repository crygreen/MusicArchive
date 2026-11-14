import csv
import webbrowser
import time

with open("soundcloud_links.csv", encoding="utf-8-sig") as f:
    tracks = list(csv.DictReader(f))

print("Будем открывать поиск по одному треку.")
print("Enter — следующий, q — остановить.")

for i, track in enumerate(tracks, 1):
    print(f"\n[{i}/{len(tracks)}] {track['Трек']}")
    webbrowser.open(track["Поиск SoundCloud"])

    command = input("Enter — далее: ")

    if command.lower() == "q":
        break

print("Поиск завершён.")