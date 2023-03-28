import os
import json
import random
from collections import Counter
import sys
from moviepy.video.io.ffmpeg_tools import *
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    ImageClip,
    imageio,
    CompositeAudioClip,
    CompositeVideoClip,
    TextClip,
    concatenate_videoclips,
)

post_json = open("./media/post/post.json", encoding="utf-8")
post = json.load(post_json)

try:

    # generate title
    ignore_words = [
        "all",
        "just",
        "being",
        "over",
        "both",
        "through",
        "yourselves",
        "its",
        "before",
        "herself",
        "had",
        "should",
        "to",
        "only",
        "under",
        "ours",
        "has",
        "do",
        "them",
        "his",
        "very",
        "they",
        "not",
        "during",
        "now",
        "him",
        "nor",
        "did",
        "this",
        "she",
        "each",
        "further",
        "where",
        "few",
        "because",
        "doing",
        "some",
        "are",
        "our",
        "ourselves",
        "out",
        "what",
        "for",
        "while",
        "does",
        "above",
        "between",
        "t",
        "be",
        "we",
        "who",
        "were",
        "here",
        "hers",
        "by",
        "on",
        "about",
        "of",
        "against",
        "s",
        "or",
        "own",
        "into",
        "yourself",
        "down",
        "your",
        "from",
        "her",
        "their",
        "there",
        "been",
        "whom",
        "too",
        "themselves",
        "was",
        "until",
        "more",
        "himself",
        "that",
        "but",
        "don",
        "with",
        "than",
        "those",
        "he",
        "me",
        "myself",
        "these",
        "up",
        "will",
        "below",
        "can",
        "theirs",
        "my",
        "and",
        "then",
        "is",
        "am",
        "it",
        "an",
        "as",
        "itself",
        "at",
        "have",
        "in",
        "any",
        "if",
        "again",
        "no",
        "when",
        "same",
        "how",
        "other",
        "which",
        "you",
        "after",
        "most",
        "such",
        "why",
        "a",
        "off",
        "i",
        "yours",
        "so",
        "the",
        "having",
        "once",
    ]
    all_words = []

    for comment in post["comments"]:
        comment_txt_array = comment["comment_txt"].lower().split()
        for word in comment_txt_array:
            if word not in ignore_words:
                all_words.append(word)

    most_common = Counter(all_words).most_common()

    vid_title = ""
    for index, word in enumerate(most_common):
        if index < 5:
            vid_title += word[0] + " "

    print(vid_title)

    # game bg
    games = os.listdir("./media/games")
    if ".DS_Store" in games:
        games.remove(".DS_Store")

    game_clip = VideoFileClip(f"./media/games/{random.choice(games)}").volumex(0.2)
    width = game_clip.size[1] / 2

    reddit_clips = []

    # post
    post_speach = AudioFileClip(post["post_speach"])
    post_audio = CompositeAudioClip([post_speach])

    post_clip = (
        ImageClip(post["post_img"])
        .resize(width=width)
        .margin(top=200, opacity=0)
        .set_opacity(0.8)
        .set_fps(24)
        .set_audio(post_audio)
        .set_duration(post_audio.duration)
    )
    reddit_clips.append(post_clip)

    # comments
    for comment in post["comments"]:
        comment_speach = AudioFileClip(comment["comment_speach"])
        comment_audio = CompositeAudioClip([comment_speach])

        comment_clip = (
            ImageClip(comment["comment_img"])
            .set_opacity(0.8)
            .resize(width=width)
            .margin(top=200, opacity=0)
            .set_fps(24)
            .set_audio(comment_audio)
            .set_duration(comment_audio.duration)
        )
        reddit_clips.append(comment_clip)

    # mark
    mark_duration = 10
    bg_music_file = AudioFileClip("./media/bg_music/smoke.mp3")
    bg_music = CompositeAudioClip([bg_music_file]).set_duration(mark_duration)

    mark = (
        ImageClip("./media/mark/free_coins_1.png")
        .set_duration(mark_duration)
        .set_opacity(0.8)
        .resize(width=width)
        .margin(top=200, opacity=0)
        .set_fps(24)
        .set_audio(bg_music)
    )
    reddit_clips.append(mark)

    # video w/o game
    reddit_clips_concat = concatenate_videoclips(reddit_clips, method="compose")

    # bg_clip
    game_clip = game_clip.crop(
        x_center=game_clip.size[0] / 2,
        width=width,
        height=game_clip.size[1],
        # y1=0,
        # y2=game_clip.size[1],
    )
    random_start = random.uniform(10, game_clip.duration - 240)
    game_clip = game_clip.subclip(random_start).set_duration(
        reddit_clips_concat.duration
    )

    # compose & save
    all_clips = CompositeVideoClip(clips=[game_clip, reddit_clips_concat])
    all_clips.write_videofile(f"./media/vids/{vid_title}#reddit.mp4")
    sys.exit(0)

except:
    sys.exit(1)
