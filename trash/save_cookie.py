import os  # proxy bypass in mac setting: *.local, 169.254/16
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]

user_agent_rotator = UserAgent(
    software_names=software_names, operating_systems=operating_systems, limit=100
)


# ▶️
async def main():
    rand_user_agent = user_agent_rotator.get_random_user_agent()

    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Mobile/15E148 Safari/604.1"
        )
        await stealth_async(page)

        await page.goto("https://www.reddit.com")
        await page.wait_for_timeout(60000)
        await browser.contexts[0].storage_state(path=f"./rdit_scrp.json")
        print(f"✅")

        await browser.close()


asyncio.run(main())
