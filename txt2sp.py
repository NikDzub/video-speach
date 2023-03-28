import pyttsx3
import json
import random
import sys

engine = pyttsx3.init()

try:

    post_json = open("./media/post/post.json")
    post = json.load(post_json)

    voices = engine.getProperty("voices")
    acceptable_voices = [0, 1, 6, 7, 11, 16, 17, 18, 21, 26, 27, 28, 32, 33]

    engine.setProperty("rate", 280)
    engine.setProperty("volume", 1)

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
    sys.exit(0)
except:
    sys.exit(1)
