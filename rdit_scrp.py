import json
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import sys
import random
import re
import datetime

# script args
head = False
n_comments = int(sys.argv[1])

# history
history_json = open("./etc/reddit_history.json", encoding="utf-8")
history = json.load(history_json)

# urls
reddit_urls_json = open("./etc/reddit_urls.json", encoding="utf-8")
reddit_urls = json.load(reddit_urls_json)

# mobile selectors
# /r/
nav_slct = 'div[class*="CommunityHeader-text-row m-top-margin"] nav'
post_slct = 'a[class*="Post__link"][href*="comments"]'
post_com_slct = 'a[class*="PostFooter"][href*="comments"]'
# /comments
top_nav = 'nav[class*="TopNav"]'
top_com_slct = 'div[class*="Tree"][class*="m-toplevel"]'
top_com_body_slct = (
    'div[class*="Tree"][class*="m-toplevel"] div[class*="Comment__body"]'
)
every_com_slct = 'div[class*="m-comment"]'
post_title_slct = 'h1[class*="post-title"]'
post_content_slct = 'div[class*="PostContent"]'  # migth b text or img
post_content_title_slct = 'article[class*="Post"]'
# for removal
nav_bluish = 'header[class*="PostHeader"] div'
com_timestamp_slct = 'div[class*="CommentHeader__timestamp"]'
more_com_slct = 'div[class*="m-more"]'
com_tools_slct = 'div[class*="Comment__tools"]'
com_head_more_slct = ['td[class*="CommentHeader__colMore"]']
post_footer_slct = 'footer[class*="PostFooter"]'
post_header_slct = 'a[href*="/r/"]'


async def main():
    async with async_playwright() as p:

        async def a_1():
            browser = await p.chromium.launch(headless=head)
            page = await browser.new_page(
                storage_state="./cookies/reddit/rdit_scrp.json",
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Mobile/15E148 Safari/604.1",
            )
            await stealth_async(page)
            # await page.set_viewport_size({"width": 600, "height": 1000})
            await page.emulate_media(color_scheme="dark")
            await page.goto(random.choice(reddit_urls), wait_until="networkidle")

            # close pop up
            await page.click('text="Continue"')
            print("time")
            await page.wait_for_timeout(435434545)

            # get all posts + comment-count
            posts = await page.query_selector_all(post_com_slct)
            for post in posts:
                pass
                # post_url = await post.get_attribute("href")
                # post_com_count = await post.inner_text()
                # print(f"{post_url} {post_com_count}")

            # go to top post
            await posts[0].click()
            await page.wait_for_selector(top_com_slct)
            await page.wait_for_selector(every_com_slct)
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            print("loadded")
            # /comments loaded

            # check url
            post_url = page.url
            print(f"post url:{post_url}")
            if post_url in history:
                await page.close()
                await browser.close()
                print("url used")
                return sys.exit(1)
                # ⛔️

            # check if video
            is_video = await page.wait_for_selector(
                'div[class*="PostContent"] video', timeout=500
            )
            if bool(is_video):
                await page.close()
                await browser.close()
                print("is video")
                return sys.exit(1)
                # ⛔️

            # remove unwanted comments
            all_com = await page.query_selector_all(every_com_slct)
            for index, com in enumerate(all_com):
                com_text = await com.inner_text()
                unwanted = ["[deleted]", "I am a bot"]
                is_pin = [e for e in unwanted if (e in com_text)]

                if bool(is_pin):
                    await com.evaluate("e=>e.remove();")
                    all_com.pop(index)

            # remove unwanted elements
            async def remover(slct):
                try:
                    more_com = await page.query_selector_all(slct)
                    for com in more_com:
                        await com.evaluate("e=>e.remove();")
                except:
                    pass

            await remover(more_com_slct)
            await remover(com_timestamp_slct)
            await remover(com_tools_slct)
            await remover(com_head_more_slct)
            await remover(post_header_slct)
            await remover(post_footer_slct)
            await remover(top_nav)
            await remover(nav_bluish)
            print("items removed")

            # ✅
            # get post title
            post_title = await page.wait_for_selector(post_title_slct, timeout=3000)
            post_title = await post_title.inner_text()
            post_title = re.sub(r"\W_+", "", post_title)
            # get post content - migth b img
            try:
                post_txt = await page.wait_for_selector(post_content_slct, timeout=3000)
                post_txt = await post_txt.inner_text()
                post_title += re.sub(r"\W_+", "", post_txt)

            except:
                pass
            print(f"title:{post_title}")

            # get post screen shot 📸
            post = await page.wait_for_selector(post_content_title_slct)
            post_img_path = "./media/post/post.png"
            await post.evaluate('e=>e.style.padding="20px"')
            await post.screenshot(path=post_img_path)
            print("screen shot post")

            # comment images & txt should sync by order
            comment_blocks = await page.query_selector_all(top_com_slct)
            comment_txts = await page.query_selector_all(top_com_body_slct)

            comments = []
            comments_img_path = "./media/post/comments"

            comment_txts__len = comment_txts.__len__()
            print(f"comments length:{comment_txts__len}")

            # loop over txt's & screenshot block w same index
            for index, comment_txt in enumerate(comment_txts):
                if index < n_comments and comment_txts__len > n_comments:
                    try:
                        txt = await comment_txt.inner_text()  # might trow error
                        print(f"comment {index} txt: {txt}")

                        if txt.__len__() > 0:
                            path = f"{comments_img_path}/{index}/comment.png"
                            speach_path = (
                                f"{comments_img_path}/{index}/comment_speach.aiff"
                            )
                            await comment_blocks[index].scroll_into_view_if_needed()
                            await page.wait_for_timeout(500)
                            await comment_blocks[index].evaluate(
                                'e => e.style.padding="20px"'
                            )
                            await comment_blocks[index].screenshot(path=path)  # 📸
                            print(f"screen shot comment {index}")
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
                print(f"{comments.__len__()} != {n_comments}")
                await page.close()
                await browser.close()
                return sys.exit(1)

        await a_1()


asyncio.run(main())
