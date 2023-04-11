import pyttsx3
import json
import random
import sys
import datetime

engine = pyttsx3.init()

try:

    post_json = open("./media/post/post.json")
    post = json.load(post_json)

    voices = engine.getProperty("voices")
    acceptable_voices = [0, 1, 6, 7, 5, 17, 26, 27, 28, 32, 33, 37, 40, 45]

    engine.setProperty("rate", 280)
    engine.setProperty("volume", 1.2)

    # comments
    for index, comment in enumerate(post["comments"]):
        engine.setProperty("voice", voices[random.choice(acceptable_voices)].id)

        comment_txt = comment["comment_txt"]
        engine.save_to_file(
            comment_txt, f"./media/post/comments/{index}/comment_speach.aiff"
        )

    # main post
    engine.setProperty("voice", voices[7].id)

    post_txt = post["post_txt"]
    engine.save_to_file(post_txt, f"./media/post/post_speach.aiff")

    engine.runAndWait()
    print(f"{sys.argv[0]} ✅ {datetime.datetime.now()}")
    sys.exit(1)

except:
    sys.exit(0)
