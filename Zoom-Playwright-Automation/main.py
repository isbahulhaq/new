# Zoom Automation using Brave + Playwright

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
import nest_asyncio
import random
from playwright.async_api import async_playwright

nest_asyncio.apply()

MUTEX = threading.Lock()
BRAVE_PATH = "/usr/bin/brave-browser"


def generate_name():
    first = ["Arjun", "Rohan", "Rahul", "Aman", "Imran", "Sahil", "Kabir", "Farhan"]
    last = ["Kumar", "Sharma", "Verma", "Ansari", "Ali", "Khan", "Singh", "Yadav"]
    return random.choice(first) + " " + random.choice(last)


def sync_print(text):
    with MUTEX:
        print(text)


async def start(name_id, username, wait_time, meetingcode, passcode):
    sync_print(f"{name_id} started!")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            executable_path=BRAVE_PATH,
            args=[
                "--use-fake-device-for-media-stream",
                "--use-fake-ui-for-media-stream",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )

        context = await browser.new_context(permissions=["microphone"])
        page = await context.new_page()

        await page.goto(f"https://zoom.us/wc/join/{meetingcode}", timeout=200000)

        try:
            await page.click("#onetrust-accept-btn-handler", timeout=5000)
        except:
            pass

        try:
            await page.click("#wc_agree1", timeout=50000)
        except:
            pass

        await page.wait_for_selector('input[type="text"]', timeout=200000)
        await page.fill('input[type="text"]', username)
        await page.fill('input[type="password"]', passcode)

        join_button = await page.wait_for_selector('button.preview-join-button')
        await join_button.click()

        try:
            mic_button = await page.wait_for_selector('button:text(\"Join Audio by Computer\")', timeout=200000)
            await mic_button.click()
            sync_print(f"{name_id} mic aayenge.")
        except Exception as e:
            sync_print(f"{name_id} mic nahi aayenge: {str(e)}")

        sync_print(f"{name_id} sleeping for {wait_time} seconds ...")
        await asyncio.sleep(wait_time)
        sync_print(f"{name_id} ended!")

        await browser.close()


async def main():
    number = int(input("Enter number of Users: "))
    meetingcode = input("Enter meeting code (No Space): ")
    passcode = input("Enter Password (No Space): ")

    sec = 90
    wait_time = sec * 60

    with ThreadPoolExecutor(max_workers=number) as executor:
        loop = asyncio.get_event_loop()
        tasks = []

        for i in range(number):
            username = generate_name()
            task = loop.create_task(start(f"[Thread{i}]", username, wait_time, meetingcode, passcode))
            tasks.append(task)

        await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
