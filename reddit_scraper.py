import json
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

head = False


# handles
async def block_media(route, req):
    if req.resource_type in {"image", "media", "font", "stylesheet", "css"}:
        try:
            await route.abort()
        except:
            pass


# selectors
url_hour = "https://www.reddit.com/r/AskReddit/top/?t=hour"
url_day = "https://www.reddit.com/r/AskReddit/top/?t=day"

post_selector = 'div[class*="Post"]'
post_txt_selector = 'div[data-adclicklocation="title"]'

comment_selector = 'div[class*="Comment"]'
comment_txt_selector = 'div[data-testid="comment"]'


async def main():
    async with async_playwright() as p:

        async def a_1():
            browser = await p.chromium.launch(
                headless=head,
            )
            page = await browser.new_page()
            await stealth_async(page)
            await page.set_viewport_size({"width": 700, "height": 700})
            await page.emulate_media(color_scheme="dark")

            # 🕹  🕹🕹 STARTrrtrtrt t 🕹🕹
            await page.goto(url_hour, wait_until="load")
            post = await page.wait_for_selector(post_selector)
            post_url = page.url
            # page loaded

            # toggle dark mode
            try:
                await page.click('div[class="header-user-dropdown"]', timeout=1000)
                await page.click('i[class*="icon-night"]', timeout=1000)

            except:
                pass

            # get top post's inner text
            post_txt = await page.wait_for_selector(post_txt_selector)
            post_txt = await post_txt.inner_text()

            # get top posts's screen shot
            post_img_path = "./media/post/post.png"
            await post.screenshot(path=post_img_path)

            # go to comments
            await post.click()
            await page.wait_for_load_state("networkidle")

            await page.wait_for_selector(comment_selector)
            await page.wait_for_selector(comment_txt_selector)
            # comments loaded

            # post blocks and images should sync by order
            comment_blocks = await page.query_selector_all(comment_selector)
            comment_txts = await page.query_selector_all(comment_txt_selector)

            comments = []
            comments_img_path = "./media/post/comments"

            # loop over txt's & screenshot block w same index
            for index, comment_txt in enumerate(comment_txts):
                if index < 5:
                    path = f"{comments_img_path}/{index}/comment.png"
                    speach_path = f"{comments_img_path}/{index}/comment_speach.aiff"

                    await comment_blocks[index].scroll_into_view_if_needed(timeout=1000)
                    await comment_blocks[index].screenshot(path=path)
                    txt = await comment_txt.inner_text()

                    # append to comments array
                    comment = {
                        "comment_txt": txt,
                        "comment_img": path,
                        "comment_speach": speach_path,
                    }
                    comments.append(comment)

            # post.json construction
            post_json = {
                "post_url": post_url,
                "post_txt": post_txt,
                "post_img": post_img_path,
                "post_speach": "./media/post/post_speach.aiff",
                "comments": comments,
            }

            # save post.json
            with open("./media/post/post.json", "w") as outfile:
                json.dump(post_json, outfile)

            await page.close()
            await browser.close()

        await a_1()


asyncio.run(main())
