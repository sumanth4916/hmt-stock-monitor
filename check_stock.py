import json
import os
import time

from playwright.sync_api import sync_playwright

from telegram_utils import send

PRODUCTS = [
    {
        "name": "HMT Stellar DASS 04 Blue",
        "url": "https://www.hmtwatches.store/product/b8fbabdb-a49d-4e5d-92c6-71eda34c9382"
    }
]

STATE_FILE = "state.json"


def load_state():
    if not os.path.exists(STATE_FILE):
        return {}

    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)


def check_product(browser, product):

    page = browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        viewport={"width": 1366, "height": 768},
    )

    page.goto(
        product["url"],
        wait_until="domcontentloaded",
        timeout=60000,
    )

    page.wait_for_timeout(5000)

    html = page.content()

    page.close()

    if "The request could not be satisfied" in html:
        return "BLOCKED"

    if "Out of Stock" in html:
        return "OUT"

    if "Add to Cart" in html:
        return "IN"

    return "UNKNOWN"


def main():

    state = load_state()

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        for product in PRODUCTS:

            print("=" * 60)
            print(product["name"])

            result = None

            for attempt in range(3):

                print(f"Attempt {attempt + 1}")

                try:

                    result = check_product(browser, product)

                    print("STATUS:", result)

                    if result != "BLOCKED":
                        break

                    time.sleep(10)

                except Exception as e:

                    print(e)
                    time.sleep(10)

            previous = state.get(product["name"], "OUT")

            if result == "IN":

                if previous != "IN":

                    print("NEW STOCK FOUND")

                    send(
f"""🚨 HMT STOCK ALERT 🚨

{product['name']}

Available Now!

{product['url']}
"""
                    )

                    state[product["name"]] = "IN"

                else:

                    print("Already notified")

            elif result == "OUT":

                print("Still Out of Stock")

                state[product["name"]] = "OUT"

            elif result == "BLOCKED":

                print("CloudFront blocked after retries")

            else:

                print("Unknown page state")

        browser.close()

    save_state(state)


if __name__ == "__main__":
    main()