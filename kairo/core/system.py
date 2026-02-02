"""System utilities for Kairo."""
import os
import sys
import time
import threading

from colorama import Fore, Style

from kairo.config import get_user_data_path
from kairo.models.text import Message
from kairo.models.variable import DataType


class System:
    """Core system utilities for the Kairo shell."""
    
    @staticmethod
    def clear_screen():
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def print_instant(text, end='\n', is_error=False):
        """Print text instantly."""
        from kairo.core.terminal import TerminalState
        
        color_code = Fore.RED if is_error else ""
        reset_code = Style.RESET_ALL if is_error else ""
        
        TerminalState.write(str(text), color_code, end + reset_code)

    @staticmethod
    def print_slow(text, delay=0.005, end='\n', is_error=False):
        """Print text character by character."""
        from kairo.core.terminal import TerminalState
        
        color_code = Fore.RED if is_error else ""
        
        for char in str(text):
            TerminalState.write(char, color_code, '')
            time.sleep(delay)
        
        if end:
            reset_code = Style.RESET_ALL if is_error else ""
            TerminalState.write('', '', end + reset_code)

    @staticmethod
    def colored_input(prompt, hidden=False, start_animation=True):
        """Get colored input from user."""
        from kairo.core.terminal import TerminalState, AsciiArt
        from kairo.utils.input import Input
        
        System.print_slow(prompt, end='')
        
        if start_animation:
            AsciiArt.start_animation()
        
        TerminalState.write('', Fore.YELLOW, '')
        
        try:
            if hidden:
                user_input = Input.get_hidden_input()
            else:
                user_input = input()
                if TerminalState._recording:
                    TerminalState._output_buffer.append(f"{Fore.YELLOW}{user_input}{Style.RESET_ALL}\n")
        except KeyboardInterrupt:
            TerminalState.write('', Style.RESET_ALL, '')
            raise
        
        TerminalState.write('', Style.RESET_ALL, '')
        
        return user_input

    @staticmethod
    def handle_shutdown():
        """Handle system shutdown."""
        from kairo.core.terminal import TerminalState
        from kairo.core.sound import Sound
        
        TerminalState.write('', Style.RESET_ALL, '')
        System.print_instant(Message.SHUTDOWN)
        System.show_loading_bar("shutdown", Fore.RED)
        System.clear_screen()
        sys.exit(1)

    @staticmethod
    def show_loading_bar(sound_name, color=Fore.MAGENTA, filled_char='█', unfilled_char='.'):
        """Display loading bar synchronized with sound playback."""
        from kairo.core.terminal import TerminalState
        from kairo.core.sound import Sound
        
        sound_thread = threading.Thread(target=lambda: Sound.play(sound_name))
        sound_thread.start()
        
        try:
            duration = Sound.get_sound_duration(sound_name)
        except:
            duration = 2.0
        
        bar_width = 50
        TerminalState.write("\n[", color, '')
        start_time = time.time()
        
        while sound_thread.is_alive():
            elapsed = time.time() - start_time
            progress = min(elapsed / duration, 1.0)
            filled = int(bar_width * progress)
            bar = f"{filled_char * filled}{unfilled_char * (bar_width - filled)}"
            percentage = int(progress * 100)
            
            sys.stdout.write(f"\r{color}[{bar}] {percentage}%{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(0.05)
        
        full_bar = f"{filled_char * bar_width}"
        final_output = f"\r{color}[{full_bar}] 100%{Style.RESET_ALL}\n"
        
        sys.stdout.write(final_output)
        sys.stdout.flush()
        
        if TerminalState._recording and len(TerminalState._output_buffer) > 0:
            TerminalState._output_buffer.pop()
            TerminalState._output_buffer.append(f"{color}[{full_bar}] 100%{Style.RESET_ALL}\n")
        
        sound_thread.join()

    @staticmethod
    def welcome(username):
        """Display welcome message with loading bar and animated border."""
        from kairo.core.terminal import TerminalState, AsciiArt
        from kairo.core.sound import Sound
        
        AsciiArt.stop_animation()
        
        System.clear_screen()
        System.print_instant(Message.BOOT)
        
        preload_thread = threading.Thread(target=Sound.preload_sounds, daemon=True)
        preload_thread.start()
        
        System.show_loading_bar("boot", Fore.MAGENTA)
        System.clear_screen()
        
        AsciiArt.initialize_terminal_dimensions()
        TerminalState.start_recording()
        AsciiArt.start_animation()

        System.print_slow(f"Welcome, {username}!\nType '{Fore.MAGENTA}help{Style.RESET_ALL}' for command list, '{Fore.MAGENTA}exit{Style.RESET_ALL}' to close;")
        
    @staticmethod
    def glitch():
        """Display error message and exit."""
        from kairo.core.sound import Sound
        
        System.clear_screen()
        Sound.play_and_print("glitch", Message.GLITCH, is_error=True)
        time.sleep(0.5)
        System.print_slow(Message.ERROR, is_error=True)
        time.sleep(0.5)
        System.clear_screen()
        sys.exit(1)

    @staticmethod
    def create_user_directory(username):
        """Create user directory if it doesn't exist."""
        user_dir = os.path.join(get_user_data_path(), "users", username)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        return user_dir

    @staticmethod
    def show_result(result, output_type="sound"):
        """Centralized result display handler."""
        from kairo.core.sound import Sound
        from kairo.utils.formatting import NumberFormatter
        import kairo.state as state
        
        if output_type == "sound":
            if isinstance(result, (int, float)):
                Sound.play_and_print("enter", NumberFormatter.format_number(result))
            else:
                Sound.play_and_print("enter", result)
        elif output_type == "silent":
            pass
        else:
            System.print_instant(result)

    @staticmethod
    def throw_error(message, set_null_result=True):
        """Consolidated error display function."""
        from kairo.core.sound import Sound
        import kairo.state as state
        
        System.print_instant(Message.MALFUNCTION, is_error=True)
        Sound.play("error")
        System.print_slow(message, is_error=True)
        
        if set_null_result:
            state.last_command_result = ("NULL", DataType.NULL)
