import os
import time

try:
    import pygame
except ImportError:
    print("Error: The 'pygame' library is not installed.")
    print("Please install it by running: pip install pygame")
    exit(1)

def main():
    # Initialize pygame mixer
    try:
        pygame.mixer.init()
    except Exception as e:
        print(f"Failed to initialize pygame mixer: {e}")
        return

    # Look for the sound folder relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sound_dir = os.path.join(script_dir, 'sound')

    if not os.path.exists(sound_dir):
        print(f"Could not find sound folder at: {sound_dir}")
        return

    # List all audio files (.mp3, .wav, etc.)
    valid_extensions = ('.wav', '.mp3', '.ogg')
    sound_files = [f for f in os.listdir(sound_dir) if f.lower().endswith(valid_extensions)]

    if not sound_files:
        print("No audio files found in the sound folder.")
        return

    print("--- Audio Test Utility ---")
    
    while True:
        print("\nAvailable sounds:")
        for idx, filename in enumerate(sound_files):
            print(f"{idx + 1}. {filename}")
        print("0. Exit")
        
        choice = input("\nEnter the number of the sound to play (or 0 to exit): ")
        
        if choice.strip() == '0':
            print("Exiting...")
            break
            
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(sound_files):
                selected_file = sound_files[choice_idx]
                file_path = os.path.join(sound_dir, selected_file)
                
                print(f"\n>>> Playing '{selected_file}'...")
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()
                
                # Wait for the user to stop the playback
                input("Press Enter to stop playing and return to menu...")
                pygame.mixer.music.stop()
            else:
                print("Invalid choice. Please pick from the list above.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
        except Exception as e:
            print(f"Error playing sound: {e}")

if __name__ == "__main__":
    main()
