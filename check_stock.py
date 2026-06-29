from playwright.sync_api import sync_playwright
import requests

# ==========================
# CONFIGURATION
# ==========================

BOT_TOKEN = "8816952930:AAGsO__i8ONwDPRmIbm0jXl7BYTWy92pUx8"
CHAT_ID = "907538806"

PRODUCT_URL = "https://www.hmtwatches.store/product/b8fbabdb-a49d-4e5d-92c6-71eda34c9382"


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message
        }
    )


with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(PRODUCT_URL, wait_until="networkidle")

    html = page.content()

    title = page.title()

    print(title)

    if "Out of Stock" in html:
        print("❌ OUT OF STOCK")

    elif "Add to Cart" in html:

        print("🎉 IN STOCK")

        send_telegram(
            f"""🚨 HMT STOCK ALERT 🚨

{title}

Available Now!

{PRODUCT_URL}
"""
        )

    else:

        print("⚠ Unable to determine stock status.")

    browser.close()