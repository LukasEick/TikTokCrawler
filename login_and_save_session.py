from playwright.sync_api import sync_playwright
import os

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://www.tiktok.com/login")
    print("➡ Bitte einloggen (z. B. mit Telefonnummer)")
    page.wait_for_timeout(20000)

    input("✅ Drücke ENTER nach dem Login...")

    # Versuche zu speichern
    try:
        state_path = os.path.join(os.getcwd(), "state_lukas_eick.json")
        context.storage_state(path=state_path)
        print(f"💾 state_lukas_eick.json gespeichert unter: {state_path}")
    except Exception as e:
        print(f"❌ Fehler beim Speichern: {e}")

    browser.close()
