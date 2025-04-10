from playwright.sync_api import sync_playwright
import os
import json
import time
from supabase_client import save_tiktok_state, supabase


def login_and_fetch_messages(username: str, password: str) -> list:
    username = username.strip().lower().replace(" ", "_")
    messages = []
    state_file = f"state_{username}.json"
    headless_mode = os.path.exists(state_file)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # ✅ Session Wiederverwendung
        if headless_mode:
            context = browser.new_context(storage_state=state_file)
            print(f"✅ Bestehende Session geladen: {state_file}")
        else:
            context = browser.new_context()
            print("🆕 Neue Session gestartet – automatischer Login wird versucht.")

        page = context.new_page()

        if not headless_mode:
            try:
                # 🔐 TikTok Login Seite öffnen
                page.goto("https://www.tiktok.com/login", timeout=60000)

                # Login Methode auswählen
                page.locator('text=Mit Telefon / E-Mail / Benutzername fortfahren').click(timeout=10000)
                page.locator('text=E-Mail / Benutzername').click(timeout=10000)

                # Login-Daten ausfüllen
                page.locator('input[name="username"]').fill(username)
                page.locator('input[name="password"]').fill(password)

                # Login-Button klicken
                page.locator('button:has-text("Einloggen")').click()

                # Warte kurz, bis TikTok reagiert
                page.wait_for_timeout(5000)

            except Exception as e:
                print(f"⚠️ Fehler beim automatischen Login: {e}")
                timestamp = int(time.time())
                page.screenshot(path=f"login_error_{timestamp}.png")
                print("🔐 Bitte manuell einloggen...")
                page.wait_for_timeout(30000)  # Optional mehr Zeit

        # ✅ Nachrichten abrufen
        try:
            page.goto("https://www.tiktok.com/messages", timeout=60000)
            page.wait_for_selector('[data-e2e="chat-list-item"]', timeout=15000)
        except Exception as e:
            print(f"⚠️ Fehler beim Laden der Nachrichten-Seite: {e}")
            timestamp = int(time.time())
            page.screenshot(path=f"messages_error_{timestamp}.png")

        chat_items = page.query_selector_all('[data-e2e="chat-list-item"]')

        for item in chat_items:
            try:
                text_wrapper = item.query_selector('div[class*="InfoTextWrapper"]')
                if not text_wrapper:
                    continue

                p_tags = text_wrapper.query_selector_all("p")
                span_tags = text_wrapper.query_selector_all("span")

                if len(p_tags) < 1 or len(span_tags) < 2:
                    continue

                sender = p_tags[0].inner_text()
                content = span_tags[0].inner_text()
                timestamp_msg = span_tags[1].inner_text()

                messages.append({
                    "sender": sender,
                    "content": content,
                    "timestamp": timestamp_msg
                })

            except Exception as e:
                print("[WARNUNG] Fehler beim Auslesen einer Nachricht:", e)
                continue

        # ✅ Session speichern & Supabase aktualisieren
        context.storage_state(path=state_file)
        save_tiktok_state(username, state_file)

        browser.close()

    return messages


def load_tiktok_state(username: str) -> bool:
    try:
        result = supabase.table("tiktok_sessions").select("state_json").eq("username", username).execute()
        data = result.data
        if data and len(data) > 0:
            with open(f"state_{username}.json", "w") as f:
                json.dump(data[0]["state_json"], f)
            return True
    except Exception as e:
        print("❌ Fehler beim Laden der TikTok-Session:", e)
    return False
