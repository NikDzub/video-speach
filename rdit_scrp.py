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
reddit_urls_json = open("./etc/reddit_urls.json", encoding="utf-8")
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

# mobile selectors
# /r/
nav_slct = 'div[class*="CommunityHeader-text-row m-top-margin"] nav'
post_slct = 'a[class*="Post__link"][href*="comments"]'
post_com_slct = 'a[class*="PostFooter"][href*="comments"]'
# /comments
more_com_slct = 'div[class*="m-more"]'
top_com_slct = 'div[class*="Tree"][class*="m-toplevel"]'


async def main():
    async with async_playwright() as p:

        async def a_1():
            browser = await p.chromium.launch(headless=head)
            page = await browser.new_page(
                storage_state="./cookies/reddit/rdit_scrp.json",
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Mobile/15E148 Safari/604.1",
            )
            await stealth_async(page)
            await page.set_viewport_size({"width": 600, "height": 700})
            await page.emulate_media(color_scheme="dark")

            await page.goto(random.choice(reddit_urls), wait_until="networkidle")

            # pop up
            await page.click('text="Continue"')

            # get all posts
            posts = await page.query_selector_all(post_com_slct)
            for post in posts:
                post_url = await post.get_attribute("href")
                post_com_count = await post.inner_text()
                print(f"{post_url} {post_com_count}")

            await posts[0].click()
            await page.wait_for_selector(top_com_slct)
            # loaded
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")

            all_com = await page.query_selector_all(top_com_slct)
            print(all_com.__len__())

            for index, com in enumerate(all_com):
                is_pin = (
                    "I am a bot, and this action was performed automatically. Please contact the moderators of this subreddit if you have any questions or concerns"
                    in (await com.inner_text())
                )
                if is_pin:
                    print(f"is pin {index}")
                    await com.evaluate("e=>e.remove();")
                    all_com.pop(index)

            print(all_com.__len__())

            try:
                more_com = await page.wait_for_selector(more_com_slct, timeout=2000)
            except:
                pass

            print("time")
            await page.wait_for_timeout(435435345)

            post_home = await page.wait_for_selector(post_home_selector, timeout=3000)
            # /r/* loaded

            # toggle dark mode
            try:
                await page.click('div[class="header-user-dropdown"]', timeout=3000)
                await page.click('i[class*="icon-night"]', timeout=3000)
                menu = await page.query_selector('div[role="menu"]')
                await menu.evaluate('e => e.style.display = "none"')
            except:
                pass

            # go to /r/*/comments/*
            await post_home.click()
            await page.reload(wait_until="domcontentloaded")

            await page.wait_for_selector(comment_selector, timeout=3000)
            await page.wait_for_selector(comment_txt_selector, timeout=3000)
            post = await page.wait_for_selector(post_selector, timeout=3000)
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            # page loaded

            # check url
            post_url = page.url
            if post_url in history:
                await page.close()
                await browser.close()
                print("url used")
                return sys.exit(1)
                # ⛔️

            # ✅
            # get post title
            post_title = await page.wait_for_selector(post_title_selector, timeout=3000)
            post_title = await post_title.inner_text()
            post_title = re.sub(r"\W_+", "", post_title)

            # get post txt - optional
            try:
                post_txt = await page.wait_for_selector(post_txt_selector, timeout=3000)
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
                                timeout=3000
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
                print(f"{sys.argv[0]} {datetime.datetime.now()}")
                sys.exit(0)

            else:
                return sys.exit(1)

        await a_1()


asyncio.run(main())
