from playwright.async_api import async_playwright
import os
import json
from supabase_client import save_tiktok_state
from supabase_client import supabase

async def login_and_fetch_messages(username: str, password: str) -> list:
    username = username.strip().lower().replace(" ", "_")
    messages = []
    state_file = f"state_{username}.json"
    headless_mode = os.path.exists(state_file)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        if headless_mode:
            context = await browser.new_context(storage_state=state_file)
            print(f"✅ Bestehende Session geladen: {state_file}")
        else:
            context = await browser.new_context()
            print("🆕 Neue Session gestartet – manueller Login nötig.")

        page = await context.new_page()
        await page.goto("https://www.tiktok.com/messages", timeout=60000)


        if not headless_mode:
            print("🔐 Bitte manuell einloggen und danach ENTER drücken...")
            input("⏳ Warte auf manuelle Anmeldung...")

        try:
            await page.wait_for_selector('[data-e2e="chat-list-item"]', timeout=15000)  # oder auch 20000 wenn nötig
        except Exception as e:
            print("⚠️ Chat-Liste wurde nicht rechtzeitig gefunden:", e)
            await page.screenshot(path="error_screenshot.png")

        chat_items = await page.query_selector_all('[data-e2e="chat-list-item"]')

        for item in chat_items:
            try:
                text_wrapper = await item.query_selector('div[class*="InfoTextWrapper"]')
                if not text_wrapper:
                    print("[WARNUNG] Element fehlt – wird übersprungen.")
                    continue

                p_tags = await text_wrapper.query_selector_all("p")
                span_tags = await text_wrapper.query_selector_all("span")

                if len(p_tags) < 1 or len(span_tags) < 2:
                    continue

                sender = await p_tags[0].inner_text()
                content = await span_tags[0].inner_text()
                timestamp = await span_tags[1].inner_text()

                messages.append({
                    "sender": sender,
                    "content": content,
                    "timestamp": timestamp
                })

            except Exception as e:
                print("[WARNUNG] Fehler beim Auslesen:", e)
                continue

        # ✅ Session speichern & in Supabase hochladen
        await context.storage_state(path=state_file)
        save_tiktok_state(username, state_file)

        await browser.close()

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
