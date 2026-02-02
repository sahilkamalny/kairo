"""Sound management for Kairo."""
import os
import threading
from playsound import playsound

from kairo.config import get_app_path


class Sound:
    """Handles audio playback for the Kairo shell."""
    
    base_path = get_app_path()

    @staticmethod
    def preload_sounds():
        """Preload commonly used sounds to reduce first-play delay."""
        sound_files = ["enter", "help", "error", "boot", "shutdown"]
        
        for sound in sound_files:
            try:
                sound_path = os.path.join(Sound.base_path, "sounds", f"{sound}.mp3")
                if os.path.exists(sound_path):
                    with open(sound_path, 'rb') as f:
                        f.read(1024)  # Read first 1KB to cache
            except:
                pass  # Silently ignore errors during preload

    @staticmethod
    def play(sound: str):
        """Play a sound file."""
        sound_path = os.path.join(Sound.base_path, "sounds", f"{sound}.mp3")
        playsound(sound_path)

    @staticmethod
    def play_and_print(sound: str, result: str = "", is_slow: bool = False, is_error: bool = False):
        """Play sound and print result simultaneously."""
        # Import here to avoid circular import
        from kairo.core.system import System
        
        sound_thread = threading.Thread(target=lambda: Sound.play(sound))
        sound_thread.start()
        if result != "":
            if is_slow:
                System.print_slow(f"\n{result}", is_error=is_error)
            else:
                System.print_instant(f"\n{result}", is_error=is_error)

    @staticmethod
    def get_sound_duration(sound: str) -> float:
        """Get duration of a sound file in seconds."""
        try:
            from mutagen.mp3 import MP3
            sound_path = os.path.join(Sound.base_path, "sounds", f"{sound}.mp3")
            audio = MP3(sound_path)
            return audio.info.length
        except:
            return 2.0  # Default 2 seconds if mutagen not available
