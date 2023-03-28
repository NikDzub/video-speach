import json
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import sys
import random
import re

head = False

# args
name_of_script = sys.argv[0]
n_comments = sys.argv[1]


# handles
async def block_media(route, req):
    if req.resource_type in {"image", "media", "font", "stylesheet", "css"}:
        try:
            await route.abort()
        except:
            pass


# history
history_json = open("./etc/reddit_history.json", encoding="utf-8")
history = json.load(history_json)

# urls
urls = [
    "https://www.reddit.com/r/AskReddit/top/?t=hour",
    "https://www.reddit.com/r/AskReddit/top/?t=day",
    "https://www.reddit.com/r/Funnymemes/top/?t=day",
    "https://www.reddit.com/r/funny/top/?t=day",
    "https://www.reddit.com/r/selfimprovement/top/?t=day",
    "https://www.reddit.com/r/malementalhealth/top/?t=day",
    "https://www.reddit.com/r/Tinder/top/?t=day",
]

# selectors :
# /r/*
post_home_selector = 'div[class*="Post"]'
# /r/*/comments/*
post_selector = 'div[data-testid*="post-container"]'
post_title_selector = 'div[data-adclicklocation="title"]'
post_txt_selector = 'div[data-click-id="text"]'  # optional

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

            await page.goto(random.choice(urls), wait_until="networkidle")
            post_home = await page.wait_for_selector(post_home_selector)
            print("/r/* loaded")
            # /r/* loaded

            # toggle dark mode
            try:
                await page.click('div[class="header-user-dropdown"]', timeout=1000)
                await page.click('i[class*="icon-night"]', timeout=1000)
                menu = await page.query_selector('div[role="menu"]')
                await menu.evaluate('e => e.style.display = "none"')
                print("toggle dark mode")
            except:
                pass

            # go to /r/*/comments/*
            await post_home.click()
            await page.reload(wait_until="domcontentloaded")
            print("/r/*/comments/* loaded 0")

            await page.wait_for_selector(comment_selector)
            print(1)
            await page.wait_for_selector(comment_txt_selector)
            print(2)
            post = await page.wait_for_selector(post_selector)
            print(3)
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            print(4)
            print("/r/*/comments/* loaded 1")
            # page loaded

            # check url
            post_url = page.url
            if post_url in history:
                await page.close()
                await browser.close()
                print("url used")
                # sys.exit(1)
                # ⛔️

            # ✅
            # get post title
            post_title = await page.wait_for_selector(post_title_selector)
            post_title = await post_title.inner_text()
            post_title = re.sub(r"\W_+", "", post_title)
            print(post_title)

            # get post txt - optional
            try:
                post_txt = await page.wait_for_selector(post_txt_selector, timeout=1000)
                post_txt = await post_txt.inner_text()
                post_title += re.sub(r"\W_+", "", post_txt)

            except:
                pass

            # get post screen shot 📸
            post_img_path = "./media/post/post.png"
            await post.screenshot(path=post_img_path)

            # comment images & txt should sync by order
            comment_blocks = await page.query_selector_all(comment_selector)
            comment_txts = await page.query_selector_all(comment_txt_selector)

            comments = []
            comments_img_path = "./media/post/comments"

            print("comments:")
            print(comment_blocks.__len__())
            print(comment_txts.__len__())

            # loop over txt's & screenshot block w same index
            if comment_blocks.__len__() > int(
                n_comments
            ) and comment_txts.__len__() > int(n_comments):

                for index, comment_txt in enumerate(comment_txts):
                    if (
                        index < int(n_comments) and index != 0
                    ):  # first comment migth be a pin
                        try:
                            txt = await comment_txt.inner_text()

                            if txt.__len__() > 0:
                                path = f"{comments_img_path}/{index}/comment.png"
                                speach_path = (
                                    f"{comments_img_path}/{index}/comment_speach.aiff"
                                )

                                await comment_blocks[index].scroll_into_view_if_needed(
                                    timeout=1000
                                )
                                await comment_blocks[index].evaluate(
                                    'e => e.style.paddingBottom="50px"'
                                )
                                await comment_blocks[index].screenshot(path=path)  # 📸
                                txt = re.sub(r"\W_+", "", txt)

                            # append to comments array
                            comment = {
                                "comment_txt": txt,
                                "comment_img": path,
                                "comment_speach": speach_path,
                            }
                            comments.append(comment)

                        except:
                            pass

            # post.json construction
            post_json = {
                "post_url": post_url,
                "post_txt": post_title,
                "post_img": post_img_path,
                "post_speach": "./media/post/post_speach.aiff",
                "comments": comments,
            }

            # save post.json
            with open("./media/post/post.json", "w") as outfile:
                json.dump(post_json, outfile)

            # save to history
            with open("./etc/reddit_history.json", "w") as outfile:
                history.append(post_url)
                json.dump(history, outfile)

            await page.close()
            await browser.close()
            sys.exit(0)

        await a_1()


asyncio.run(main())
