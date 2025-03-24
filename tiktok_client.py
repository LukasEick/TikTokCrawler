from playwright.sync_api import sync_playwright
from typing import List
import time

def login_and_fetch_messages(username: str, password: str) -> List[dict]:
    messages = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("https://www.tiktok.com/login")
        page.wait_for_timeout(2000)

        # Simulierter Login (musst du ggf. anpassen)
        page.fill("input[name='username']", username)
        page.fill("input[name='password']", password)
        page.click("button[type='submit']")
        page.wait_for_timeout(5000)

        page.goto("https://www.tiktok.com/messages")
        page.wait_for_timeout(3000)

        # Hier müsste basierend auf DOM angepasst werden
        message_elements = page.query_selector_all(".message-class-placeholder")
        for element in message_elements:
            sender = element.query_selector(".sender").inner_text()
            content = element.query_selector(".message").inner_text()
            timestamp = element.query_selector(".timestamp").inner_text()
            messages.append({
                "sender": sender,
                "content": content,
                "timestamp": timestamp
            })

        browser.close()
    return messages
