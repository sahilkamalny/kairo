"""Terminal state management for Kairo."""
import sys
import os
import threading
import datetime
import shutil

from colorama import Fore, Style


class TerminalState:
    """Manages terminal state for restoration after curses screens."""
    
    _output_buffer = []
    _recording = False
    _stdout_lock = threading.Lock()
    
    @staticmethod
    def start_recording():
        """Start recording terminal output."""
        TerminalState._recording = True
        TerminalState._output_buffer = []
    
    @staticmethod
    def stop_recording():
        """Stop recording terminal output."""
        TerminalState._recording = False
    
    @staticmethod
    def reset():
        """Reset the buffer (used on reboot)."""
        TerminalState._output_buffer = []
    
    @staticmethod
    def write(text: str, color_code: str = "", end: str = ''):
        """Write to stdout and record if active."""
        with TerminalState._stdout_lock:
            full_output = f"{color_code}{text}{end}"
            
            sys.stdout.write(full_output)
            sys.stdout.flush()
            
            if TerminalState._recording:
                TerminalState._output_buffer.append(full_output)
    
    @staticmethod
    def restore():
        """Restore the terminal state from buffer."""
        # Import here to avoid circular import
        from kairo.core.system import System
        
        System.clear_screen()
        
        with TerminalState._stdout_lock:
            for output in TerminalState._output_buffer:
                sys.stdout.write(output)
                sys.stdout.flush()


class AsciiArt:
    """Animated ASCII art border for the terminal."""
    
    _stdout_lock = threading.Lock()
    _running = True
    _terminal_width = None
    _terminal_height = None
    _current_thread = None
    _stop_event = threading.Event()
    _thread_lock = threading.Lock()

    @staticmethod
    def initialize_terminal_dimensions():
        """Record terminal dimensions."""
        try:
            size = shutil.get_terminal_size()
            AsciiArt._terminal_width = size.columns
            AsciiArt._terminal_height = size.lines
        except:
            AsciiArt._terminal_width = 120
            AsciiArt._terminal_height = 30

    @staticmethod
    def stop_animation():
        """Stop the current animation thread safely."""
        with AsciiArt._thread_lock:
            AsciiArt._stop_event.set()
            
            if AsciiArt._current_thread and AsciiArt._current_thread.is_alive():
                AsciiArt._current_thread.join(timeout=0.5)
            
            AsciiArt._current_thread = None
            AsciiArt._stop_event.clear()
    
    @staticmethod
    def start_animation():
        """Start the animation thread safely."""
        with AsciiArt._thread_lock:
            if AsciiArt._current_thread and AsciiArt._current_thread.is_alive():
                AsciiArt._stop_event.set()
                AsciiArt._current_thread.join(timeout=0.5)
                AsciiArt._stop_event.clear()
            
            AsciiArt.initialize_terminal_dimensions()
            
            AsciiArt._current_thread = threading.Thread(
                target=AsciiArt.draw_animated_border, 
                daemon=True
            )
            AsciiArt._current_thread.start()
    
    @staticmethod
    def handle_terminal_resize():
        """Handle terminal resize by clearing screen and redrawing from buffer."""
        from kairo.core.system import System
        
        AsciiArt.stop_animation()
        AsciiArt.initialize_terminal_dimensions()
        System.clear_screen()
        
        with TerminalState._stdout_lock:
            for output in TerminalState._output_buffer:
                sys.stdout.write(output)
                sys.stdout.flush()
        
        AsciiArt.start_animation()

    @staticmethod
    def draw_animated_border():
        """Draw an animated cyberpunk-style ASCII art border on the right side."""
        import time
        
        box_width = 28
        
        while not AsciiArt._stop_event.is_set():
            try:
                current_width = shutil.get_terminal_size().columns
            except:
                current_width = AsciiArt._terminal_width or 120
            
            start_col = max(0, current_width - box_width - 1)
            start_line = 1
            
            current_time = datetime.datetime.now().strftime('%I:%M %p')
            
            frames = [
                [
                    f"{Fore.MAGENTA}╔══════════════════════════╗{Style.RESET_ALL}",
                    f"{Fore.MAGENTA}║ ▶◀ KAIRO ▶◀ {current_time} ▓▒░ ║{Style.RESET_ALL}",
                    f"{Fore.MAGENTA}╚══════════════════════════╝{Style.RESET_ALL}"
                ],
                [
                    f"{Fore.MAGENTA}╔══════════════════════════╗{Style.RESET_ALL}",
                    f"{Fore.MAGENTA}║ ◀▶ KAIRO ◀▶ {current_time} ░▓▒ ║{Style.RESET_ALL}",
                    f"{Fore.MAGENTA}╚══════════════════════════╝{Style.RESET_ALL}"
                ],
                [
                    f"{Fore.MAGENTA}╔══════════════════════════╗{Style.RESET_ALL}",
                    f"{Fore.MAGENTA}║ ◥◤ KAIRO ◥◤ {current_time} ▒░▓ ║{Style.RESET_ALL}",
                    f"{Fore.MAGENTA}╚══════════════════════════╝{Style.RESET_ALL}"
                ],
                [
                    f"{Fore.MAGENTA}╔══════════════════════════╗{Style.RESET_ALL}",
                    f"{Fore.MAGENTA}║ ◢◣ KAIRO ◢◣ {current_time} ░▒▓ ║{Style.RESET_ALL}",
                    f"{Fore.MAGENTA}╚══════════════════════════╝{Style.RESET_ALL}"
                ]
            ]
            
            for frame in frames:
                if AsciiArt._stop_event.is_set():
                    return
                    
                with AsciiArt._stdout_lock:
                    sys.stdout.write("\033[?25l\0337")
                    
                    for line_num, line in enumerate(frame):
                        sys.stdout.write(f"\033[{start_line + line_num};{start_col}H")
                        sys.stdout.write(line)
                    
                    sys.stdout.write("\0338\033[?25h")
                    sys.stdout.flush()
                time.sleep(0.625)
