
import json
import urllib.request
from getpass import getpass

token = input("Вставь новый токен: ").strip()

url = f"https://api.telegram.org/bot{token}/getUpdates"

try:
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read())

    if not data["ok"]:
        print("Ошибка:", data)
    else:
        found = False
        for update in data["result"]:
            post = update.get("channel_post")
            if post:
                chat = post["chat"]
                print("Название канала:", chat.get("title"))
                print("ID канала:", chat["id"])
                found = True

        if not found:
            print("Сообщений канала пока не найдено.")
except Exception as e:
    print("Ошибка подключения:", e)
