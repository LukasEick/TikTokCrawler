from playwright.sync_api import sync_playwright
import os
import json
from supabase_client import save_tiktok_state
from supabase_client import supabase

def login_and_fetch_messages(username: str, password: str) -> list:
    username = username.strip().lower().replace(" ", "_")
    messages = []
    state_file = f"state_{username}.json"
    headless_mode = os.path.exists(state_file)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("🆕 Neue Session gestartet – automatischer Login wird versucht.")
        page.goto("https://www.tiktok.com/login", timeout=60000)

        try:
            # Schritt 1: "Mit Telefon/E-Mail/Benutzername fortfahren" klicken
            page.locator('text=Mit Telefon / E-Mail / Benutzername fortfahren').click()

            # Schritt 2: "E-Mail / Benutzername" klicken
            page.locator('text=E-Mail / Benutzername').click()

            # Schritt 3: Username ausfüllen
            page.locator('input[name="username"]').fill(username)

            # Schritt 4: Passwort ausfüllen
            page.locator('input[name="password"]').fill(password)

            # Schritt 5: Login Button klicken
            page.locator('button:has-text("Einloggen")').click()

            # Warten bis Weiterleitung kommt (Anpassen falls nötig)
            page.wait_for_timeout(5000)

        except Exception as e:
            print(f"⚠️ Fehler beim automatischen Ausfüllen: {e}")
            print("🔐 Bitte manuell einloggen...")

            # Screenshot zur Fehlersuche
            page.screenshot(path="login_error.png")

            # Optional: Mehr Zeit geben
            page.wait_for_timeout(30000)

        # Warten auf Nachrichten-Seite oder ähnliches
        try:
            page.goto("https://www.tiktok.com/messages", timeout=60000)
            page.wait_for_selector('[data-e2e="chat-list-item"]', timeout=15000)
        except Exception as e:
            print(f"⚠️ Fehler beim Laden der Nachrichten-Seite: {e}")
            page.screenshot(path="messages_error.png")

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
                timestamp = span_tags[1].inner_text()

                messages.append({
                    "sender": sender,
                    "content": content,
                    "timestamp": timestamp
                })

            except Exception as e:
                print("[WARNUNG] Fehler beim Auslesen:", e)
                continue

        # ✅ Session speichern & in Supabase hochladen
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
