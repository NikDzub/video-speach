import os
import json
import random
from moviepy.video.io.ffmpeg_tools import *
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    ImageClip,
    imageio,
    CompositeAudioClip,
    CompositeVideoClip,
    concatenate_videoclips,
)


post_json = open("./media/post/post.json", encoding="utf-8")
post = json.load(post_json)

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


reddit_clips_concat = concatenate_videoclips(reddit_clips, method="compose")


game_clip = game_clip.crop(
    x_center=game_clip.size[0] / 2,
    width=width,
    height=game_clip.size[1],
    # y1=0,
    # y2=game_clip.size[1],
)
random_start = random.uniform(10, game_clip.duration)
game_clip = game_clip.subclip(random_start).set_duration(reddit_clips_concat.duration)


# all_clips = concatenate_videoclips([game_clip, reddit_clips_concat], method="compose")
all_clips = CompositeVideoClip(clips=[game_clip, reddit_clips_concat])


all_clips.write_videofile("./media/vids/clip.mp4")
