#!/usr/bin/python3
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

# 📹 vids
vids_path = "./media/vids"
vids = os.listdir(vids_path)
if ".DS_Store" in vids:
    vids.remove(".DS_Store")


# handles
async def block_media(route, req):
    if req.resource_type in {"image", "media", "font", "stylesheet"}:
        try:
            await route.abort()
        except:
            pass


async def get_user_id(res):
    try:
        body = await res.body()
        decoded_body = eval(body)
        if "user_id" in decoded_body["data"]:
            global id
            id = decoded_body["data"]["user_id"]
    except:
        pass


print(f"{states_path} & {vids_path}")


# ▶️
async def main():
    i = 0
    states_len = len(states)

    async with async_playwright() as p:
        for state in states:
            i = i + 1

            state = state.replace(".json", "")

            browser = await p.chromium.launch(headless=head)

            await browser.new_context(
                storage_state=f"./{states_path}/{state}.json",
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Mobile/15E148 Safari/604.1",
            )
            # await browser.contexts[0].route("**/*", block_media)
            page = await browser.contexts[0].new_page()
            await stealth_async(page)

            # get user id (if logged)
            page.on("response", lambda res: get_user_id(res))
            await page.goto("about:blank")
            await page.goto(
                f"https://www.tiktok.com/messages/?lang=en", wait_until="load"
            )
            await page.reload(wait_until="load")

            if id != False:
                for vid in vids:
                    # print(vid)

                    page.on(
                        "filechooser",
                        lambda file_chooser: file_chooser.set_files(
                            f"{vids_path}/{vid}"
                        ),
                    )
                    await page.goto(
                        "https://www.tiktok.com/upload?lang=en", wait_until="load"
                    )

                    await page.frame_locator("iframe").locator(
                        ".file-select-button"
                    ).click()
                    await page.frame_locator("iframe").locator(
                        ".change-video-btn"
                    ).click()
                    # await page.frame_locator("iframe").locator(".hash").click()
                    await page.frame_locator("iframe").locator(".btn-post").click()
                    await page.frame_locator("iframe").locator(
                        ".modal-title-container"
                    ).click()
                    await page.click("text=Post", timeout=2000)
                    await page.wait_for_timeout(1000)

                    # delete video
                    os.remove(f"{vids_path}/{vid}")

                # save new cookie
                await browser.contexts[0].storage_state(
                    path=f"{states_path}/{state}.json"
                )
                # save
                print(f"[{i}/{states_len}] {state} 📹✅")

            else:
                print(f"[{i}/{states_len}] {state} ❌")

            await page.close()
            await browser.close()


asyncio.run(main())
