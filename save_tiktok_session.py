from playwright.sync_api import sync_playwright
import os

# Pfad zur gespeicherten Sitzung
STATE_FILE = os.path.join(os.path.dirname(__file__), "state_lukas_eick.json")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Login-Seite öffnen
    page.goto("https://www.tiktok.com/login")
    print("🔐 Bitte melde dich vollständig bei TikTok an (z. B. mit Telefonnummer)")

    # Gib dir selbst Zeit (z. B. 60 Sekunden), um dich anzumelden
    page.wait_for_timeout(60000)

    # Falls Login erfolgreich, speichern wir die Sitzung
    context.storage_state(path=STATE_FILE)
    print(f"✅ Session gespeichert unter: {STATE_FILE}")

    browser.close()
