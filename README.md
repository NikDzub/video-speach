## Reddit Bot

**Using Playwright, Moviepy and Pyttsx3**

python rdit_scrp.py 6 && python3 txt2sp.py && python editor.py && python uploadTik.py


cron:*/30 * * * * cd ~/Desktop/moviepy && /usr/bin/python3 rdit_scrp.py 6 && /Library/Frameworks/Python.framework/Versions/3.10/bin/python3 txt2sp.py && /usr/bin/python3 editor.py && /usr/bin/python3 uploadTik.py >> ~/Desktop/moviepy/cron.txt 2>&1

<hr>

**rdit_scrp.py -n_comments:**

1.geting random /r/ url from ./etc/reddit_urls.json

2.check top post (is already used url / video post? then abort)

3.hide unwanted content (pinned / deleted / promoted comments)

4.hide unwanted elements (for cleaner look)

5.screen shot and write data to ./media/post/post.json

<hr>

**txt2sp.py**

1.chosing a random **acceptable** voice for each comment

2.save text to speach audio file to ./media/post/comments/**{index}**

<hr>

**python editor.py**

1.getting info from post.json about every location of screen shots and their corresponding audio

2.adding random video game clip from ./media/games

3.editing the video

4.naming the video by most used words

<hr>

**uploadTik.py**

1.login to TikTok from ./cookies/tiktok/**user_cookie.json**

2.upload the video and delete it

(can also upload multiple videos to multiple accounts)

<hr>

**There are a ton of those bots but i really wanted to build one for myself**

[Video Link](https://www.tiktok.com/@blast_k1/video/7215623162933873922)

<img width="402" alt="Screen Shot 2023-04-03 at 21 26 25" src="https://user-images.githubusercontent.com/87159434/229595248-1857572f-d7bd-4855-b8bf-9e334614dafc.png">
