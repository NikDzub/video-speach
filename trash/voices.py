import pyttsx3

engine = pyttsx3.init()
engine.setProperty("rate", 300)

voices = engine.getProperty("voices")
# engine.setProperty('voice', voices[3].id)
# 0 1 6 7 5 17 26 27 28 32 33 37 40 45

for index, voice in enumerate(voices):

    print(index)
    engine.setProperty("voice", voice.id)

    engine.say(
        "The Segway was once touted as a revolutionary transportation device, but ultimately failed to live up to its hype due to its high cost, limited practicality, and safety concerns"
    )
    engine.runAndWait()
    engine.stop()
