from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import asyncio
import os
import random


head = False

# 👤 states
states_path = "./cookies/tiktok"
states = os.listdir(states_path)
if ".DS_Store" in states:
    states.remove(".DS_Store")


# handles
async def block_media(route, req):
    if req.resource_type in {"image", "media", "font", "stylesheet"}:
        try:
            await route.abort()
        except:
            pass


# ▶️
async def main():
    i = 0
    states_len = len(states)

    async with async_playwright() as p:
        for state in states:

            state = state.replace(".json", "")

            browser = await p.chromium.launch(headless=head)

            await browser.new_context(
                storage_state=f"./{states_path}/{state}.json",
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Mobile/15E148 Safari/604.1",
            )
            # await browser.contexts[0].route("**/*", block_media)
            page = await browser.contexts[0].new_page()
            await stealth_async(page)

            await page.goto(
                f"https://www.tiktok.com/messages/?lang=en", wait_until="load"
            )

            # save
            await browser.contexts[0].storage_state(path=f"{states_path}/{state}.json")

            await page.close()
            await browser.close()


asyncio.run(main())
