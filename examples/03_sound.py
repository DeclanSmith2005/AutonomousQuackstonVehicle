from time import sleep
from robot_hat import Music, TTS
import readchar
from os import geteuid
import os

if geteuid() != 0:
    print(f"\033[0;33m{'The program needs to be run using sudo, otherwise there may be no sound.'}\033[0m")

music = Music()
tts = TTS()

manual = '''
Input key to call the function!
    space: Play sound effect (Car horn)
    c: Play sound effect with threads
    t: Text to speak
    q: Play/Stop Music
'''

# Get the absolute path to the sound folder
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "sound")
CAR_HORN_PATH = os.path.join(SOUND_DIR, "car-double-horn.wav")
MUSIC_PATH = os.path.join(SOUND_DIR, "autonomous_in_quackston.mp3")

def main():
    print(manual)

    flag_bgm = False
    music.music_set_volume(20)
    tts.lang("en-US")

    while True:
        key = readchar.readkey()
        key = key.lower()
        if key == "q":
            flag_bgm = not flag_bgm
            if flag_bgm is True:
                print('Play Music')
                music.music_play(MUSIC_PATH)
            else:
                print('Stop Music')
                music.music_stop()

        elif key == readchar.key.SPACE:
            print('Beep beep beep !')
            music.sound_play(CAR_HORN_PATH)
            sleep(0.1)

        elif key == "c":
            print('Beep beep beep !')
            music.sound_play_threading(CAR_HORN_PATH)
            sleep(0.1)

        elif key == "t":
            words = "Hello ducks, I am your autonomous taxi!"
            print(f'{words}')
            tts.say(words)
            sleep(0.1)

if __name__ == "__main__":
    main()