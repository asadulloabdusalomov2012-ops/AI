

import os
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.environ.get("API_ID", input("Enter your API_ID: ")))
API_HASH = os.environ.get("API_HASH") or input("Enter your API_HASH: ")

with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    session_string = client.session.save()
    print("\n--- YOUR STRING SESSION BELOW ---")
    print(session_string)
    print("--- Copy this into Railway's TELEGRAM_SESSION variable ---\n")
