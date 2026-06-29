from playwright.sync_api import sync_playwright
import requests
import os
import sys

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


try:
    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        page.goto(PRODUCT_URL, timeout=60000)

        page.wait_for_timeout(5000)

        html = page.content()

        title = page.title()

        print(title)

        if "The request could not be satisfied" in html:
            print("CloudFront blocked request")
            sys.exit(1)

        if "Out of Stock" in html:
            print("OUT OF STOCK")

        elif "Add to Cart" in html:
            print("IN STOCK")

            send(
f"""🚨 HMT STOCK ALERT 🚨

{title}

{PRODUCT_URL}
"""
            )

        else:
            print("UNKNOWN STATUS")

        browser.close()

except Exception as e:
    print(e)
    sys.exit(1)