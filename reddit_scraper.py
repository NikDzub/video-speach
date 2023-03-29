import json
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import sys
import random
import re
import datetime

# args
head = False
n_comments = int(sys.argv[1])

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
reddit_urls_json = open("./etc/reddit_history.json", encoding="utf-8")
reddit_urls = json.load(reddit_urls_json)

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

            await page.goto(random.choice(reddit_urls), wait_until="networkidle")
            post_home = await page.wait_for_selector(post_home_selector)
            # /r/* loaded

            # toggle dark mode
            try:
                await page.click('div[class="header-user-dropdown"]', timeout=1000)
                await page.click('i[class*="icon-night"]', timeout=1000)
                menu = await page.query_selector('div[role="menu"]')
                await menu.evaluate('e => e.style.display = "none"')
            except:
                pass

            # go to /r/*/comments/*
            await post_home.click()
            await page.reload(wait_until="domcontentloaded")

            await page.wait_for_selector(comment_selector)
            await page.wait_for_selector(comment_txt_selector)
            post = await page.wait_for_selector(post_selector)
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            # page loaded

            # check url
            post_url = page.url
            if post_url in history:
                await page.close()
                await browser.close()
                # print("url used")
                return sys.exit(1)
                # ⛔️

            # ✅
            # get post title
            post_title = await page.wait_for_selector(post_title_selector)
            post_title = await post_title.inner_text()
            post_title = re.sub(r"\W_+", "", post_title)

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

            comment_txts__len = comment_txts.__len__()

            # loop over txt's & screenshot block w same index
            for index, comment_txt in enumerate(comment_txts):
                if (
                    index < n_comments and comment_txts__len > n_comments
                ):  # first comment might be a pin
                    try:
                        txt = await comment_txt.inner_text()  # might trow error

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

            if comments.__len__() == n_comments:
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

                # append url to history.json
                with open("./etc/reddit_history.json", "w") as outfile:
                    history.append(post_url)
                    json.dump(history, outfile)

                # finished
                await page.close()
                await browser.close()
                print(datetime.datetime.now())
                sys.exit(0)

            else:
                return sys.exit(1)

        await a_1()


asyncio.run(main())
