from time import sleep
from robot_hat import Music,TTS
import readchar
from os import geteuid

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
                music.music_play('../sound/autonomous_in_quackston.mp3')
            else:
                print('Stop Music')
                music.music_stop()

        elif key == readchar.key.SPACE:
            print('Beep beep beep !')
            music.sound_play('../sound/car-double-horn.wav')
            sleep(0.05)

        elif key == "c":
            print('Beep beep beep !')
            music.sound_play_threading('../sound/car-double-horn.wav')
            sleep(0.05)

        elif key == "t":
            words = "Hello ducks, I am your autonomous taxi!"
            print(f'{words}')
            tts.say(words)

if __name__ == "__main__":
    main()