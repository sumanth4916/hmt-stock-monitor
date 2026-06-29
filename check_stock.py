from playwright.sync_api import sync_playwright
import requests
import os
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

PRODUCT_URL = "https://www.hmtwatches.store/product/b8fbabdb-a49d-4e5d-92c6-71eda34c9382"


def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": msg
        },
        timeout=30
    )


def check_stock():

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )

        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )

        page.goto(
            PRODUCT_URL,
            wait_until="domcontentloaded",
            timeout=60000
        )

        page.wait_for_timeout(5000)

        html = page.content()

        title = page.title()

        print("TITLE:", title)

        browser.close()

        if "The request could not be satisfied" in html:
            return "BLOCKED"

        if "Out of Stock" in html:
            return "OUT"

        if "Add to Cart" in html:
            return "IN"

        return "UNKNOWN"


for attempt in range(3):

    print(f"Attempt {attempt + 1}")

    try:

        result = check_stock()

        print("STATUS:", result)

        if result == "OUT":
            print("Watch is still out of stock.")
            break

        elif result == "IN":

            send(
f"""🚨 HMT STOCK ALERT 🚨

The HMT Stellar DASS 04 is AVAILABLE!

{PRODUCT_URL}
"""
            )

            print("Telegram notification sent.")
            break

        elif result == "BLOCKED":

            print("CloudFront blocked this request. Retrying...")
            time.sleep(10)

        else:

            print("Unknown page state.")
            time.sleep(5)

    except Exception as e:

        print("ERROR:", e)
        time.sleep(10)

print("Finished.")