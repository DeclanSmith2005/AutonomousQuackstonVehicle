from picarx import Picarx
from time import sleep
from robot_hat import Music,TTS
import readchar
from os import geteuid

if geteuid() != 0:
    print(f"\033[0;33m{'The program needs to be run using sudo, otherwise there may be no sound.'}\033[0m")

music = Music()
tts = TTS()
speed = 80

manual = '''
Input key to call the function!
    s: stop car
'''

def main():
    print(manual)
    count = 0
    try: 
        px = Picarx()
        music.music_set_volume(50)
        tts.lang("en-US")

        words = "Starting acceleration test in three... two... one..."
        print(f'{words}')
        sleep(1)
        tts.say(words)
        sleep(1)

        px.forward(speed)

        while True:
            key = readchar.readkey()
            key = key.lower()
            count += 1
            if (key == "s" or count == 10):
                px.stop()
                break
            sleep(0.5)

    finally:
        px.stop()
        sleep(0.2)

if __name__ == "__main__":
    main()