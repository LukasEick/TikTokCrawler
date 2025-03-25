from playwright.sync_api import sync_playwright
from typing import List
import os

# Speichere state.json direkt im Projektordner
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "state.json")

def login_and_fetch_messages(username: str, password: str) -> List[dict]:
    messages = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])


        # Session laden oder neu starten
        if os.path.exists(STATE_FILE):
            context = browser.new_context(storage_state=STATE_FILE)
            print("✅ Alte Sitzung geladen.")
        else:
            context = browser.new_context()
            print("🆕 Neue Sitzung gestartet.")

        page = context.new_page()
        page.goto("https://www.tiktok.com/messages")
        page.wait_for_timeout(5000)

        if "login" in page.url.lower():
            print("➡ Noch nicht eingeloggt – bitte manuell anmelden.")
            page.goto("https://www.tiktok.com/login")
            page.wait_for_timeout(15000)
            input("🔐 Nach Login ENTER drücken...")

            # Session speichern
            context = browser.new_context(storage_state="state.json")
            print(f"💾 Session gespeichert unter: {STATE_FILE}")

        # Nachrichten lesen
        chat_items = page.query_selector_all('[data-e2e="chat-list-item"]')

        for item in chat_items:
            try:
                text_wrapper = item.query_selector('div[class*="InfoTextWrapper"]')
                if not text_wrapper:
                    print("[WARNUNG] Kein Textblock gefunden – wird übersprungen.")
                    continue

                # Hole alle <p> und <span>-Elemente aus dem Block
                p_tags = text_wrapper.query_selector_all("p")
                span_tags = text_wrapper.query_selector_all("span")

                if len(p_tags) < 1 or len(span_tags) < 2:
                    print("[WARNUNG] Unvollständige Nachricht – wird übersprungen.")
                    continue

                sender = p_tags[0].inner_text()
                content = span_tags[0].inner_text()
                timestamp = span_tags[1].inner_text()

                messages.append({
                    "sender": sender,
                    "content": content,
                    "timestamp": timestamp
                })

            except Exception as e:
                print(f"[WARNUNG] Fehler beim Auslesen: {e}")
                continue

        browser.close()
    return messages
