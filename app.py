import sys
import datetime
import time
import os
import json
import shutil
import threading
import ctypes
import re
import random
import math
from colorama import init, Fore, Style
from playsound import playsound
from enum import Enum
from typing import List, Tuple

# Import platform-specific modules for character input
if os.name == 'nt':  # Windows
    import msvcrt
    try:
        import curses
    except ImportError:
        print("=" * 60)
        print("ERROR: Required module 'windows-curses' not installed.")
        print("This application requires curses support on Windows.")
        print("=" * 60)
        input("Press Enter to exit...")
        sys.exit(1)
else:  # Unix-like
    import tty
    import termios
    import select
    import curses

# Add after the existing imports, before System Messages
try:
    import requests
    from bs4 import BeautifulSoup
    import html2text
except ImportError:
    print("=" * 60)
    print("WARNING: Web browser dependencies not installed.")
    print("To enable the 'browser' command, install:")
    print("  pip install requests beautifulsoup4 html2text")
    print("=" * 60)
    requests = None
    BeautifulSoup = None
    html2text = None

# System Messages
class Message:
    MENU = "█▓▒░ SYSTEM MENU ░▒▓█"
    BOOT = "█▓▒░ BOOTING SYSTEM ░▒▓█"
    SHUTDOWN = "\n█▓▒░ SYSTEM SHUTDOWN ░▒▓█"
    MALFUNCTION = "\n░▒▓█ SYSTEM MALFUNCTION █▓▒░"
    GLITCH = "░▒▓█ ┊⧗͡͠҉͘͢͏̀҉G͏̴L҉̷͘͞͏̀͞͡I̷͡҉̴T̵C͟H͜ █▓▒░"
    ERROR = "⊠⊡⧗͡҉⧛͜⚠͠ ⬢ ERROR C͏͝O̷͏D͘E: 0xA͠C4D32 ⬢ ⚠⧛⧗⊡⊠\nU̴͢S̸̛E̶͝R̷͝ ̷͘D̵͟O̸͡E̸̛S̶͟ ̵͡N̶̸O̵͜T̵͡ ̴͜Ę̵X̵͢I̵̡S̶͝T̷͡\n▒▓▒▒͠▓▒▒░▒▓ ▒▒░▓▒░░▓▒▒▒▒▒▓▒▒▒▒▒▒▒▒▒▓▒▒▒▒▒▒▒▒▒▓▒▒▒▒ ▒▒▒▒▓▒▒▒▒▒▒▒▒▒▓▒▒▒▒▒▒▒▒▒▓▒▒▒▒▒▒▒▒▒▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░"

class SplashScreen:
    @staticmethod
    def _fade_out(frame_cells, term_width, term_height, delay=0.001):
        """
        Column-by-column fade from sides to center with 5-column wide magenta highlighting.
        Highlights 5 columns on each side, but only clears the outermost left and right columns.
        """
        delay = delay * (144 / term_width)
        left_col = 0
        right_col = term_width - 1
        
        while left_col <= right_col:
            out = ["\033[H"]
            
            highlight_color = Fore.MAGENTA
            highlight_width = int(term_width / 10)
            
            # Calculate highlight ranges
            left_highlight_start = left_col
            left_highlight_end = min(left_col + highlight_width - 1, right_col)
            
            right_highlight_start = max(right_col - highlight_width + 1, left_col)
            right_highlight_end = right_col
            
            # Highlight left side columns (5 columns wide)
            for x in range(left_highlight_start, left_highlight_end + 1):
                for y in range(term_height):
                    if (y, x) in frame_cells:
                        cell_content = frame_cells[(y, x)]
                        # Strip existing color codes and apply magenta
                        ansi_re = re.compile(r'\x1b\[[0-9;]*[A-Za-z]')
                        clean_char = ansi_re.sub('', cell_content)
                        out.append(f"\033[{y+1};{x+1}H{highlight_color}{clean_char}{Style.RESET_ALL}")
            
            # Highlight right side columns (5 columns wide) - only if not overlapping with left
            if right_highlight_start > left_highlight_end:
                for x in range(right_highlight_start, right_highlight_end + 1):
                    for y in range(term_height):
                        if (y, x) in frame_cells:
                            cell_content = frame_cells[(y, x)]
                            ansi_re = re.compile(r'\x1b\[[0-9;]*[A-Za-z]')
                            clean_char = ansi_re.sub('', cell_content)
                            out.append(f"\033[{y+1};{x+1}H{highlight_color}{clean_char}{Style.RESET_ALL}")
            
            sys.stdout.write("".join(out))
            sys.stdout.flush()
            time.sleep(delay)
            
            # Then clear ONLY the outermost left and right columns
            out = ["\033[H"]
            for y in range(term_height):
                out.append(f"\033[{y+1};{left_col+1}H ")
                if left_col != right_col:
                    out.append(f"\033[{y+1};{right_col+1}H ")
            
            sys.stdout.write("".join(out))
            sys.stdout.flush()
            
            # Move to next columns (only the outermost ones move inward)
            left_col += 1
            right_col -= 1
            
            # Small delay before next iteration
            if left_col <= right_col:
                time.sleep(delay * 0.3)
                      
    @staticmethod
    def show(glow_speed: float = 1.0, side_density: float = 0.4, rain_density: float = 0.125):
        """
        Cyberpunk splash screen with vertical rain, glowing title (KAIRO always bright),
        breathing version glow for "v 0.1", and a closed magenta container with caved corners.
        Streams scale dynamically with window size and share a smooth, uniform gradient.
        """

        # PRELOAD SOUNDS IMMEDIATELY at startup
        Sound.preload_sounds()

        try:
            term_width = shutil.get_terminal_size().columns
            term_height = shutil.get_terminal_size().lines
        except:
            term_width, term_height = 120, 30

        # --- Scaling factors ---
        width_scale = term_width / 144
        height_scale = term_height / 38

        System.clear_screen()
        chars = "0123456789ABCDEF"
        ansi_re = re.compile(r'\x1b\[[0-9;]*[A-Za-z]')
        def visible_len(s): return len(ansi_re.sub('', s))

        title_lines = ["KAIRO", "", "v 0.1"]
        center_y = (term_height // 2) - (len(title_lines) // 2)

        # --- Column setup (rain) with HEIGHT-PROPORTIONAL lengths ---
        num_columns = int(term_width * rain_density)
        
        # Calculate rain stream lengths proportional to terminal height
        height_scale_factor = 1.0
        base_min_length = int(6 * height_scale * height_scale_factor)
        base_max_length = 3 * base_min_length
        
        columns = []
        used_positions = set()

        for _ in range(num_columns):
            # Randomize X positions to avoid even spacing
            while True:
                x = random.randint(0, term_width - 1)
                if x not in used_positions:
                    used_positions.add(x)
                    break
            base_speed = random.choice([1, 2, 3])
            stream_length = random.randint(base_min_length, base_max_length)
            columns.append({
                "x": x,
                "y": random.randint(-term_height, 0),
                "speed": base_speed,
                "chars": [random.choice(chars) for _ in range(term_height)],
                "length": stream_length,
            })

        # --- Side streams setup (randomized vertical positions) ---
        left_streams, right_streams = [], []
        num_side_streams = max(1, int(term_height * side_density))

        # Randomized but non-uniform Y positions
        y_positions = sorted(random.sample(range(term_height), num_side_streams))
        while len(y_positions) < num_side_streams:
            y_positions.append(random.randint(0, term_height - 1))

        width_scale_factor = 1.0
        min_len = int(10 * width_scale * width_scale_factor)
        max_len = 4 * min_len

        for y in y_positions:
            length = random.randint(min_len, max_len)
            left_streams.append({
                "y": y,
                "length": length,
                "chars": [random.choice(chars) for _ in range(length)],
                "progress": 0,
                "speed": random.choice([1, 2]),
                "direction": "right",
                "vertical_speed": 1,
            })
            length = random.randint(min_len, max_len)
            right_streams.append({
                "y": y,
                "length": length,
                "chars": [random.choice(chars) for _ in range(length)],
                "progress": 0,
                "speed": random.choice([1, 2]),
                "direction": "left",
                "vertical_speed": 1,
            })

        # --- Shared gradient for side streams ---
        longest_stream_len = max_len
        def get_color_for_position(i):
            pos = i / longest_stream_len
            if pos < 0.15:
                return Fore.LIGHTMAGENTA_EX + Style.BRIGHT
            elif pos < 0.30:
                return Fore.MAGENTA
            elif pos < 0.55:
                return Fore.MAGENTA
            else:
                return Fore.MAGENTA + Style.DIM

        # --- Shared gradient for vertical rain (HEIGHT-PROPORTIONAL) ---
        def get_rain_color_for_offset(offset, stream_length):
            """Get color based on position in stream, proportional to stream length"""
            pos = offset / stream_length
            if pos < 0.05:  # Head (brightest)
                return Fore.LIGHTCYAN_EX + Style.BRIGHT
            elif pos < 0.30:  # Near head
                return Fore.CYAN
            elif pos < 0.65:  # Middle
                return Fore.LIGHTBLUE_EX
            else:  # Tail (dimmest)
                return Fore.BLUE + Style.DIM

        # --- Hide cursor ---
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()
        if os.name != "nt":
            old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())

        user_pressed_key = False
        start_time = time.time()
        prev_side_stream_rows = set()

        try:
            while not user_pressed_key:
                try:
                    new_width = shutil.get_terminal_size().columns
                    new_height = shutil.get_terminal_size().lines
                except:
                    new_width, new_height = term_width, term_height

                if (new_width, new_height) != (term_width, term_height):
                    term_width, term_height = new_width, new_height
                    width_scale = term_width / 144
                    height_scale = term_height / 38
                    System.clear_screen()
                    prev_side_stream_rows.clear()
                    
                    # --- Regenerate vertical rain columns with HEIGHT-PROPORTIONAL lengths ---
                    num_columns = int(term_width * rain_density)
                    base_min_length = int(8 * height_scale * height_scale_factor)
                    base_max_length = 2 * base_min_length
                    
                    columns = []
                    used_positions = set()
                    for _ in range(num_columns):
                        while True:
                            x = random.randint(0, term_width - 1)
                            if x not in used_positions:
                                used_positions.add(x)
                                break
                        base_speed = random.choice([1, 2, 3])
                        stream_length = random.randint(base_min_length, base_max_length)
                        columns.append({
                            "x": x,
                            "y": random.randint(-term_height, 0),
                            "speed": base_speed,
                            "chars": [random.choice(chars) for _ in range(term_height)],
                            "length": stream_length,
                        })
                    
                    # --- Regenerate side streams ---
                    left_streams, right_streams = [], []
                    num_side_streams = max(1, int(term_height * side_density))
                    y_positions = sorted(random.sample(range(term_height), num_side_streams))
                    while len(y_positions) < num_side_streams:
                        y_positions.append(random.randint(0, term_height - 1))
                    
                    min_len = int(10 * width_scale * width_scale_factor)
                    max_len = 4 * min_len
                    
                    for y in y_positions:
                        length = random.randint(min_len, max_len)
                        left_streams.append({
                            "y": y,
                            "length": length,
                            "chars": [random.choice(chars) for _ in range(length)],
                            "progress": 0,
                            "speed": random.choice([1, 2]),
                            "direction": "right",
                            "vertical_speed": 1,
                        })
                        length = random.randint(min_len, max_len)
                        right_streams.append({
                            "y": y,
                            "length": length,
                            "chars": [random.choice(chars) for _ in range(length)],
                            "progress": 0,
                            "speed": random.choice([1, 2]),
                            "direction": "left",
                            "vertical_speed": 1,
                        })
                    
                    # --- Update longest stream length for gradient ---
                    longest_stream_len = max_len

                center_y = (term_height // 2) - (len(title_lines) // 2)
                longest_line_len = max(visible_len(l) for l in title_lines)
                box_width = longest_line_len + 12
                box_height = len(title_lines) + 4
                top_y = max(0, center_y - 2)
                left_x = max(0, (term_width - box_width) // 2)

                t = time.time() - start_time
                frame_cells = {}

                # --- Clear previous side stream rows ---
                for y in prev_side_stream_rows:
                    if 0 <= y < term_height:
                        for x in range(term_width):
                            if not (top_y <= y < top_y + box_height and left_x <= x < left_x + box_width):
                                frame_cells[(y, x)] = " "
                prev_side_stream_rows.clear()

                # --- Update and scroll side streams down ---
                for stream_list in (left_streams, right_streams):
                    for stream in stream_list:
                        # Shift characters once per frame
                        stream["chars"].pop()
                        stream["chars"].insert(0, random.choice(chars))

                        # Increment progress smoothly (controls how far into the stream is visible)
                        stream["progress"] += stream["speed"] * 0.5
                        if stream["progress"] > stream["length"]:
                            stream["progress"] = stream["length"]

                        # Move vertically
                        stream["y"] += stream["vertical_speed"]
                        if stream["y"] >= term_height:
                            stream["y"] = -1  # wrap around

                # --- Build protection map (safe zones) ---
                protected_ranges = {y: [] for y in range(term_height)}
                for stream_list in (left_streams, right_streams):
                    for stream in stream_list:
                        y = stream["y"]
                        if y < 0 or y >= term_height:
                            continue
                        direction = stream["direction"]
                        length = stream["length"]
                        progress = min(stream["progress"], length)
                        if direction == "right":
                            start_x = 0
                            end_x = min(int(progress), term_width - 1)
                        else:
                            start_x = max(term_width - int(progress), 0)
                            end_x = term_width - 1
                        protected_ranges[y].append((start_x, end_x))

                # --- Vertical rain with HEIGHT-PROPORTIONAL gradient ---
                # First, clear ALL non-protected positions where rain columns exist
                for col in columns:
                    x = col["x"]
                    for clear_y in range(term_height):
                        # Skip if protected by side stream
                        if any(r[0] <= x <= r[1] for r in protected_ranges.get(clear_y, [])):
                            continue
                        # Skip if inside title box
                        if top_y <= clear_y < top_y + box_height and left_x <= x < left_x + box_width:
                            continue
                        # Clear this position
                        frame_cells[(clear_y, x)] = " "

                # Now draw the rain
                for col in columns:
                    x = col["x"]
                    col["y"] += col["speed"]
                    if col["y"] > term_height + col["length"]:
                        col["y"] = random.randint(-term_height // 2, -5)
                        col["chars"] = [random.choice(chars) for _ in range(term_height)]
                        col["length"] = random.randint(base_min_length, base_max_length)

                    for offset in range(col["length"]):
                        y = col["y"] - offset
                        if not (0 <= y < term_height):
                            continue
                        if top_y <= y < top_y + box_height and left_x <= x < left_x + box_width:
                            continue
                        # Check if this position is protected by a side stream
                        if any(r[0] <= x <= r[1] for r in protected_ranges.get(y, [])):
                            continue
                        
                        # Use proportional gradient based on stream length
                        color = get_rain_color_for_offset(offset, col["length"])
                        ch = col["chars"][y % len(col["chars"])]
                        frame_cells[(y, x)] = f"{color}{ch}{Style.RESET_ALL}"

                # --- Side streams (shared gradient, progressive reveal) ---
                for stream_list in (left_streams, right_streams):
                    for stream in stream_list:
                        y = stream["y"]
                        if y < 0 or y >= term_height:
                            continue

                        direction = stream["direction"]
                        visible_chars = int(stream["progress"])
                        visible_chars = max(1, min(visible_chars, stream["length"]))

                        for i, ch in enumerate(stream["chars"][:visible_chars]):
                            if direction == "right":
                                x = i
                            else:
                                x = term_width - 1 - i
                            if not (0 <= x < term_width):
                                continue
                            if top_y <= y < top_y + box_height and left_x <= x < left_x + box_width:
                                continue

                            color = get_color_for_position(i)
                            frame_cells[(y, x)] = f"{color}{ch}{Style.RESET_ALL}"

                        prev_side_stream_rows.add(y)

                # --- Box frame ---
                box_color = Fore.MAGENTA + Style.DIM
                if 0 <= top_y < term_height:
                    frame_cells[(top_y, left_x)] = f"{box_color}╭{'─'*(box_width-2)}╮{Style.RESET_ALL}"
                if 0 <= top_y + box_height - 1 < term_height:
                    frame_cells[(top_y + box_height - 1, left_x)] = f"{box_color}╰{'─'*(box_width-2)}╯{Style.RESET_ALL}"
                for i in range(1, box_height - 1):
                    y = top_y + i
                    if 0 <= y < term_height:
                        frame_cells[(y, left_x)] = f"{box_color}│{Style.RESET_ALL}"
                        frame_cells[(y, left_x + box_width - 1)] = f"{box_color}│{Style.RESET_ALL}"
                        for j in range(1, box_width - 1):
                            frame_cells[(y, left_x + j)] = " "

                # --- Draw text properly, character by character ---
                for i, line in enumerate(title_lines):
                    y = center_y + i
                    x_start = (term_width - visible_len(line)) // 2
                    if "KAIRO" in line:
                        for j, ch in enumerate(line):
                            frame_cells[(y, x_start + j)] = f"{Fore.MAGENTA}{Style.BRIGHT}{ch}{Style.RESET_ALL}"
                    elif "v" in line:
                        phase = (math.sin(t * math.pi * glow_speed) + 1) / 2
                        color = Fore.LIGHTBLUE_EX if phase >= 0.5 else (Fore.BLUE + Style.DIM)
                        for j, ch in enumerate(line):
                            frame_cells[(y, x_start + j)] = f"{color}{ch}{Style.RESET_ALL}"

                # --- Emit frame ---
                out = ["\033[H"]
                for (y, x), cell in frame_cells.items():
                    out.append(f"\033[{y+1};{x+1}H{cell}")
                sys.stdout.write("".join(out))
                sys.stdout.flush()

                # --- Exit ---  
                if os.name == "nt":
                    import msvcrt
                    if msvcrt.kbhit():
                        msvcrt.getch()
                        SplashScreen._fade_out(frame_cells, term_width, term_height)
                        user_pressed_key = True
                else:
                    if select.select([sys.stdin], [], [], 0)[0]:
                        sys.stdin.read(1)
                        SplashScreen._fade_out(frame_cells, term_width, term_height)
                        user_pressed_key = True

                time.sleep(0.05)

        finally:
            if os.name != "nt":
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            sys.stdout.write("\033[?25h")
            sys.stdout.flush()
            System.clear_screen()

class AsciiArt:
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
            
            AsciiArt._current_thread = threading.Thread(target=AsciiArt.draw_animated_border, daemon=True)
            AsciiArt._current_thread.start()
    
    @staticmethod
    def handle_terminal_resize():
        """Handle terminal resize by clearing screen and redrawing from buffer"""
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
        """Draw an animated cyberpunk-style ASCII art border on the right side with MAGENTA color."""
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

class Curses:
    @staticmethod
    def wrapper(func):
        """Wrapper that resets terminal and returns the function's return value"""
        # CRITICAL: Reset terminal colors BEFORE opening curses
        print(Style.RESET_ALL, end='', flush=True)
        sys.stdout.write('\033[0m')  # Additional ANSI reset
        sys.stdout.flush()

        # Call curses.wrapper and return its result
        return curses.wrapper(func)

class CursesLoginScreen:
    """Modern sleek login interface using curses"""
    
    def __init__(self, users):
        self.users = users
        self.username = ""
        self.password = ""
        self.mode = "menu"
        self.selected_option = 0
        self.input_field = "username"
        self.message = ""
        self.message_color = curses.COLOR_GREEN
        
    def draw_title(self, stdscr, y_offset=2):
        """Draw the KAIRO title"""
        height, width = stdscr.getmaxyx()
        
        title_lines = [
            "█▄▀ ▄▀█ █ █▀█ █▀█",
            "█ █ █▀█ █ █▀▄ █▄█"
        ]
        
        for i, line in enumerate(title_lines):
            x_pos = (width - len(line)) // 2
            try:
                stdscr.addstr(y_offset + i, x_pos, line, curses.color_pair(2) | curses.A_BOLD)
            except curses.error:
                pass
    
    def draw_menu(self, stdscr):
        """Draw the main menu"""
        height, width = stdscr.getmaxyx()
        
        stdscr.clear()
        
        self.draw_title(stdscr, 3)
        
        options = ["LOGIN", "CREATE USER", "REMOVE USER"]
        menu_y = height // 2
        
        for i, option in enumerate(options):
            y_pos = menu_y + (i * 2)
            x_pos = (width - len(option) - 4) // 2
            
            if i == self.selected_option:
                prefix = "▶ "
                suffix = " ◀"
                color = curses.color_pair(1) | curses.A_BOLD
            else:
                prefix = "  "
                suffix = "  "
                color = curses.A_NORMAL
            
            display = f"{prefix}{option}{suffix}"
            try:
                stdscr.addstr(y_pos, x_pos, display, color)
            except curses.error:
                pass
        
        help_y = height - 2
        help_text = "↑/↓: Navigate  |  Enter: Select  |  Esc: Quit"
        try:
            stdscr.addstr(help_y, (width - len(help_text)) // 2, help_text, curses.color_pair(3))
        except curses.error:
            pass
        
        stdscr.refresh()
    
    def draw_login(self, stdscr):
        """Draw the login screen"""
        height, width = stdscr.getmaxyx()
        
        stdscr.clear()
        
        self.draw_title(stdscr, 2)
        
        box_width = 50
        box_height = 12
        box_y = (height - box_height) // 2
        box_x = (width - box_width) // 2
        
        try:
            for i in range(box_height):
                if i == 0:
                    stdscr.addstr(box_y + i, box_x, "╔" + "═" * (box_width - 2) + "╗", curses.color_pair(2))
                elif i == box_height - 1:
                    stdscr.addstr(box_y + i, box_x, "╚" + "═" * (box_width - 2) + "╝", curses.color_pair(2))
                else:
                    stdscr.addstr(box_y + i, box_x, "║" + " " * (box_width - 2) + "║", curses.color_pair(2))
        except curses.error:
            pass
        
        username_y = box_y + 3
        label_x = box_x + 4
        field_x = box_x + 15
        field_width = box_width - 17
        
        try:
            username_color = curses.color_pair(1) if self.input_field == "username" else curses.A_NORMAL
            stdscr.addstr(username_y, label_x, "Username:", username_color | curses.A_BOLD)
            
            field_bg = "─" * field_width
            stdscr.addstr(username_y, field_x, field_bg, curses.A_DIM)
            
            display_username = self.username[:field_width]
            stdscr.addstr(username_y, field_x, display_username, curses.color_pair(1) | curses.A_BOLD)
        except curses.error:
            pass
        
        password_y = box_y + 6
        
        try:
            password_color = curses.color_pair(1) if self.input_field == "password" else curses.A_NORMAL
            stdscr.addstr(password_y, label_x, "Password:", password_color | curses.A_BOLD)
            
            field_bg = "─" * field_width
            stdscr.addstr(password_y, field_x, field_bg, curses.A_DIM)
            
            display_password = "•" * len(self.password[:field_width])
            stdscr.addstr(password_y, field_x, display_password, curses.color_pair(1) | curses.A_BOLD)
        except curses.error:
            pass
        
        if self.message:
            msg_y = box_y + 9
            msg_x = box_x + (box_width - len(self.message)) // 2
            try:
                stdscr.addstr(msg_y, msg_x, self.message, curses.color_pair(4 if self.message_color == curses.COLOR_RED else 3))
            except curses.error:
                pass
        
        help_y = height - 2
        help_text = "Tab: Switch Field  |  Enter: Submit  |  Esc: Back"
        try:
            stdscr.addstr(help_y, (width - len(help_text)) // 2, help_text, curses.color_pair(3))
        except curses.error:
            pass
        
        stdscr.refresh()
    
    def run(self, stdscr):
        """Main login loop"""
        stdscr.attrset(0)
        stdscr.bkgd(' ')
        stdscr.clear()
        stdscr.refresh()
        
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_YELLOW, -1)
        curses.init_pair(2, curses.COLOR_MAGENTA, -1)
        curses.init_pair(3, curses.COLOR_CYAN, -1)
        curses.init_pair(4, curses.COLOR_RED, -1)
        
        curses.curs_set(0)
        stdscr.keypad(True)
        stdscr.timeout(100)
        
        while True:
            if self.mode == "menu":
                self.draw_menu(stdscr)
                
                ch = stdscr.getch()
                
                if ch == -1:
                    continue
                
                try:
                    keyname = curses.keyname(ch).decode()
                except:
                    keyname = ''
                
                if keyname in ('KEY_UP', 'KEY_A2') or ch in (curses.KEY_UP, 259, 450):
                    self.selected_option = (self.selected_option - 1) % 3
                elif keyname in ('KEY_DOWN', 'KEY_C2') or ch in (curses.KEY_DOWN, 258, 456):
                    self.selected_option = (self.selected_option + 1) % 3
                elif ch in (ord('\n'), ord('\r'), curses.KEY_ENTER, 10, 13):
                    if self.selected_option == 0:
                        self.mode = "login"
                        self.username = ""
                        self.password = ""
                        self.input_field = "username"
                        self.message = ""
                    elif self.selected_option == 1:
                        self.mode = "create"
                        self.username = ""
                        self.password = ""
                        self.input_field = "username"
                        self.message = ""
                    elif self.selected_option == 2:
                        self.mode = "remove"
                        self.username = ""
                        self.password = ""
                        self.input_field = "username"
                        self.message = ""
                elif ch == 27:
                    return ("exit", None)
            
            elif self.mode in ("login", "create", "remove"):
                self.draw_login(stdscr)
                
                ch = stdscr.getch()
                
                if ch == -1:
                    continue
                
                if ch == 27:
                    self.mode = "menu"
                elif ch == 9:
                    self.input_field = "password" if self.input_field == "username" else "username"
                    self.message = ""
                elif ch in (ord('\n'), ord('\r'), curses.KEY_ENTER, 10, 13):
                    if self.mode == "login":
                        user = UserManager.match_user(self.users, self.username)
                        if not user:
                            self.message = "User not found"
                            self.message_color = curses.COLOR_RED
                        elif user.password != self.password:
                            self.message = "Incorrect password"
                            self.message_color = curses.COLOR_RED
                        else:
                            return ("login", user.username)
                    
                    elif self.mode == "create":
                        if any(u.username.lower() == self.username.lower() for u in self.users):
                            self.message = "Username already exists"
                            self.message_color = curses.COLOR_RED
                        elif len(self.username) == 0:
                            self.message = "Username required"
                            self.message_color = curses.COLOR_RED
                        elif len(self.password) == 0:
                            self.message = "Password required"
                            self.message_color = curses.COLOR_RED
                        else:
                            return ("create", (self.username, self.password))
                    
                    elif self.mode == "remove":
                        user = UserManager.match_user(self.users, self.username)
                        if not user:
                            self.message = "User not found"
                            self.message_color = curses.COLOR_RED
                        elif user.password != self.password:
                            self.message = "Incorrect password"
                            self.message_color = curses.COLOR_RED
                        else:
                            return ("remove", user.username)
                
                elif ch in (curses.KEY_BACKSPACE, 127, 8):
                    if self.input_field == "username" and self.username:
                        self.username = self.username[:-1]
                    elif self.input_field == "password" and self.password:
                        self.password = self.password[:-1]
                    self.message = ""
                
                elif 32 <= ch <= 126:
                    if self.input_field == "username":
                        if len(self.username) < 30:
                            self.username += chr(ch)
                    elif self.input_field == "password":
                        if len(self.password) < 30:
                            self.password += chr(ch)
                    self.message = ""

class CursesEditor:
    """A full-featured terminal text editor using curses (nano-like interface)"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.original_filepath = filepath  # Track original path
        self.lines: List[str] = []
        self.cursor_y = 0
        self.cursor_x = 0
        self.offset_y = 0  # Vertical scroll offset
        self.offset_x = 0  # Horizontal scroll offset
        self.modified = False
        self.status_message = ""
        self.status_timeout = 0
        self.clipboard = []  # Clipboard for cut/copy/paste
        # Undo/Redo system
        self.undo_stack = []  # Stack of (action_type, data) tuples
        self.redo_stack = []  # Stack of undone actions
        self.max_undo = 1000   # Maximum undo history
        
        # Selection state
        self.selection_start = None  # (y, x) tuple
        self.selection_end = None    # (y, x) tuple
        self.selecting = False       # True while shift is held
        
        # Track file state
        self.file_existed = os.path.exists(filepath)
        self.was_renamed = False
        self.was_deleted = False
        self.was_saved = False
        
        # Load file content
        self._load_file()

    def _load_file(self):
        """Load file content into lines array"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content:
                        self.lines = content.split('\n')
                    else:
                        self.lines = ['']
            except Exception as e:
                self.lines = ['']
                self.status_message = f"Error loading file: {str(e)}"
        else:
            self.lines = ['']
    
    def _save_file(self) -> bool:
        """Save current content to file"""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.lines))
            self.modified = False
            self.was_saved = True
            self.status_message = f"[ Wrote {len(self.lines)} lines to {os.path.basename(self.filepath)} ]"
            self.status_timeout = 20
            return True
        except Exception as e:
            self.status_message = f"Error saving: {str(e)}"
            self.status_timeout = 20
            return False
    
    def _get_file_info(self) -> str:
        """Get file metadata information"""
        try:
            stat = os.stat(self.filepath)
            size = stat.st_size
            modified_time = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %I:%M:%S %p')
            
            # Format size
            if size < 1024:
                size_str = f"{size}B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f}KB"
            else:
                size_str = f"{size / (1024 * 1024):.1f}MB"
            
            return f"[ {os.path.basename(self.filepath)} | {size_str} | Modified: {modified_time} | Lines: {len(self.lines)} ]"
        except Exception as e:
            return f"[ Error getting file info: {str(e)} ]"
        
    def _force_clear_help_bar(self, stdscr):
        """Force clear the help bar by overwriting with default help text"""
        height, width = stdscr.getmaxyx()
        help_y = height - 1
        help_text = " ^S_Save  ^Z_Undo  ^Y_Redo  ^X_Cut  ^O_Copy  ^P_Paste  ^A_Select All  ^F_Find  ^I_Info  ^R_Rename  ^D_Delete  Esc_Quit"
        try:
            stdscr.addstr(help_y, 0, help_text[:width].ljust(width)[:width], curses.color_pair(3))
            stdscr.refresh()
        except curses.error:
            pass
    
    def _set_status(self, message: str, timeout: int = 10):
        """Set status message with timeout"""
        self.status_message = message
        self.status_timeout = timeout
    
    def _get_selection_bounds(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Get normalized selection bounds (start always before end)"""
        if self.selection_start is None or self.selection_end is None:
            return None, None
        
        start = self.selection_start
        end = self.selection_end
        
        # Normalize so start is before end
        if start[0] > end[0] or (start[0] == end[0] and start[1] > end[1]):
            start, end = end, start
        
        return start, end
    
    def _delete_selection(self):
        """Delete the current selection"""
        start, end = self._get_selection_bounds()
        if start is None:
            return
        
        start_y, start_x = start
        end_y, end_x = end

        # Save undo state BEFORE deleting
        deleted_lines = self.lines[start_y:end_y+1].copy()
        self._save_undo_state('delete_selection', {
            'start': start,
            'end': end,
            'deleted_lines': deleted_lines
        })
        
        if start_y == end_y:
            # Single line selection
            self.lines[start_y] = self.lines[start_y][:start_x] + self.lines[start_y][end_x:]
        else:
            # Multi-line selection
            # Keep beginning of start line and end of end line
            self.lines[start_y] = self.lines[start_y][:start_x] + self.lines[end_y][end_x:]
            # Remove lines in between
            del self.lines[start_y + 1:end_y + 1]
        
        self.cursor_y = start_y
        self.cursor_x = start_x
        self.modified = True
        self._clear_selection()
    
    def _get_selected_text(self) -> str:
        """Get the text within the current selection"""
        start, end = self._get_selection_bounds()
        if start is None:
            return ""
        
        start_y, start_x = start
        end_y, end_x = end
        
        if start_y == end_y:
            # Single line
            return self.lines[start_y][start_x:end_x]
        else:
            # Multiple lines
            result = [self.lines[start_y][start_x:]]
            for y in range(start_y + 1, end_y):
                result.append(self.lines[y])
            result.append(self.lines[end_y][:end_x])
            return '\n'.join(result)
    
    def _clear_selection(self):
        """Clear the selection"""
        self.selection_start = None
        self.selection_end = None
        self.selecting = False

    def _handle_arrow_with_selection(self, direction):
        """Handle arrow key press when selection is active (shift released)"""
        if self.selection_start is None:
            return
        
        start, end = self._get_selection_bounds()
        if start is None:
            return
        
        start_y, start_x = start
        end_y, end_x = end
        
        if direction == 'left':
            # Jump to beginning of selection, then move left one character
            self.cursor_y = start_y
            self.cursor_x = start_x
            # Now move left
            if self.cursor_x > 0:
                self.cursor_x -= 1
            elif self.cursor_y > 0:
                self.cursor_y -= 1
                self.cursor_x = len(self.lines[self.cursor_y])
                
        elif direction == 'right':
            # Jump to end of selection, then move right one character
            self.cursor_y = end_y
            self.cursor_x = end_x
            # Now move right
            if self.cursor_x < len(self.lines[self.cursor_y]):
                self.cursor_x += 1
            elif self.cursor_y < len(self.lines) - 1:
                self.cursor_y += 1
                self.cursor_x = 0
                
        elif direction == 'up':
            # Jump to beginning of selection, then move up one line
            self.cursor_y = start_y
            self.cursor_x = start_x
            # Now move up
            if self.cursor_y > 0:
                self.cursor_y -= 1
                self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))
            else:
                # Already at top, just go to beginning of line
                self.cursor_x = 0
                
        elif direction == 'down':
            # Jump to end of selection, then move down one line
            self.cursor_y = end_y
            self.cursor_x = end_x
            # Now move down
            if self.cursor_y < len(self.lines) - 1:
                self.cursor_y += 1
                self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))
            else:
                # Already at bottom, just go to end of line
                self.cursor_x = len(self.lines[self.cursor_y])
        
        # Clear selection after jump
        self._clear_selection()
        
    def _ensure_valid_cursor(self):
        """Ensure cursor position is within valid bounds"""
        if not self.lines:
            self.lines = ['']
        
        # Clamp cursor_y
        self.cursor_y = max(0, min(len(self.lines) - 1, self.cursor_y))
        
        # Clamp cursor_x to current line length
        if self.cursor_y < len(self.lines):
            max_x = len(self.lines[self.cursor_y])
            self.cursor_x = max(0, min(max_x, self.cursor_x))
    
    def _save_undo_state(self, action_type: str, data: dict):
        """Save current state for undo"""
        self.undo_stack.append((action_type, data))
        # Limit undo stack size
        if len(self.undo_stack) > self.max_undo:
            self.undo_stack.pop(0)
        # Clear redo stack when new action is performed
        self.redo_stack.clear()

    def _undo(self):
        """Undo last action"""
        if not self.undo_stack:
            self._set_status("Nothing to undo")
            return
        
        action_type, data = self.undo_stack.pop()
        
        try:
            # Save current state for redo before undoing
            if action_type == 'insert_char':
                redo_data = {
                    'y': data['y'],
                    'x': data['x'],
                    'char': data['char'],
                    'old_line': self.lines[data['y']] if data['y'] < len(self.lines) else ''
                }
                self.redo_stack.append(('insert_char', redo_data))
                
                if data['y'] < len(self.lines):
                    self.lines[data['y']] = data['old_line']
                self.cursor_y = data['y']
                self.cursor_x = data['x']
                
            elif action_type == 'delete_char':
                redo_data = {
                    'y': data['y'],
                    'x': data['x'],
                    'char': data['char'],
                    'old_line': self.lines[data['y']] if data['y'] < len(self.lines) else ''
                }
                self.redo_stack.append(('delete_char', redo_data))
                
                if data['y'] < len(self.lines):
                    self.lines[data['y']] = data['old_line']
                self.cursor_y = data['y']
                self.cursor_x = data['x']
                
            elif action_type == 'delete_char_forward':
                redo_data = {
                    'y': data['y'],
                    'x': data['x'],
                    'old_line': self.lines[data['y']] if data['y'] < len(self.lines) else ''
                }
                self.redo_stack.append(('delete_char_forward', redo_data))
                
                if data['y'] < len(self.lines):
                    self.lines[data['y']] = data['old_line']
                self.cursor_y = data['y']
                self.cursor_x = data['x']
                
            elif action_type == 'insert_line':
                redo_data = {
                    'y': data['y'],
                    'old_line': data['old_line'],
                    'new_line': data['new_line']
                }
                self.redo_stack.append(('insert_line', redo_data))
                
                if data['y'] < len(self.lines):
                    self.lines[data['y']] = data['old_line']
                if data['y'] + 1 < len(self.lines):
                    del self.lines[data['y'] + 1]
                self.cursor_y = data['y']
                self.cursor_x = data.get('x', 0)
                
            elif action_type == 'join_lines':
                redo_data = {
                    'y': data['y'],
                    'old_line': self.lines[data['y']] if data['y'] < len(self.lines) else ''
                }
                self.redo_stack.append(('join_lines', redo_data))
                
                if data['y'] < len(self.lines):
                    self.lines[data['y']] = data['line1']
                    self.lines.insert(data['y'] + 1, data['line2'])
                self.cursor_y = data['y']
                self.cursor_x = data.get('x', 0)
            
            elif action_type == 'paste':
                redo_data = {
                    'y': data['y'],
                    'x': data['x'],
                    'text': data['text'],
                    'old_line': data['old_line']
                }
                self.redo_stack.append(('paste', redo_data))
                
                if data['y'] < len(self.lines):
                    self.lines[data['y']] = data['old_line']
                self.cursor_y = data['y']
                self.cursor_x = data['x']

            elif action_type == 'paste_multiline':
                redo_data = {
                    'old_lines': self.lines.copy(),
                    'old_cursor_y': self.cursor_y,
                    'old_cursor_x': self.cursor_x,
                    'new_cursor_y': data['new_cursor_y'],
                    'new_cursor_x': data['new_cursor_x'],
                    'paste_text': data['paste_text']
                }
                self.redo_stack.append(('paste_multiline', redo_data))
                
                self.lines = data['old_lines'].copy()
                self.cursor_y = data['old_cursor_y']
                self.cursor_x = data['old_cursor_x']
            
            elif action_type == 'delete_selection':
                redo_data = {
                    'start': data['start'],
                    'end': data['end'],
                    'deleted_lines': data['deleted_lines']
                }
                self.redo_stack.append(('delete_selection', redo_data))
                
                start_y, start_x = data['start']
                end_y, end_x = data['end']
                
                if start_y < len(self.lines):
                    self.lines[start_y:end_y+1] = data['deleted_lines']
                self.cursor_y = start_y
                self.cursor_x = start_x
            
            elif action_type == 'replace_single':
                # Undo single replacement
                redo_data = {
                    'y': data['y'],
                    'x': data['x'],
                    'old_line': self.lines[data['y']] if data['y'] < len(self.lines) else '',
                    'search_term': data['search_term'],
                    'replace_text': data['replace_text']
                }
                self.redo_stack.append(('replace_single', redo_data))
                
                if data['y'] < len(self.lines):
                    self.lines[data['y']] = data['old_line']
                self.cursor_y = data['y']
                self.cursor_x = data['x']
            
            elif action_type == 'replace_all':
                # Undo replace all
                redo_data = {
                    'old_lines': self.lines.copy(),
                    'search_term': data['search_term'],
                    'replace_text': data['replace_text'],
                    'count': data['count']
                }
                self.redo_stack.append(('replace_all', redo_data))
                
                self.lines = data['old_lines'].copy()
            
            self._clear_selection()
            self._set_status("Undo")
            self._ensure_valid_cursor()
            
        except (IndexError, KeyError) as e:
            self._set_status(f"Undo failed: {str(e)}")
            self._ensure_valid_cursor()
                
    def _redo(self):
        """Redo last undone action"""
        if not self.redo_stack:
            self._set_status("Nothing to redo")
            return
        
        action_type, data = self.redo_stack.pop()
        
        try:
            if action_type == 'insert_char':
                old_line = self.lines[data['y']] if data['y'] < len(self.lines) else ''
                if data['y'] < len(self.lines):
                    self.lines[data['y']] = data['old_line']
                self.cursor_y = data['y']
                self.cursor_x = data['x'] + 1
                self.undo_stack.append(('insert_char', {
                    'y': data['y'],
                    'x': data['x'],
                    'char': data['char'],
                    'old_line': old_line
                }))
                
            elif action_type == 'delete_char':
                old_line = self.lines[data['y']] if data['y'] < len(self.lines) else ''
                if data['y'] < len(self.lines):
                    self.lines[data['y']] = data['old_line']
                self.cursor_y = data['y']
                self.cursor_x = data['x']
                self.undo_stack.append(('delete_char', {
                    'y': data['y'],
                    'x': data['x'],
                    'char': data['char'],
                    'old_line': old_line
                }))
            
            elif action_type == 'delete_char_forward':
                old_line = self.lines[data['y']] if data['y'] < len(self.lines) else ''
                if data['y'] < len(self.lines):
                    self.lines[data['y']] = data['old_line']
                self.cursor_y = data['y']
                self.cursor_x = data['x']
                self.undo_stack.append(('delete_char_forward', {
                    'y': data['y'],
                    'x': data['x'],
                    'old_line': old_line
                }))
            
            elif action_type == 'insert_line':
                if data['y'] < len(self.lines):
                    self.lines[data['y']] = data['old_line']
                    self.lines.insert(data['y'] + 1, data['new_line'])
                self.cursor_y = data['y'] + 1
                self.cursor_x = 0
                self.undo_stack.append(('insert_line', data))
            
            elif action_type == 'join_lines':
                saved_lines = []
                if data['y'] < len(self.lines):
                    saved_lines.append(self.lines[data['y']])
                if data['y'] + 1 < len(self.lines):
                    saved_lines.append(self.lines[data['y'] + 1])
                else:
                    saved_lines.append('')
                    
                if data['y'] < len(self.lines):
                    self.lines[data['y']] = data['old_line']
                if data['y'] + 1 < len(self.lines):
                    del self.lines[data['y'] + 1]
                self.cursor_y = data['y']
                self.cursor_x = len(data.get('line1', ''))
                self.undo_stack.append(('join_lines', {
                    'y': data['y'],
                    'x': len(data.get('line1', '')),
                    'line1': saved_lines[0] if saved_lines else '',
                    'line2': saved_lines[1] if len(saved_lines) > 1 else '',
                    'old_line': data['old_line']
                }))
            
            elif action_type == 'paste':
                old_line = self.lines[data['y']] if data['y'] < len(self.lines) else ''
                if data['y'] < len(self.lines):
                    line = self.lines[data['y']]
                    new_line = line[:data['x']] + data['text'] + line[data['x']:]
                    self.lines[data['y']] = new_line
                self.cursor_y = data['y']
                self.cursor_x = data['x'] + len(data['text'])
                self.undo_stack.append(('paste', {
                    'y': data['y'],
                    'x': data['x'],
                    'text': data['text'],
                    'old_line': old_line
                }))

            elif action_type == 'paste_multiline':
                old_lines_state = self.lines.copy()
                old_cursor_y_state = self.cursor_y
                old_cursor_x_state = self.cursor_x
                
                self.lines = data['old_lines'].copy()
                self.cursor_y = data['new_cursor_y']
                self.cursor_x = data['new_cursor_x']
                
                self.undo_stack.append(('paste_multiline', {
                    'old_lines': old_lines_state,
                    'old_cursor_y': old_cursor_y_state,
                    'old_cursor_x': old_cursor_x_state,
                    'new_cursor_y': data['new_cursor_y'],
                    'new_cursor_x': data['new_cursor_x'],
                    'paste_text': data['paste_text']
                }))
            
            elif action_type == 'delete_selection':
                start_y, start_x = data['start']
                end_y, end_x = data['end']
                deleted_lines = []
                if start_y < len(self.lines) and end_y < len(self.lines):
                    deleted_lines = self.lines[start_y:end_y+1].copy()
                
                if start_y < len(self.lines) and end_y < len(self.lines):
                    if start_y == end_y:
                        self.lines[start_y] = self.lines[start_y][:start_x] + self.lines[start_y][end_x:]
                    else:
                        self.lines[start_y] = self.lines[start_y][:start_x] + self.lines[end_y][end_x:]
                        del self.lines[start_y + 1:end_y + 1]
                
                self.cursor_y = start_y
                self.cursor_x = start_x
                self.undo_stack.append(('delete_selection', {
                    'start': data['start'],
                    'end': data['end'],
                    'deleted_lines': deleted_lines
                }))
            
            elif action_type == 'replace_single':
                # Redo single replacement
                old_line = self.lines[data['y']] if data['y'] < len(self.lines) else ''
                
                if data['y'] < len(self.lines):
                    self.lines[data['y']] = data['old_line']
                
                self.undo_stack.append(('replace_single', {
                    'y': data['y'],
                    'x': data['x'],
                    'old_line': old_line,
                    'search_term': data['search_term'],
                    'replace_text': data['replace_text']
                }))
                
                self.cursor_y = data['y']
                self.cursor_x = data['x']
            
            elif action_type == 'replace_all':
                # Redo replace all
                old_lines_state = self.lines.copy()
                
                self.lines = data['old_lines'].copy()
                
                self.undo_stack.append(('replace_all', {
                    'old_lines': old_lines_state,
                    'search_term': data['search_term'],
                    'replace_text': data['replace_text'],
                    'count': data['count']
                }))
            
            self._clear_selection()
            self._set_status("Redo")
            self._ensure_valid_cursor()
            
        except (IndexError, KeyError) as e:
            self._set_status(f"Redo failed: {str(e)}")
            self._ensure_valid_cursor()           
    
    def _insert_char(self, ch: int):
        """Insert character at cursor position"""
        # Delete selection if exists
        if self.selection_start is not None:
            self._delete_selection()
        
        # Ensure we have valid lines
        if not self.lines:
            self.lines = ['']
        
        # Ensure cursor_y is valid
        if self.cursor_y >= len(self.lines):
            self.cursor_y = len(self.lines) - 1
        
        if ch == 10:  # Enter key
            # Split line at cursor
            current_line = self.lines[self.cursor_y]
            old_line = current_line
            new_first = current_line[:self.cursor_x]
            new_second = current_line[self.cursor_x:]
            
            # Save undo state
            self._save_undo_state('insert_line', {
                'y': self.cursor_y,
                'x': self.cursor_x,
                'old_line': old_line,
                'new_line': new_second
            })
            
            self.lines[self.cursor_y] = new_first
            self.lines.insert(self.cursor_y + 1, new_second)
            self.cursor_y += 1
            self.cursor_x = 0
            self.modified = True
        elif ch == 9:  # Tab key
            # Insert 4 spaces
            old_line = self.lines[self.cursor_y]
            
            # Save undo state
            self._save_undo_state('insert_char', {
                'y': self.cursor_y,
                'x': self.cursor_x,
                'char': '    ',
                'old_line': old_line
            })
            
            self.lines[self.cursor_y] = (
                self.lines[self.cursor_y][:self.cursor_x] + 
                '    ' + 
                self.lines[self.cursor_y][self.cursor_x:]
            )
            self.cursor_x += 4
            self.modified = True
        elif 32 <= ch <= 126:  # Printable ASCII
            # Insert character
            char = chr(ch)
            old_line = self.lines[self.cursor_y]
            
            # Save undo state
            self._save_undo_state('insert_char', {
                'y': self.cursor_y,
                'x': self.cursor_x,
                'char': char,
                'old_line': old_line
            })
            
            self.lines[self.cursor_y] = (
                self.lines[self.cursor_y][:self.cursor_x] + 
                char + 
                self.lines[self.cursor_y][self.cursor_x:]
            )
            self.cursor_x += 1
            self.modified = True
    
    def _delete_char(self):
        """Delete character at cursor (Backspace)"""
        # If there's a selection, delete it
        if self.selection_start is not None:
            self._delete_selection()
            return
        
        if self.cursor_x > 0:
            # Delete character before cursor
            old_line = self.lines[self.cursor_y]
            deleted_char = self.lines[self.cursor_y][self.cursor_x - 1]
            
            # Save undo state
            self._save_undo_state('delete_char', {
                'y': self.cursor_y,
                'x': self.cursor_x - 1,
                'char': deleted_char,
                'old_line': old_line
            })
            
            self.lines[self.cursor_y] = (
                self.lines[self.cursor_y][:self.cursor_x - 1] + 
                self.lines[self.cursor_y][self.cursor_x:]
            )
            self.cursor_x -= 1
            self.modified = True
        elif self.cursor_y > 0:
            # Join with previous line
            prev_line = self.lines[self.cursor_y - 1]
            current_line = self.lines[self.cursor_y]
            
            # Save undo state
            self._save_undo_state('join_lines', {
                'y': self.cursor_y - 1,
                'x': len(prev_line),
                'line1': prev_line,
                'line2': current_line,
                'old_line': prev_line + current_line
            })
            
            self.cursor_x = len(prev_line)
            self.lines[self.cursor_y - 1] = prev_line + self.lines[self.cursor_y]
            del self.lines[self.cursor_y]
            self.cursor_y -= 1
            self.modified = True
    
    def _delete_char_forward(self):
        """Delete character at cursor (Delete key)"""
        # If there's a selection, delete it
        if self.selection_start is not None:
            self._delete_selection()
            return
        
        if self.cursor_x < len(self.lines[self.cursor_y]):
            # Delete character at cursor
            old_line = self.lines[self.cursor_y]
            
            # Save undo state
            self._save_undo_state('delete_char_forward', {
                'y': self.cursor_y,
                'x': self.cursor_x,
                'old_line': old_line
            })
            
            self.lines[self.cursor_y] = (
                self.lines[self.cursor_y][:self.cursor_x] + 
                self.lines[self.cursor_y][self.cursor_x + 1:]
            )
            self.modified = True
        elif self.cursor_y < len(self.lines) - 1:
            # Join with next line
            current_line = self.lines[self.cursor_y]
            next_line = self.lines[self.cursor_y + 1]
            
            # Save undo state
            self._save_undo_state('join_lines', {
                'y': self.cursor_y,
                'x': self.cursor_x,
                'line1': current_line,
                'line2': next_line,
                'old_line': current_line + next_line
            })
            
            self.lines[self.cursor_y] += self.lines[self.cursor_y + 1]
            del self.lines[self.cursor_y + 1]
            self.modified = True
    
    def _move_cursor(self, dy: int, dx: int):
        """Move cursor by delta, with bounds checking"""
        # Vertical movement
        self.cursor_y = max(0, min(len(self.lines) - 1, self.cursor_y + dy))
        
        # Horizontal movement
        max_x = len(self.lines[self.cursor_y])
        self.cursor_x = max(0, min(max_x, self.cursor_x + dx))
    
    def _adjust_scroll(self, height, width):
        """Adjust scroll offsets to keep cursor visible"""
        # Vertical scrolling (reserve 1 line for title + 1 line blank + 1 blank at bottom + 1 line for help)
        text_height = height - 4
        
        if self.cursor_y < self.offset_y:
            self.offset_y = self.cursor_y
        elif self.cursor_y >= self.offset_y + text_height:
            self.offset_y = self.cursor_y - text_height + 1
        
        # Horizontal scrolling
        text_width = width
        
        if self.cursor_x < self.offset_x:
            self.offset_x = self.cursor_x
        elif self.cursor_x >= self.offset_x + text_width:
            self.offset_x = self.cursor_x - text_width + 1

    def _draw_screen(self, stdscr):
        """Draw the entire screen with line numbers and padding"""
        height, width = stdscr.getmaxyx()
        
        # CRITICAL: Clear with explicit color reset
        stdscr.bkgdset(' ', 0)
        stdscr.clear()
        
        # Draw title bar at top (MAGENTA background, WHITE text) with time on right
        title_y = 0
        filename = os.path.basename(self.filepath)
        modified_indicator = " [Modified]" if self.modified else ""
        current_time = datetime.datetime.now().strftime('%I:%M %p')
        time_text = f"{current_time} "
        
        # Build title without time first
        title_content = f" EDITOR <> {filename}{modified_indicator} | Line {self.cursor_y + 1}/{len(self.lines)}, Col {self.cursor_x + 1}"
        
        # Calculate available width for title (leave room for time)
        available_width = width - len(time_text)
        padded_title = title_content[:available_width].ljust(available_width)
        full_title_line = padded_title + time_text
        
        try:
            stdscr.addstr(title_y, 0, full_title_line[:width], curses.color_pair(3))
        except curses.error:
            pass
        
        # Calculate line number column width (MINIMUM 2 CHARACTERS)
        total_lines = len(self.lines)
        line_num_width = max(2, len(str(total_lines)))
        line_num_separator = "│"
        gutter_width = line_num_width + len(line_num_separator) + 1
        
        # Adjust available width for text
        text_width = width - gutter_width
        
        # Get selection bounds
        sel_start, sel_end = self._get_selection_bounds()
        
        # PADDING: Start content at line 2 (line 1 is blank)
        content_start_y = 2
        # PADDING: Reserve 3 lines at bottom
        text_height = height - 4
        
        for i in range(text_height):
            line_num = i + self.offset_y
            if line_num < len(self.lines):
                # Draw line number with separator (right-aligned)
                line_number_str = f"{line_num + 1:>{line_num_width}}{line_num_separator} "
                try:
                    stdscr.addstr(content_start_y + i, 0, line_number_str, curses.color_pair(4))
                except curses.error:
                    pass
                
                # Get the visible portion of the line
                line = self.lines[line_num][self.offset_x:self.offset_x + text_width]
                
                try:
                    # Check if this line has selection
                    if sel_start and sel_end:
                        start_y, start_x = sel_start
                        end_y, end_x = sel_end
                        
                        if start_y <= line_num <= end_y:
                            # This line has selection
                            if line_num == start_y:
                                sel_x_start = max(0, start_x - self.offset_x)
                            else:
                                sel_x_start = 0
                            
                            if line_num == end_y:
                                sel_x_end = min(len(line), end_x - self.offset_x)
                            else:
                                sel_x_end = len(line)
                            
                            # Draw line in parts
                            x_pos = gutter_width
                            
                            # Before selection
                            if sel_x_start > 0:
                                stdscr.addstr(content_start_y + i, x_pos, line[:sel_x_start], 0)
                                x_pos += sel_x_start
                            
                            # Selection (highlighted)
                            if sel_x_end > sel_x_start:
                                sel_text = line[sel_x_start:sel_x_end]
                                stdscr.addstr(content_start_y + i, x_pos, sel_text, curses.A_REVERSE)
                                x_pos += len(sel_text)
                            
                            # After selection
                            if sel_x_end < len(line):
                                stdscr.addstr(content_start_y + i, x_pos, line[sel_x_end:], 0)
                        else:
                            # No selection on this line
                            stdscr.addstr(content_start_y + i, gutter_width, line[:text_width], 0)
                    else:
                        # No selection at all
                        stdscr.addstr(content_start_y + i, gutter_width, line[:text_width], 0)
                except curses.error:
                    pass
        
        # Show status message if active (replaces help bar temporarily)
        help_y = height - 1
        if self.status_message and self.status_timeout > 0:
            status_text = f" {self.status_message}"
            try:
                stdscr.addstr(help_y, 0, status_text.ljust(width)[:width], curses.color_pair(3))
            except curses.error:
                pass
        else:
            # Draw help bar (MAGENTA background, WHITE text)
            help_text = " ^S_Save  ^Z_Undo  ^Y_Redo  ^X_Cut  ^O_Copy  ^P_Paste  ^A_Select All  ^F_Find  ^I_Info  ^R_Rename  ^D_Delete  Esc_Quit"
            try:
                stdscr.addstr(help_y, 0, help_text[:width].ljust(width)[:width], curses.color_pair(3))
            except curses.error:
                pass
        
        # Position cursor
        screen_y = self.cursor_y - self.offset_y + content_start_y
        screen_x = self.cursor_x - self.offset_x + gutter_width
        if content_start_y <= screen_y < height - 2 and gutter_width <= screen_x < width:
            stdscr.move(screen_y, screen_x)
        
        stdscr.refresh()

    def _confirm_exit(self, stdscr) -> bool:
        """Ask user to confirm exit if modified"""
        if not self.modified:
            return True
        
        height, width = stdscr.getmaxyx()
        status_y = height - 1
        
        prompt = " Save modified file? (Y/N/C to cancel) "
        
        # Clear any buffered input first
        stdscr.nodelay(True)
        while stdscr.getch() != -1:
            pass
        stdscr.nodelay(False)
        
        try:
            stdscr.attron(curses.A_REVERSE)
            stdscr.addstr(status_y, 0, prompt.ljust(width)[:width])
            stdscr.attroff(curses.A_REVERSE)
            stdscr.refresh()
        except curses.error:
            pass
        
        while True:
            ch = stdscr.getch()
            
            if ch in (ord('y'), ord('Y')):
                if self._save_file():
                    return True
                else:
                    continue
            elif ch in (ord('n'), ord('N')):
                return True
            elif ch in (ord('c'), ord('C'), 27):  # C or Escape
                self._set_status("Exit cancelled")
                return False
    
    def _rename_file(self, stdscr):
        """Rename the current file (deferred until save)"""
        # Clear any active status messages AND force overwrite help bar BEFORE showing prompt
        self.status_message = ""
        self.status_timeout = 0
        self._force_clear_help_bar(stdscr)
        
        height, width = stdscr.getmaxyx()
        status_y = height - 2
            
        current_name = os.path.basename(self.filepath)
        prompt = f" Rename: "
        
        new_name = ""
        cursor_pos = len(prompt)
        
        stdscr.timeout(-1)
        
        while True:
            try:
                display_line = prompt + new_name
                stdscr.attron(curses.color_pair(3))
                stdscr.addstr(status_y, 0, display_line.ljust(width)[:width])
                stdscr.attroff(curses.color_pair(3))
                stdscr.move(status_y, cursor_pos)
                stdscr.refresh()
                
                ch = stdscr.getch()
                
                if ch in (ord('\n'), ord('\r'), curses.KEY_ENTER, 10, 13):
                    break
                elif ch == 27:
                    new_name = ""
                    break
                elif ch in (curses.KEY_BACKSPACE, 127, 8):
                    if new_name:
                        new_name = new_name[:-1]
                        cursor_pos -= 1
                elif 32 <= ch <= 126:
                    new_name += chr(ch)
                    cursor_pos += 1
            except Exception:
                break
        
        stdscr.timeout(100)
        
        if not new_name:
            self._set_status("Rename cancelled")
            return
        
        # Defer rename until save - just update the filepath
        new_path = os.path.join(os.path.dirname(self.filepath), new_name)
        
        # Check if target already exists (only if file was already created)
        if os.path.exists(new_path) and self.file_existed:
            self._set_status(f"Error: '{new_name}' already exists", timeout=30)
            return
        
        self.filepath = new_path
        self.was_renamed = True
        self.modified = True  # Force save to apply rename
        self._set_status(f"Will rename to '{new_name}' on save", timeout=20)

    def _delete_file(self, stdscr) -> bool:
        """Delete the current file with confirmation. Returns True if deleted (should exit editor)."""
        # Clear any active status messages before showing prompt
        self.status_message = ""
        self.status_timeout = 0
        
        height, width = stdscr.getmaxyx()
        status_y = height - 1
        
        filename = os.path.basename(self.filepath)
        
        # Different prompt for non-existent files
        if not self.file_existed:
            prompt = f" Cancel file creation? (Y/N) "
        else:
            prompt = f" Delete '{filename}'? (Y/N) "
        
        try:
            stdscr.attron(curses.A_REVERSE)
            stdscr.addstr(status_y, 0, prompt.ljust(width)[:width])
            stdscr.attroff(curses.A_REVERSE)
            stdscr.refresh()
        except curses.error:
            pass
        
        stdscr.timeout(-1)
        
        while True:
            ch = stdscr.getch()
            if ch in (ord('y'), ord('Y')):
                if self.file_existed:
                    # File exists - delete it
                    try:
                        os.remove(self.filepath)
                        self.was_deleted = True
                        stdscr.timeout(100)
                        return True
                    except Exception as e:
                        self._set_status(f"Delete failed: {str(e)}", timeout=30)
                        stdscr.timeout(100)
                        return False
                else:
                    # File doesn't exist yet - just mark as deleted (don't create)
                    self.was_deleted = True
                    stdscr.timeout(100)
                    return True
            elif ch in (ord('n'), ord('N'), 27):  # N or Escape
                if not self.file_existed:
                    self._set_status("Creation will continue")
                else:
                    self._set_status("Delete cancelled")
                stdscr.timeout(100)
                return False
        
    def _search(self, stdscr):
        """Search for text in the file with proper magenta background and replace option"""
        height, width = stdscr.getmaxyx()
        status_y = height - 2

        # FORCE OVERWRITE bottom bar with help text BEFORE prompting
        self._force_clear_help_bar(stdscr)

        prompt = " Search: "
        
        # CRITICAL: Reset colors explicitly before drawing search bar
        stdscr.bkgdset(' ', 0)
        stdscr.attrset(0)
        
        # Draw prompt with magenta background
        try:
            stdscr.attron(curses.color_pair(3))
            stdscr.addstr(status_y, 0, prompt.ljust(width)[:width])
            stdscr.attroff(curses.color_pair(3))
            stdscr.move(status_y, len(prompt))
            stdscr.refresh()
        except curses.error:
            pass

        # Manual input handling to preserve color
        search_term = ""
        cursor_pos = len(prompt)
        
        stdscr.timeout(-1)  # Blocking mode for input
        
        while True:
            try:
                # Redraw the line with current input
                display_line = prompt + search_term
                stdscr.attron(curses.color_pair(3))
                stdscr.addstr(status_y, 0, display_line.ljust(width)[:width])
                stdscr.attroff(curses.color_pair(3))
                stdscr.move(status_y, cursor_pos)
                stdscr.refresh()
                
                ch = stdscr.getch()
                
                if ch in (ord('\n'), ord('\r'), curses.KEY_ENTER, 10, 13):  # Enter
                    break
                elif ch == 27:  # Escape
                    search_term = ""
                    break
                elif ch in (curses.KEY_BACKSPACE, 127, 8):  # Backspace
                    if search_term:
                        search_term = search_term[:-1]
                        cursor_pos -= 1
                elif 32 <= ch <= 126:  # Printable characters
                    search_term += chr(ch)
                    cursor_pos += 1
            except Exception:
                break
        
        stdscr.timeout(100)  # Restore non-blocking mode

        if not search_term:
            self._set_status("Search cancelled")
            return

        # Perform search
        found = False
        found_y, found_x = -1, -1
        start_y, start_x = self.cursor_y, self.cursor_x + 1
        
        for y in range(start_y, len(self.lines)):
            pos = self.lines[y].lower().find(search_term.lower(), start_x if y == start_y else 0)
            if pos >= 0:
                found_y, found_x = y, pos
                found = True
                break

        if not found:
            for y in range(0, start_y + 1):
                pos = self.lines[y].lower().find(search_term.lower())
                if pos >= 0:
                    found_y, found_x = y, pos
                    found = True
                    break

        if not found:
            self._set_status(f"Not found: {search_term}")
            return
        
        # Found the search term - move cursor to END of selection and select it
        self.cursor_y, self.cursor_x = found_y, found_x + len(search_term)
        self.selection_start = (found_y, found_x)
        self.selection_end = (found_y, found_x + len(search_term))
        self.selecting = False
        self._set_status(f"Found: {search_term}")
        
        # Redraw to show the found position
        self._draw_screen(stdscr)
        
        # ROOT FIX: Clear help bar BEFORE showing replace prompt
        self._force_clear_help_bar(stdscr)
        
        # Ask if user wants to replace - STRICT KEY CHECKING
        replace_prompt = " Replace? (Y/N) "
        try:
            stdscr.attron(curses.color_pair(3))
            stdscr.addstr(status_y, 0, replace_prompt.ljust(width)[:width])
            stdscr.attroff(curses.color_pair(3))
            stdscr.refresh()
        except curses.error:
            pass
        
        stdscr.timeout(-1)
        while True:
            replace_choice = stdscr.getch()
            if replace_choice in (ord('y'), ord('Y')):
                break
            elif replace_choice in (ord('n'), ord('N'), 27):  # N or Escape
                self._set_status("Replace cancelled")
                stdscr.timeout(100)
                return
        stdscr.timeout(100)
        
        # ROOT FIX: Clear help bar BEFORE showing replacement text prompt
        self._force_clear_help_bar(stdscr)
        
        # Get replacement text
        replace_prompt = " Replace with: "
        replace_text = ""
        cursor_pos = len(replace_prompt)
        
        stdscr.timeout(-1)
        
        while True:
            try:
                display_line = replace_prompt + replace_text
                stdscr.attron(curses.color_pair(3))
                stdscr.addstr(status_y, 0, display_line.ljust(width)[:width])
                stdscr.attroff(curses.color_pair(3))
                stdscr.move(status_y, cursor_pos)
                stdscr.refresh()
                
                ch = stdscr.getch()
                
                if ch in (ord('\n'), ord('\r'), curses.KEY_ENTER, 10, 13):
                    break
                elif ch == 27:  # Escape
                    replace_text = None
                    break
                elif ch in (curses.KEY_BACKSPACE, 127, 8):
                    if replace_text:
                        replace_text = replace_text[:-1]
                        cursor_pos -= 1
                elif 32 <= ch <= 126:
                    replace_text += chr(ch)
                    cursor_pos += 1
            except Exception:
                break
        
        stdscr.timeout(100)
        
        if replace_text is None:
            self._set_status("Replace cancelled")
            return
        
        # ROOT FIX: Clear help bar BEFORE showing replace all prompt
        self._force_clear_help_bar(stdscr)
        
        # Ask if replace all - STRICT KEY CHECKING
        replace_all_prompt = " Replace all occurrences? (Y/N) "
        try:
            stdscr.attron(curses.color_pair(3))
            stdscr.addstr(status_y, 0, replace_all_prompt.ljust(width)[:width])
            stdscr.attroff(curses.color_pair(3))
            stdscr.refresh()
        except curses.error:
            pass
        
        stdscr.timeout(-1)
        while True:
            replace_all_choice = stdscr.getch()
            if replace_all_choice in (ord('y'), ord('Y')):
                # Replace all occurrences
                count = 0
                
                # Save undo state BEFORE replacing all
                old_lines = self.lines.copy()
                
                for y in range(len(self.lines)):
                    line = self.lines[y]
                    new_line = ""
                    search_lower = search_term.lower()
                    i = 0
                    
                    while i < len(line):
                        if i + len(search_term) <= len(line) and line[i:i+len(search_term)].lower() == search_lower:
                            new_line += replace_text
                            i += len(search_term)
                            count += 1
                        else:
                            new_line += line[i]
                            i += 1
                    
                    self.lines[y] = new_line
                
                # Save undo state for replace all
                self._save_undo_state('replace_all', {
                    'old_lines': old_lines,
                    'search_term': search_term,
                    'replace_text': replace_text,
                    'count': count
                })
                
                self.modified = True
                self._set_status(f"Replaced {count} occurrence(s)")
                stdscr.timeout(100)
                break
                
            elif replace_all_choice in (ord('n'), ord('N'), 27):  # N or Escape
                # Replace only this occurrence
                line = self.lines[found_y]
                old_line = line
                
                # Save undo state BEFORE replacing single
                self._save_undo_state('replace_single', {
                    'y': found_y,
                    'x': found_x,
                    'old_line': old_line,
                    'search_term': search_term,
                    'replace_text': replace_text
                })
                
                self.lines[found_y] = line[:found_x] + replace_text + line[found_x + len(search_term):]
                self.modified = True
                
                # Select the replacement text
                self.cursor_x = found_x
                self.selection_start = (found_y, found_x)
                self.selection_end = (found_y, found_x + len(replace_text))
                self.selecting = False
                self._set_status("Replaced 1 occurrence")
                stdscr.timeout(100)
                break

    def run(self, stdscr):
        """Main editor loop"""
        # CRITICAL: Force terminal reset BEFORE doing anything
        stdscr.attrset(0)
        stdscr.bkgd(' ')
        stdscr.clear()
        stdscr.refresh()
        
        # Setup curses
        curses.curs_set(1)  # Show cursor
        stdscr.keypad(True)  # Enable keypad for arrow keys
        stdscr.timeout(100)  # Non-blocking getch with 100ms timeout
        
        # Initialize colors AFTER reset
        curses.start_color()
        curses.use_default_colors()
        # Color pair 3: Force bright white (15 if available, else 7) on magenta
        try:
            curses.init_pair(3, 15, 5)  # Try bright white first
        except:
            curses.init_pair(3, 7, 5)   # Fallback to regular white

        curses.init_pair(4, curses.COLOR_BLUE, -1)  # BLUE for line numbers
        
        while True:
            height, width = stdscr.getmaxyx()
            
            # Adjust scroll to keep cursor visible
            self._adjust_scroll(height, width)
            
            # Draw screen
            self._draw_screen(stdscr)
            
            # Decrement status timeout
            if self.status_timeout > 0:
                self.status_timeout -= 1
                if self.status_timeout == 0:
                    self.status_message = ""
            
            # Get input
            ch = stdscr.getch()
            
            if ch == -1:  # Timeout, no input
                continue
            
            # Get the key name for more reliable shift detection
            try:
                keyname = curses.keyname(ch).decode()
            except Exception:
                keyname = ''
            
            # Helper functions for shift key detection
            def is_shift_up():
                return keyname in ('KEY_SUP', 'KEY_SR', 'kUP5', 'kUP6') or ch in (547, 337, 563)

            def is_shift_down():
                return keyname in ('KEY_SDOWN', 'KEY_SF', 'kDN5', 'kDN6') or ch in (548, 336, 522)

            def is_shift_left():
                return keyname in ('KEY_SLEFT', 'kLFT5', 'kLFT6') or ch in (391, 393, 545)

            def is_shift_right():
                return keyname in ('KEY_SRIGHT', 'kRIT5', 'kRIT6') or ch in (400, 402, 546)
            
            # Helper functions for numpad keys (standard + numpad codes)
            def is_up_arrow():
                return keyname in ('KEY_UP', 'KEY_A2') or ch in (curses.KEY_UP, 259, 450)
            
            def is_down_arrow():
                return keyname in ('KEY_DOWN', 'KEY_C2') or ch in (curses.KEY_DOWN, 258, 456)
            
            def is_left_arrow():
                return keyname in ('KEY_LEFT', 'KEY_B1') or ch in (curses.KEY_LEFT, 260, 452)
            
            def is_right_arrow():
                return keyname in ('KEY_RIGHT', 'KEY_B3') or ch in (curses.KEY_RIGHT, 261, 454)
            
            def is_home():
                return keyname in ('KEY_HOME', 'KEY_A1') or ch in (curses.KEY_HOME, 262, 449)
            
            def is_end():
                return keyname in ('KEY_END', 'KEY_C1') or ch in (curses.KEY_END, 358, 455)
            
            def is_pgup():
                return keyname in ('KEY_PPAGE', 'KEY_A3') or ch in (curses.KEY_PPAGE, 339, 451)
            
            def is_pgdn():
                return keyname in ('KEY_NPAGE', 'KEY_C3') or ch in (curses.KEY_NPAGE, 338, 457)
            
            # Check shift+arrow keys FIRST
            if is_shift_up():
                if not self.selecting:
                    self.selection_start = (self.cursor_y, self.cursor_x)
                    self.selecting = True
                
                if self.cursor_y > 0:
                    self.cursor_y -= 1
                    self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))
                else:
                    # No line above - extend selection to beginning of current line
                    self.cursor_x = 0
                
                self.selection_end = (self.cursor_y, self.cursor_x)
            
            elif is_shift_down():
                if not self.selecting:
                    self.selection_start = (self.cursor_y, self.cursor_x)
                    self.selecting = True
                
                if self.cursor_y < len(self.lines) - 1:
                    self.cursor_y += 1
                    self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))
                else:
                    # No line below - extend selection to end of current line
                    self.cursor_x = len(self.lines[self.cursor_y])
                
                self.selection_end = (self.cursor_y, self.cursor_x)
            
            elif is_shift_left():
                if not self.selecting:
                    self.selection_start = (self.cursor_y, self.cursor_x)
                    self.selecting = True
                
                if self.cursor_x > 0:
                    self.cursor_x -= 1
                elif self.cursor_y > 0:
                    self.cursor_y -= 1
                    self.cursor_x = len(self.lines[self.cursor_y])
                
                self.selection_end = (self.cursor_y, self.cursor_x)
            
            elif is_shift_right():
                if not self.selecting:
                    self.selection_start = (self.cursor_y, self.cursor_x)
                    self.selecting = True
                
                if self.cursor_x < len(self.lines[self.cursor_y]):
                    self.cursor_x += 1
                elif self.cursor_y < len(self.lines) - 1:
                    self.cursor_y += 1
                    self.cursor_x = 0
                
                self.selection_end = (self.cursor_y, self.cursor_x)
            
            # Regular arrow keys (without shift) - use helper functions with selection handling
            elif is_up_arrow():
                if self.selection_start is not None:
                    self._handle_arrow_with_selection('up')
                elif self.cursor_y > 0:
                    self.cursor_y -= 1
                    self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))
            
            elif is_down_arrow():
                if self.selection_start is not None:
                    self._handle_arrow_with_selection('down')
                elif self.cursor_y < len(self.lines) - 1:
                    self.cursor_y += 1
                    self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))
            
            elif is_left_arrow():
                if self.selection_start is not None:
                    self._handle_arrow_with_selection('left')
                elif self.cursor_x > 0:
                    self.cursor_x -= 1
                elif self.cursor_y > 0:
                    self.cursor_y -= 1
                    self.cursor_x = len(self.lines[self.cursor_y])
            
            elif is_right_arrow():
                if self.selection_start is not None:
                    self._handle_arrow_with_selection('right')
                elif self.cursor_x < len(self.lines[self.cursor_y]):
                    self.cursor_x += 1
                elif self.cursor_y < len(self.lines) - 1:
                    self.cursor_y += 1
                    self.cursor_x = 0
            
            elif ch == 27:  # Escape
                if self._confirm_exit(stdscr):
                    break
            
            elif ch == 24:  # Ctrl+X - Cut
                if self.selection_start is not None:
                    selected_text = self._get_selected_text()
                    self.clipboard = [selected_text]
                    self._delete_selection()
                    self._set_status("Selection cut to clipboard")
                else:
                    self._set_status("No selection to cut")
                self._ensure_valid_cursor()

            elif ch == 3:  # Ctrl+C
                continue
            
            elif ch == 1:  # Ctrl+A - Select All (NO STATUS MESSAGES)
                if self.lines:
                    # Check if we just used Ctrl+A (simple toggle)
                    if (self.selection_start == (0, 0) and 
                        self.selection_end == (len(self.lines) - 1, len(self.lines[-1]))):
                        # Already selected all - deselect
                        self._clear_selection()
                        # NO STATUS MESSAGE
                    else:
                        # Select all text
                        self.selection_start = (0, 0)
                        last_line_idx = len(self.lines) - 1
                        self.selection_end = (last_line_idx, len(self.lines[last_line_idx]))
                        self.selecting = False
                        # Jump cursor to end of selection
                        self.cursor_y = last_line_idx
                        self.cursor_x = len(self.lines[last_line_idx])
                        # NO STATUS MESSAGE

            elif ch == 26:  # Ctrl+Z - Undo
                self._undo()
            
            elif ch == 25:  # Ctrl+Y - Redo
                self._redo()
            
            elif ch == 15:  # Ctrl+O - Copy
                if self.selection_start is not None:
                    selected_text = self._get_selected_text()
                    if selected_text:
                        self.clipboard = [selected_text]
                        self._set_status("Selection copied to clipboard")
                    self._clear_selection()
                else:
                    self._set_status("No selection to copy")
                self._ensure_valid_cursor()

            elif ch == 16:  # Ctrl+P - Paste
                if self.clipboard:
                    if self.selection_start is not None:
                        self._delete_selection()
                    
                    if not self.lines:
                        self.lines = ['']
                    
                    if self.cursor_y >= len(self.lines):
                        self.cursor_y = len(self.lines) - 1
                    if self.cursor_x > len(self.lines[self.cursor_y]):
                        self.cursor_x = len(self.lines[self.cursor_y])
                    
                    paste_text = self.clipboard[0]
                    
                    # Multi-line paste with proper undo support
                    if '\n' in paste_text:
                        paste_lines = paste_text.split('\n')
                        current_line = self.lines[self.cursor_y]
                        
                        # Save COMPLETE state for undo
                        old_lines = self.lines.copy()
                        old_cursor_y = self.cursor_y
                        old_cursor_x = self.cursor_x
                        
                        line_before = current_line[:self.cursor_x]
                        line_after = current_line[self.cursor_x:]
                        
                        self.lines[self.cursor_y] = line_before + paste_lines[0]
                        
                        for i, paste_line in enumerate(paste_lines[1:-1], start=1):
                            self.lines.insert(self.cursor_y + i, paste_line)
                        
                        if len(paste_lines) > 1:
                            self.lines.insert(self.cursor_y + len(paste_lines) - 1, 
                                            paste_lines[-1] + line_after)
                            self.cursor_y += len(paste_lines) - 1
                            self.cursor_x = len(paste_lines[-1])
                        else:
                            self.cursor_x += len(paste_lines[0])
                        
                        # Save complete undo state for multi-line paste
                        self._save_undo_state('paste_multiline', {
                            'old_lines': old_lines,
                            'old_cursor_y': old_cursor_y,
                            'old_cursor_x': old_cursor_x,
                            'new_cursor_y': self.cursor_y,
                            'new_cursor_x': self.cursor_x,
                            'paste_text': paste_text
                        })
                    else:
                        # Single-line paste
                        line = self.lines[self.cursor_y]
                        old_line = line
                        
                        self._save_undo_state('paste', {
                            'y': self.cursor_y,
                            'x': self.cursor_x,
                            'text': paste_text,
                            'old_line': old_line
                        })
                        
                        new_line = line[:self.cursor_x] + paste_text + line[self.cursor_x:]
                        self.lines[self.cursor_y] = new_line
                        self.cursor_x += len(paste_text)
                    
                    self._set_status("Pasted from clipboard")
                    self.modified = True
                    self._ensure_valid_cursor()
            
            elif ch == 19:  # Ctrl+S - Save
                self._save_file()
            
            elif ch == 6:  # Ctrl+F - Search
                self._search(stdscr)
            
            elif ch == 9:  # Ctrl+I - Info
                info = self._get_file_info()
                self._set_status(info, timeout=30)
            
            elif ch == 18:  # Ctrl+R - Rename
                self._rename_file(stdscr)
            
            elif ch == 4:  # Ctrl+D - Delete
                if self._delete_file(stdscr):
                    break  # Exit editor after deleting file
            
            elif is_home():
                self.cursor_x = 0
                self._clear_selection()
            
            elif is_end():
                self.cursor_x = len(self.lines[self.cursor_y])
                self._clear_selection()
            
            elif is_pgup():  # Page Up
                self._move_cursor(-10, 0)
                self._clear_selection()
            
            elif is_pgdn():  # Page Down
                self._move_cursor(10, 0)
                self._clear_selection()
            
            elif ch == curses.KEY_BACKSPACE or ch == 127 or ch == 8:
                self._delete_char()
            
            elif ch == curses.KEY_DC:  # Delete key
                self._delete_char_forward()
            
            # Handle printable characters
            else:
                self._insert_char(ch)
                            
class InteractiveNavigator:
    """Interactive file/directory navigator using curses"""
    
    def __init__(self, base_dir, current_dir):
        self.base_dir = base_dir
        self.current_dir = current_dir
        self.selected_index = 0
        self.scroll_offset = 0
        # Start with all directories expanded - collect all directory paths
        self.expanded_dirs = self._get_all_directories(base_dir)
        self.items = []
        self.refresh_items()

        # Add status message support
        self.status_message = ""
        self.status_timeout = 0
        
        # Pre-select current directory
        for i, item in enumerate(self.items):
            if item[4]:  # is_current flag
                self.selected_index = i
                break

    def _get_all_directories(self, root_dir):
        """Recursively get all directory paths for initial expansion"""
        dirs = {root_dir}
        try:
            for item in os.listdir(root_dir):
                item_path = os.path.join(root_dir, item)
                if os.path.isdir(item_path):
                    dirs.add(item_path)
                    dirs.update(self._get_all_directories(item_path))
        except (PermissionError, Exception):
            pass
        return dirs
    
    def refresh_items(self):
        """Rebuild the tree items list"""
        # Start with HOME as the root
        self.items = [(0, "HOME", self.base_dir, True, self.current_dir == self.base_dir, None)]
        
        # Only show children of HOME if it's expanded
        if self.base_dir in self.expanded_dirs:
            base_items = DirectoryTreeBuilder.build_tree_items(self.base_dir, self.current_dir)
            parent_stack = []
            
            for item in base_items:
                depth, name, path, is_dir, is_current, parent_depth = item
                
                # Increase depth by 1 since everything is now under HOME
                depth += 1
                
                # Update parent stack
                while parent_stack and parent_stack[-1][0] >= depth:
                    parent_stack.pop()
                
                # Check if parent is collapsed
                if parent_stack and parent_stack[-1][1] not in self.expanded_dirs:
                    continue
                
                self.items.append((depth, name, path, is_dir, is_current, parent_depth))
                
                if is_dir:
                    parent_stack.append((depth, path))

    def get_color_for_item(self, item, is_selected):
        """Determine color for an item based on its depth from current directory"""
        depth, name, path, is_dir, is_current, depth_from_current = item
        
        if is_selected:
            return curses.A_REVERSE
        
        if is_current:
            return curses.color_pair(1)  # Yellow
        elif depth_from_current == 0:  # Direct child of current
            return curses.color_pair(2)  # Magenta
        elif depth_from_current is not None and depth_from_current >= 1:  # Grandchild+
            return curses.A_NORMAL  # White/default
        else:
            return curses.A_NORMAL
    
    def draw_tree(self, stdscr):
        """Draw the directory tree"""
        height, width = stdscr.getmaxyx()
        
        # Clear with explicit color reset
        stdscr.bkgdset(' ', 0)
        stdscr.clear()
        
        # Draw title with color pair - show status message if active, with time on right
        current_time = datetime.datetime.now().strftime('%I:%M %p')
        time_text = f"{current_time} "
        
        if self.status_message and self.status_timeout > 0:
            title_content = f" {self.status_message} "
        else:
            rel_path = VariableManager.get_relative_path(self.current_dir)
            title_content = f" NAVIGATOR <> {{{rel_path}}} "
        
        # Calculate available width for title (leave room for time)
        available_width = width - len(time_text)
        padded_title = title_content[:available_width].ljust(available_width)
        full_title = padded_title + time_text
        
        try:
            stdscr.addstr(0, 0, full_title[:width], curses.color_pair(3))
        except curses.error:
            pass
        
        # Adjust scroll to keep selection visible
        visible_height = height - 4
        
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + visible_height:
            self.scroll_offset = self.selected_index - visible_height + 1
        
        # Draw tree items
        for i in range(visible_height):
            item_index = self.scroll_offset + i
            
            if item_index >= len(self.items):
                break
            
            item = self.items[item_index]
            depth, name, path, is_dir, is_current, _ = item
            
            is_selected = (item_index == self.selected_index)
            
            # Build prefix (indentation + expand indicator)
            indent = "  " * depth
            
            if is_dir:
                is_expanded = path in self.expanded_dirs
                has_contents = any(os.path.isdir(os.path.join(path, e)) or os.path.isfile(os.path.join(path, e)) 
                                for e in os.listdir(path)) if os.path.exists(path) else False
                
                if is_expanded:
                    indicator = "▼ "
                elif has_contents:
                    indicator = "▶ "
                else:
                    indicator = "□ "
                
                display_name = name + "/"
            else:
                indicator = "  "
                display_name = name
            
            line = f"{indent}{indicator}{display_name}"
            
            # Apply color
            color = self.get_color_for_item(item, is_selected)
            
            try:
                stdscr.addstr(i + 3, 0, line[:width - 1], color)
            except curses.error:
                pass

        # Draw help bar with color pair and time on right
        help_text = " ↑/↓_Move  PgUp/PgDn_Jump  Home/End_Start/End  ^F_Find  Enter_Open  Space_Expand  Esc_Exit "
        full_line = help_text[:width].ljust(width)
        try:
            stdscr.addstr(height - 1, 0, full_line[:width], curses.color_pair(3))
        except curses.error:
            pass
        
        stdscr.refresh()

    def find_item(self, stdscr):
        """Search for a file or directory by name"""
        height, width = stdscr.getmaxyx()
        status_y = 0
        
        search_prompt = " Find: "
        search_term = ""
        cursor_pos = len(search_prompt)
        
        stdscr.timeout(-1)  # Blocking mode for input
        
        while True:
            try:
                # Draw prompt with magenta background
                display_line = search_prompt + search_term
                stdscr.attron(curses.color_pair(3))
                stdscr.addstr(status_y, 0, display_line.ljust(width)[:width])
                stdscr.attroff(curses.color_pair(3))
                stdscr.move(status_y, cursor_pos)
                stdscr.refresh()
                
                ch = stdscr.getch()
                
                if ch in (ord('\n'), ord('\r'), curses.KEY_ENTER, 10, 13):  # Enter
                    break
                elif ch == 27:  # Escape
                    search_term = ""
                    break
                elif ch in (curses.KEY_BACKSPACE, 127, 8):  # Backspace
                    if search_term:
                        search_term = search_term[:-1]
                        cursor_pos -= 1
                elif 32 <= ch <= 126:  # Printable characters
                    search_term += chr(ch)
                    cursor_pos += 1
            except Exception:
                break
        
        stdscr.timeout(100)  # Restore non-blocking mode
        
        if not search_term:
            return None
        
        # Search for matching item (case-insensitive, partial match)
        search_lower = search_term.lower()
        
        # Start from current selection + 1, wrap around
        start_index = (self.selected_index + 1) % len(self.items)
        
        for offset in range(len(self.items)):
            index = (start_index + offset) % len(self.items)
            item = self.items[index]
            item_name = item[1].lower()
            
            if search_lower in item_name:
                self.selected_index = index
                return item[1]  # Return found item name
        
        return None  # Not found

    # For InteractiveNavigator
    def run(self, stdscr):
        """Main navigator loop"""
        # CRITICAL: Force terminal reset
        stdscr.attrset(0)
        stdscr.bkgd(' ')
        stdscr.clear()
        stdscr.refresh()
        
        # Setup colors
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_YELLOW, -1)
        curses.init_pair(2, curses.COLOR_MAGENTA, -1)
        try:
            curses.init_pair(3, 15, 5)  # Try bright white on magenta
        except:
            curses.init_pair(3, 7, 5)   # Fallback to white on magenta
        
        curses.curs_set(0)  # Hide cursor
        stdscr.keypad(True)
        stdscr.timeout(100)
        
        while True:
            height, width = stdscr.getmaxyx()
            visible_height = height - 4
            
            self.draw_tree(stdscr)
            
            # Decrement status timeout
            if self.status_timeout > 0:
                self.status_timeout -= 1
                if self.status_timeout == 0:
                    self.status_message = ""
            
            key = stdscr.getch()
            
            if key == -1:
                continue
            
            # Navigation
            if key == curses.KEY_UP:
                self.selected_index = max(0, self.selected_index - 1)
            elif key == curses.KEY_DOWN:
                self.selected_index = min(len(self.items) - 1, self.selected_index + 1)
            elif key == curses.KEY_PPAGE:  # Page Up
                self.selected_index = max(0, self.selected_index - visible_height)
            elif key == curses.KEY_NPAGE:  # Page Down
                self.selected_index = min(len(self.items) - 1, self.selected_index + visible_height)
            elif key == curses.KEY_HOME:
                self.selected_index = 0
            elif key == curses.KEY_END:
                self.selected_index = len(self.items) - 1
            
            # Actions
            elif key == ord(' '):  # Space - toggle expand/collapse
                if self.selected_index < len(self.items):
                    item = self.items[self.selected_index]
                    path = item[2]
                    is_dir = item[3]
                    
                    if is_dir:
                        if path in self.expanded_dirs:
                            self.expanded_dirs.remove(path)
                        else:
                            self.expanded_dirs.add(path)
                        self.refresh_items()
            
            elif key == 6:  # Ctrl+F - Find
                found_name = self.find_item(stdscr)
                # Store the status message to display on next draw
                if found_name:
                    self.status_message = f"Found: {found_name}"
                else:
                    self.status_message = "Not found"
                self.status_timeout = 20  # Show for ~2 seconds (20 * 100ms)

            elif key in (ord('\n'), ord('\r'), curses.KEY_ENTER, 10, 13):  # Enter
                if self.selected_index < len(self.items):
                    item = self.items[self.selected_index]
                    path = item[2]
                    is_dir = item[3]
                    
                    # Check if it's actually a directory or file
                    if is_dir and os.path.isdir(path):
                        # Change directory
                        self.current_dir = PathResolver.normalize_to_actual_case(path)
                        self.refresh_items()
                        
                        # Update selected index to new current directory
                        for i, item in enumerate(self.items):
                            if item[4]:  # is_current
                                self.selected_index = i
                                break
                    elif os.path.isfile(path):
                        # Open file in editor - normalize path first
                        normalized_path = PathResolver.normalize_to_actual_case(path)
                        return ('edit', normalized_path)
            
            elif key == 27:  # Escape
                return ('exit', None)
            
def open_curses_editor(filepath: str) -> bool:
    """
    Open a file in the curses editor.
    Returns True if file was saved, False otherwise.
    """
    editor = CursesEditor(filepath)
    try:
        Curses.wrapper(editor.run)
        return True
    except KeyboardInterrupt:
        return False
    except Exception as e:
        print(f"Editor error: {e}")
        return False

class Text:
    INDENT = 3 * " "

class MenuOption(Enum):
    EXISTING = 0
    NEW = 1
    REMOVE = 2

class DataType(Enum):
    NUMBER = "number"
    STRING = "string"
    DIRECTORY = "directory"
    FILE = "file"
    NULL = "null"

class Variable:
    def __init__(self, name, value, var_type, is_persistent=True):
        self.name = name
        self.value = value
        self.type = var_type
        self.is_persistent = is_persistent

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

# Global variables
current_directory = ""
last_command_result = None
session_variables = {}  # For # variables
persistent_variables = {}  # For $ variables
clipboard_file = None  # For copy/paste/cut functionality - format: (path, type, is_cut)
current_user = None

class NumberFormatter:
    @staticmethod
    def format_number(value):
        """Consistently format numbers to always show decimal point"""
        if isinstance(value, (int, float)):
            if value == int(value):
                return f"{int(value)}.0"
            else:
                return str(float(value))
        return str(value)

class Input:
    @staticmethod
    def get_key():
        """Get a single keypress from the user"""
        if os.name == 'nt':
            while True:
                if msvcrt.kbhit():
                    return msvcrt.getch()
        else:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
                return ch.encode()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    @staticmethod
    def get_hidden_input():
        """Get password input with asterisk masking"""
        password = []
        try:
            if os.name == 'nt':
                while True:
                    char = msvcrt.getch()
                    if char == b'\x03':  # Ctrl+C
                        raise KeyboardInterrupt
                    char = char.decode('utf-8', errors='ignore')
                    if char == '\r':
                        sys.stdout.write('\n')
                        return ''.join(password)
                    elif char == '\b':
                        if password:
                            password.pop()
                            sys.stdout.write('\b \b')
                    elif char.isprintable():
                        password.append(char)
                        sys.stdout.write('*')
                    sys.stdout.flush()
            else:
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(fd)
                    while True:
                        char = sys.stdin.read(1)
                        if char in ('\r', '\n'):
                            sys.stdout.write('\n')
                            return ''.join(password)
                        elif char in ('\x7f', '\x08'):
                            if password:
                                password.pop()
                                sys.stdout.write('\b \b')
                        elif char.isprintable():
                            password.append(char)
                            sys.stdout.write('*')
                        sys.stdout.flush()
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except KeyboardInterrupt:
            System.handle_shutdown()

class VariableManager:
    @staticmethod
    def get_user_root(username):
        """Get the user's root directory path"""
        return os.path.join(get_user_data_path(), "users", username)
    
    @staticmethod
    def get_variables_file(username):
        """Get the path to the user's variables file"""
        variables_dir = os.path.join(get_user_data_path(), "variables")
        if not os.path.exists(variables_dir):
            os.makedirs(variables_dir)
        return os.path.join(variables_dir, f"{username}.var")
    
    @staticmethod
    def load_persistent_variables(username):
        """Load persistent variables from file"""
        global persistent_variables
        variables_file = VariableManager.get_variables_file(username)
        
        try:
            if os.path.exists(variables_file):
                with open(variables_file, 'r') as f:
                    data = json.load(f)
                    persistent_variables = {}
                    for name, var_data in data.items():
                        persistent_variables[name] = Variable(
                            name, var_data['value'], 
                            DataType(var_data['type']), 
                            True
                        )
        except Exception as e:
            System.print_instant(f"Warning: Could not load variables: {e}", is_error=True)
    
    @staticmethod
    def save_persistent_variables(username):
        """Save persistent variables to file"""
        variables_file = VariableManager.get_variables_file(username)
        
        try:
            data = {}
            for name, var in persistent_variables.items():
                data[name] = {
                    'value': var.value,
                    'type': var.type.value
                }
            
            with open(variables_file, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            System.print_instant(f"Warning: Could not save variables: {e}", is_error=True)
    
    @staticmethod
    def set_variable(name, value, var_type):
        """Set a variable (session or persistent)"""
        global current_user
        variable = Variable(name, value, var_type, name.startswith('$'))
        
        if name.startswith('$'):
            persistent_variables[name] = variable
            VariableManager.save_persistent_variables(current_user)
        elif name.startswith('#'):
            session_variables[name] = variable
        else:
            raise ValueError("Variable names must start with $ or #")
    
    @staticmethod
    def get_variable(name):
        """Get a variable value"""
        if name.startswith('$'):
            return persistent_variables.get(name)
        elif name.startswith('#'):
            return session_variables.get(name)
        return None
    
    @staticmethod
    def resolve_path(path):
        """Convert relative path to absolute path"""
        global current_user
        user_root = VariableManager.get_user_root(current_user)
        if path.startswith('/'):
            return os.path.join(user_root, path[1:])
        else:
            return os.path.join(user_root, path)
    
    @staticmethod
    def get_relative_path(absolute_path):
        """Convert absolute path to relative path from user root"""
        user_root = VariableManager.get_user_root(current_user)
        if absolute_path.startswith(user_root):
            relative = absolute_path[len(user_root):]
            if relative.startswith(os.sep):
                relative = relative[1:]
            if relative:
                return '/' + relative.replace(os.sep, '/')
            else:
                return '/'
        return None

class System:
    @staticmethod
    def clear_screen():
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def print_instant(text, end='\n', is_error=False):
        """Print text instantly"""
        color_code = Fore.RED if is_error else ""
        reset_code = Style.RESET_ALL if is_error else ""
        
        TerminalState.write(str(text), color_code, end + reset_code)

    @staticmethod
    def print_slow(text, delay=0.005, end='\n', is_error=False):
        """Print text character by character"""
        color_code = Fore.RED if is_error else ""
        
        for char in str(text):
            TerminalState.write(char, color_code, '')
            time.sleep(delay)
        
        if end:
            reset_code = Style.RESET_ALL if is_error else ""
            TerminalState.write('', '', end + reset_code)

    @staticmethod
    def colored_input(prompt, hidden=False, start_animation=True):
        """Get colored input from user"""
        
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
        """Handle system shutdown"""
        TerminalState.write('', Style.RESET_ALL, '')
        System.print_instant(Message.SHUTDOWN)
        System.show_loading_bar("shutdown", Fore.RED)
        System.clear_screen()
        sys.exit(1)

    @staticmethod
    def show_loading_bar(sound_name, color=Fore.MAGENTA, filled_char='█', unfilled_char='.'):
        """Display loading bar synchronized with sound playback"""
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
        """Display welcome message with loading bar and animated border"""
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
        """Display error message and exit"""
        System.clear_screen()
        Sound.play_and_print("glitch", Message.GLITCH, is_error=True)
        time.sleep(0.5)
        System.print_slow(Message.ERROR, is_error=True)
        time.sleep(0.5)
        System.clear_screen()
        sys.exit(1)

    @staticmethod
    def create_user_directory(username):
        """Create user directory if it doesn't exist"""
        user_dir = os.path.join(get_user_data_path(), "users", username)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        return user_dir

    @staticmethod
    def show_result(result, output_type="sound"):
        """Centralized result display handler"""
        global last_command_result
        
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
        """Consolidated error display function"""
        System.print_instant(Message.MALFUNCTION, is_error=True)
        Sound.play("error")
        System.print_slow(message, is_error=True)
        
        if set_null_result:
            global last_command_result
            last_command_result = ("NULL", DataType.NULL)

def get_app_path():
    """Get the application's base directory (for bundled resources like sounds)."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def get_user_data_path():
    """Get the user data directory (cross-platform).
    
    Returns:
        Windows: %APPDATA%/Kairo
        macOS: ~/Library/Application Support/Kairo
        Linux: ~/.local/share/Kairo
    """
    if sys.platform == 'win32':
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
    elif sys.platform == 'darwin':
        base = os.path.expanduser('~/Library/Application Support')
    else:  # Linux and other Unix-like
        base = os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
    
    data_dir = os.path.join(base, 'Kairo')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

class Sound:
    base_path = get_app_path()

    @staticmethod
    def preload_sounds():
        """Preload commonly used sounds to reduce first-play delay"""
        sound_files = ["enter", "help", "error", "boot", "shutdown"]
        
        # Touch each sound file to load into OS cache
        for sound in sound_files:
            try:
                sound_path = f"{Sound.base_path}\\sounds\\{sound}.mp3"
                if os.path.exists(sound_path):
                    # Just opening and reading a bit helps cache it
                    with open(sound_path, 'rb') as f:
                        f.read(1024)  # Read first 1KB
            except:
                pass  # Silently ignore errors during preload

    @staticmethod
    def play(sound):
        """Play a sound file"""
        playsound(f"{Sound.base_path}\\sounds\\{sound}.mp3")

    @staticmethod
    def play_and_print(sound, result="", is_slow=False, is_error=False):
        """Play sound and print result simultaneously"""
        sound_thread = threading.Thread(target=lambda: Sound.play(sound))
        sound_thread.start()
        if result != "":
            if is_slow:
                System.print_slow(f"\n{result}", is_error=is_error)
            else:
                System.print_instant(f"\n{result}", is_error=is_error)

    @staticmethod
    def get_sound_duration(sound):
        """Get duration of a sound file in seconds"""
        try:
            from mutagen.mp3 import MP3
            audio = MP3(f"{Sound.base_path}\\sounds\\{sound}.mp3")
            return audio.info.length
        except:
            # Fallback duration if mutagen not available
            return 2.0  # Default 2 seconds

class TerminalState:
    """Manages terminal state for restoration after curses screens"""
    _output_buffer = []
    _recording = False
    _stdout_lock = threading.Lock()
    
    @staticmethod
    def start_recording():
        """Start recording terminal output"""
        TerminalState._recording = True
        TerminalState._output_buffer = []
    
    @staticmethod
    def stop_recording():
        """Stop recording terminal output"""
        TerminalState._recording = False
    
    @staticmethod
    def reset():
        """Reset the buffer (used on reboot)"""
        TerminalState._output_buffer = []
    
    @staticmethod
    def write(text, color_code="", end=''):
        """Write to stdout and record if active"""
        with TerminalState._stdout_lock:
            # Build the full output string with colors
            full_output = f"{color_code}{text}{end}"
            
            # Always write to stdout
            sys.stdout.write(full_output)
            sys.stdout.flush()
            
            # Record if recording is active
            if TerminalState._recording:
                TerminalState._output_buffer.append(full_output)
    
    @staticmethod
    def restore():
        """Restore the terminal state from buffer"""
        
        # Clear the screen
        System.clear_screen()
        
        # Replay all recorded output WITHOUT going through TerminalState.write
        with TerminalState._stdout_lock:
            for output in TerminalState._output_buffer:
                sys.stdout.write(output)
                sys.stdout.flush()

class UserManager:
    @staticmethod
    def load_users(file_path):
        """Load users from JSON file"""
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                return [User(user['username'], user['password']) for user in data['users']]
        except (FileNotFoundError, json.JSONDecodeError) as e:
            error_msg = "USER DATA FILE NOT FOUND" if isinstance(e, FileNotFoundError) else "INVALID USER DATA FILE FORMAT"
            System.throw_error(error_msg)
            sys.exit(1)

    @staticmethod
    def save_users(users, file_path):
        """Save users to JSON file"""
        data = {'users': [{'username': user.username, 'password': user.password} for user in users]}
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def match_user(users, username_input):
        """Find user by username"""
        for user in users:
            if user.username.lower() == username_input.lower():
                return user
        return None

class MenuHandler:
    @staticmethod
    def display_menu(selected):
        """Display the menu with the currently selected option highlighted"""
        System.clear_screen()
        System.print_instant(Message.MENU + '\n')
        options = ["Login", "Create User", "Remove User"]
        for i, option in enumerate(options):
            if i == selected:
                sys.stdout.write(f"{Fore.YELLOW}> {option}{Style.RESET_ALL}")
            else:
                sys.stdout.write(f"  {option}")
            if i < len(options) - 1:
                sys.stdout.write('\n')
        sys.stdout.flush()

    @staticmethod
    def handle_menu():
        """Handle the menu selection"""
        selected = 0
        while True:
            MenuHandler.display_menu(selected)
            key = Input.get_key()
            if os.name == 'nt':
                if key == b'\xe0':  # Special key prefix
                    key = Input.get_key()
                    if key == b'H':  # Up arrow
                        selected = (selected - 1) % 3
                    elif key == b'P':  # Down arrow
                        selected = (selected + 1) % 3
                elif key == b'\r':  # Enter key
                    return MenuOption(selected)
            else:
                if key == b'\x1b':  # Escape sequence
                    Input.get_key()  # Skip the [
                    key = Input.get_key()
                    if key == b'A':  # Up arrow
                        selected = (selected - 1) % 3
                    elif key == b'B':  # Down arrow
                        selected = (selected + 1) % 3
                elif key == b'\r':  # Enter key
                    return MenuOption(selected)

class UserOperations:
    @staticmethod
    def add_new_user(users, file_path):
        """Add a new user to the system"""
        while True:
            username = System.colored_input("\n\nNew Username: ", start_animation=False)
            if any(user.username.lower() == username.lower() for user in users):
                System.throw_error("USERNAME ALREADY EXISTS")
                continue

            password = System.colored_input("New Password: ", hidden=True, start_animation=False)
            confirm_password = System.colored_input("Confirm Password: ", hidden=True, start_animation=False)

            if password != confirm_password:
                System.throw_error("PASSWORDS DO NOT MATCH")
                continue

            users.append(User(username, password))
            UserManager.save_users(users, file_path)
            System.create_user_directory(username)
            Sound.play_and_print("enter", f"User '{username}' created successfully!")
            break
        return users

    @staticmethod
    def remove_user(users, file_path):
        """Remove a user from the system"""
        username = System.colored_input("\n\nUsername to remove: ")
        user = UserManager.match_user(users, username)

        if not user:
            System.throw_error("USER NOT FOUND")
            return users

        password = System.colored_input("Confirm password: ", hidden=True, start_animation=False)
        if password != user.password:
            System.throw_error("INCORRECT PASSWORD")
            return users

        users = [u for u in users if u.username.lower() != username.lower()]
        UserManager.save_users(users, file_path)
        Sound.play_and_print("enter", f"User '{username}' removed successfully!")
        return users

class ArgumentParser:
    @staticmethod
    def parse_args_with_quotes(args_list):
        """Parse argument list, treating quoted strings as single arguments"""
        if not args_list:
            return []
        
        # Join back into string to parse properly
        full_string = ' '.join(args_list)
        parsed_args = []
        current_arg = ''
        in_quotes = False
        
        i = 0
        while i < len(full_string):
            char = full_string[i]
            
            if char == '"':
                if in_quotes:
                    # End of quoted string
                    parsed_args.append(current_arg)
                    current_arg = ''
                    in_quotes = False
                else:
                    # Start of quoted string
                    in_quotes = True
            elif char == ' ' and not in_quotes:
                # Space outside quotes - separator
                if current_arg:
                    parsed_args.append(current_arg)
                    current_arg = ''
            else:
                current_arg += char
            
            i += 1
        
        # Add final argument if any
        if current_arg:
            parsed_args.append(current_arg)
        
        return parsed_args

class ArgumentResolver:
    @staticmethod
    def resolve_argument(arg, expected_type):
        """Resolve an argument to its actual value"""
        if arg.lower() == "result":
            if last_command_result is None:
                raise ValueError("No previous command result available")
            result_value, result_type = last_command_result
            if result_type != expected_type:
                raise ValueError(f"Last result is of type {result_type.value}, expected {expected_type.value}")
            return result_value
    
        if arg.startswith('$') or arg.startswith('#'):
            variable = VariableManager.get_variable(arg)
            if variable is None:
                raise ValueError(f"Variable '{arg}' not found")
            if variable.type != expected_type:
                raise ValueError(f"Variable '{arg}' is of type {variable.type.value}, expected {expected_type.value}")
            return variable.value
        
        if expected_type == DataType.NUMBER:
            try:
                return float(arg)
            except ValueError:
                raise ValueError(f"'{arg}' is not a valid number")
        
        elif expected_type == DataType.STRING:
            if arg.startswith('"') and arg.endswith('"'):
                return arg[1:-1]
            else:
                raise ValueError(f"String must be quoted: '{arg}'")
        
        elif expected_type == DataType.DIRECTORY:
            if arg.startswith('/'):
                abs_path = VariableManager.resolve_path(arg, current_user)
                if not os.path.exists(abs_path) or not os.path.isdir(abs_path):
                    raise ValueError(f"Directory '{arg}' not found")
                return abs_path
            else:
                return arg
    
        elif expected_type == DataType.FILE:
            if arg.startswith('/'):
                abs_path = VariableManager.resolve_path(arg, current_user)
                if not os.path.exists(abs_path) or not os.path.isfile(abs_path):
                    raise ValueError(f"File '{arg}' not found")
                return abs_path
            else:
                return arg
        return arg
    
    @staticmethod
    def process_edit_text(text):
        """Process text for edit commands with escape sequences and conditional variable resolution"""
        result = ""
        i = 0
        
        while i < len(text):
            if text[i] == '\\' and i + 1 < len(text):
                next_char = text[i + 1]
                if next_char == 'n':
                    result += '\n'
                    i += 2
                elif next_char in ['$', '#']:
                    # Add the escaped character literally - this prevents variable resolution
                    result += next_char
                    i += 2
                else:
                    # Not a recognized escape, keep the backslash
                    result += text[i]
                    i += 1
            elif text[i] in ['$', '#']:
                # Check if this is the start of a variable name
                var_start = i
                i += 1
                # Continue reading alphanumeric characters and underscores
                while i < len(text) and (text[i].isalnum() or text[i] == '_'):
                    i += 1
                
                var_name = text[var_start:i]
                
                # Only replace if it's a valid variable name (more than just $ or #)
                if len(var_name) > 1:
                    var = VariableManager.get_variable(var_name)
                    if var:
                        result += str(var.value)
                    else:
                        # Variable not found, keep as literal text
                        result += var_name
                else:
                    # Just a standalone $ or # character
                    result += var_name
            else:
                result += text[i]
                i += 1
        
        return result

class PathResolver:
    @staticmethod
    def normalize_to_actual_case(path):
        """
        Normalize a path to use the actual filesystem casing.
        This ensures that even if user provides lowercase, we get the actual case.
        """
        if not os.path.exists(path):
            return path
        
        # Get the absolute path
        abs_path = os.path.abspath(path)
        
        # Split into drive and path components
        drive, path_rest = os.path.splitdrive(abs_path)
        
        # Split into individual parts
        parts = path_rest.strip(os.sep).split(os.sep)
        
        # Rebuild path with actual casing
        current = drive + os.sep if drive else os.sep
        
        for part in parts:
            if not part:
                continue
            
            try:
                # List directory contents
                entries = os.listdir(current)
                
                # Find the actual case-sensitive match
                actual_name = None
                for entry in entries:
                    if entry.lower() == part.lower():
                        actual_name = entry
                        break
                
                if actual_name:
                    current = os.path.join(current, actual_name)
                else:
                    # Shouldn't happen if path exists, but fallback
                    current = os.path.join(current, part)
                    
            except (FileNotFoundError, PermissionError):
                # If we can't read directory, just use what we have
                current = os.path.join(current, part)
        
        return os.path.normpath(current)
    
    @staticmethod
    def resolve_file_or_directory_argument(name, current_directory):
        """Enhanced resolver for file or directory arguments - WITH CASE PRESERVATION"""
        if name.lower() == "result":
            if last_command_result and last_command_result[1] in [DataType.FILE, DataType.DIRECTORY]:
                return VariableManager.resolve_path(last_command_result[0]), last_command_result[1]
            else:
                return None, None
        elif name.startswith('$') or name.startswith('#'):
            var = VariableManager.get_variable(name)
            if var and var.type in [DataType.FILE, DataType.DIRECTORY]:
                return VariableManager.resolve_path(var.value), var.type
            else:
                return None, None
        elif name.startswith('/'):
            abs_path = VariableManager.resolve_path(name)
            if os.path.exists(abs_path):
                # Normalize to actual case
                abs_path = PathResolver.normalize_to_actual_case(abs_path)
                if os.path.isfile(abs_path):
                    return abs_path, DataType.FILE
                elif os.path.isdir(abs_path):
                    return abs_path, DataType.DIRECTORY
            return None, None
        else:
            # Check current directory first
            current_path = os.path.join(current_directory, name)
            
            # Try exact match first
            if os.path.exists(current_path):
                # Normalize to actual case
                current_path = PathResolver.normalize_to_actual_case(current_path)
                if os.path.isfile(current_path):
                    return current_path, DataType.FILE
                elif os.path.isdir(current_path):
                    return current_path, DataType.DIRECTORY
            
            # Case-insensitive search
            try:
                for item in os.listdir(current_directory):
                    if item.lower() == name.lower():
                        full_path = os.path.join(current_directory, item)
                        # Use actual item name (preserves case)
                        if os.path.isfile(full_path):
                            return full_path, DataType.FILE
                        elif os.path.isdir(full_path):
                            return full_path, DataType.DIRECTORY
            except:
                pass
            
            return None, None

    @staticmethod
    def resolve_file_argument(filename, last_command_result, current_directory):
        """Resolve file argument to full path - WITH CASE PRESERVATION"""
        if filename.lower() == "result":
            if last_command_result and last_command_result[1] == DataType.FILE:
                return VariableManager.resolve_path(last_command_result[0])
            else:
                return None
        elif filename.startswith('$') or filename.startswith('#'):
            var = VariableManager.get_variable(filename)
            if var and var.type == DataType.FILE:
                return VariableManager.resolve_path(var.value)
            else:
                return None
        elif filename.startswith('/'):
            path = VariableManager.resolve_path(filename)
            if os.path.exists(path):
                return PathResolver.normalize_to_actual_case(path)
            return path
        else:
            # Try exact match
            path = os.path.join(current_directory, filename)
            if os.path.exists(path):
                return PathResolver.normalize_to_actual_case(path)
            
            # Case-insensitive search
            try:
                for item in os.listdir(current_directory):
                    if item.lower() == filename.lower():
                        return os.path.join(current_directory, item)
            except:
                pass
            
            return path
    
    @staticmethod
    def resolve_directory_argument(dirname, current_directory):
        """Resolve directory argument to full path - WITH CASE PRESERVATION"""
        if dirname.lower() == "result":
            if last_command_result and last_command_result[1] == DataType.DIRECTORY:
                return VariableManager.resolve_path(last_command_result[0])
            else:
                return None
        elif dirname.startswith('$') or dirname.startswith('#'):
            var = VariableManager.get_variable(dirname)
            if var and var.type == DataType.DIRECTORY:
                return VariableManager.resolve_path(var.value)
            else:
                return None
        elif dirname.startswith('/'):
            abs_path = VariableManager.resolve_path(dirname)
            if os.path.exists(abs_path) and os.path.isdir(abs_path):
                return PathResolver.normalize_to_actual_case(abs_path)
            return None
        else:
            # Check current directory first
            current_path = os.path.join(current_directory, dirname)
            if os.path.exists(current_path) and os.path.isdir(current_path):
                return PathResolver.normalize_to_actual_case(current_path)
            
            # Case-insensitive search - returns with ACTUAL case
            try:
                for item in os.listdir(current_directory):
                    if item.lower() == dirname.lower():
                        full_path = os.path.join(current_directory, item)
                        if os.path.isdir(full_path):
                            return full_path  # Already has actual case from listdir
            except:
                pass
            
            return None

class DirectoryTreeBuilder:
    """Shared utility for building directory tree structure"""
    
    @staticmethod
    def build_tree_items(base_dir, current_dir):
        """
        Build a flat list of tree items for rendering.
        Returns: List of tuples (depth, name, full_path, is_dir, is_current, parent_depth)
        """
        items = []
        current_abs = os.path.abspath(current_dir)
        
        def add_items(directory, depth=0, parent_is_current=False):
            try:
                entries = sorted(os.listdir(directory))
                dirs = [e for e in entries if os.path.isdir(os.path.join(directory, e))]
                files = [e for e in entries if os.path.isfile(os.path.join(directory, e))]
                
                dir_abs_path = os.path.abspath(directory)
                is_current = dir_abs_path == current_abs
                
                # Calculate depth from current directory
                if is_current:
                    depth_from_current = 0
                elif parent_is_current:
                    depth_from_current = 1
                else:
                    depth_from_current = None
                
                # Add directories
                for dir_name in dirs:
                    dir_path = os.path.join(directory, dir_name)
                    child_abs = os.path.abspath(dir_path)
                    child_is_current = child_abs == current_abs
                    
                    items.append((depth, dir_name, dir_path, True, child_is_current, depth_from_current))
                    
                    # Recursively add subdirectories
                    add_items(dir_path, depth + 1, is_current)
                
                # Add files
                for file_name in files:
                    file_path = os.path.join(directory, file_name)
                    items.append((depth, file_name, file_path, False, False, depth_from_current))
                    
            except (PermissionError, Exception):
                pass
        
        add_items(base_dir)
        return items

class EditHelper:
    @staticmethod
    def get_processed_line_content(prompt="Enter content:\n\n_> "):
        """Get line content and process it for variables/escapes"""
        content = System.colored_input(prompt)
        processed = ArgumentResolver.process_edit_text(content)
        return processed

class WebBrowser:
    """Terminal-based web browser using curses"""
    
    def __init__(self):
        self.search_results = []
        self.current_page = 0
        self.results_per_page = 10
        self.selected_index = 0
        self.current_url = ""
        self.page_content = []
        self.scroll_offset = 0
        self.mode = "search"  # "search" or "page"
        self.search_query = ""
        
    def google_search(self, query):
        """Perform a Google search and return results"""
        if not requests or not BeautifulSoup:
            return []
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            url = f"https://www.google.com/search?q={query}"
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for g in soup.find_all('div', class_='g'):
                title_elem = g.find('h3')
                link_elem = g.find('a')
                desc_elem = g.find('div', class_=['VwiC3b', 'lyLwlc'])
                
                if title_elem and link_elem:
                    title = title_elem.get_text()
                    link = link_elem.get('href')
                    description = desc_elem.get_text() if desc_elem else "No description available"
                    
                    if link and link.startswith('http'):
                        results.append({
                            'title': title,
                            'url': link,
                            'description': description
                        })
                        
                if len(results) >= 50:  # Limit to 50 results
                    break
            
            return results
        except Exception as e:
            return [{'title': f'Search Error: {str(e)}', 'url': '', 'description': ''}]
    
    def fetch_page(self, url):
        """Fetch and convert webpage to text"""
        if not requests or not html2text:
            return ["Error: Web browser dependencies not installed"]
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = True
            h.ignore_emphasis = False
            h.body_width = 0  # No wrapping
            
            text = h.handle(response.text)
            lines = text.split('\n')
            
            return lines
        except Exception as e:
            return [f"Error loading page: {str(e)}"]
    
    def draw_search_screen(self, stdscr, search_input=""):
        """Draw the search results screen"""
        height, width = stdscr.getmaxyx()
        
        stdscr.bkgdset(' ', 0)
        stdscr.clear()
        
        # Title bar with time on right
        current_time = datetime.datetime.now().strftime('%I:%M %p')
        time_text = f"{current_time} "
        title_content = f" BROWSER <> Google Search "
        
        available_width = width - len(time_text)
        padded_title = title_content[:available_width].ljust(available_width)
        full_title = padded_title + time_text
        
        try:
            stdscr.addstr(0, 0, full_title[:width], curses.color_pair(3))
        except curses.error:
            pass
        
        # Search bar
        search_bar_y = 2
        search_prompt = "Search: "
        try:
            stdscr.addstr(search_bar_y, 2, search_prompt)
            stdscr.addstr(search_bar_y, 2 + len(search_prompt), search_input[:width - 4 - len(search_prompt)])
        except curses.error:
            pass
        
        # Results
        if self.search_results:
            results_start_y = 4
            visible_height = height - 6  # Leave room for title, search, help
            
            start_idx = self.current_page * self.results_per_page
            end_idx = min(start_idx + self.results_per_page, len(self.search_results))
            
            # Page indicator
            total_pages = (len(self.search_results) + self.results_per_page - 1) // self.results_per_page
            page_info = f" Page {self.current_page + 1}/{total_pages} ({len(self.search_results)} results) "
            try:
                stdscr.addstr(results_start_y - 1, 2, page_info)
            except curses.error:
                pass
            
            # Display results
            for i in range(start_idx, end_idx):
                y = results_start_y + (i - start_idx) * 3
                if y + 2 >= height - 2:
                    break
                
                result = self.search_results[i]
                is_selected = (i == self.selected_index)
                
                # Result number and title
                result_num = f"[{i + 1}] "
                try:
                    if is_selected:
                        stdscr.addstr(y, 2, result_num + result['title'][:width - 4 - len(result_num)], 
                                    curses.A_REVERSE)
                    else:
                        stdscr.addstr(y, 2, result_num, curses.color_pair(2))
                        stdscr.addstr(y, 2 + len(result_num), result['title'][:width - 4 - len(result_num)])
                except curses.error:
                    pass
                
                # URL
                try:
                    url_display = result['url'][:width - 4]
                    if is_selected:
                        stdscr.addstr(y + 1, 4, url_display, curses.A_DIM | curses.A_REVERSE)
                    else:
                        stdscr.addstr(y + 1, 4, url_display, curses.A_DIM)
                except curses.error:
                    pass
                
                # Description
                try:
                    desc = result['description'][:width - 4]
                    if is_selected:
                        stdscr.addstr(y + 2, 4, desc, curses.A_REVERSE)
                    else:
                        stdscr.addstr(y + 2, 4, desc)
                except curses.error:
                    pass
        
        # Help bar
        help_y = height - 1
        help_text = " ↑/↓: Navigate | ←/→: Pages | Enter: Visit | ^N: New Search | Esc: Exit "
        full_line = help_text[:width].ljust(width)
        try:
            stdscr.addstr(help_y, 0, full_line[:width], curses.color_pair(3))
        except curses.error:
            pass
        
        stdscr.refresh()
    
    def draw_page_screen(self, stdscr):
        """Draw the webpage content screen"""
        height, width = stdscr.getmaxyx()
        
        stdscr.bkgdset(' ', 0)
        stdscr.clear()
        
        # Title bar with URL and time on right
        current_time = datetime.datetime.now().strftime('%I:%M %p')
        time_text = f"{current_time} "
        title_content = f" BROWSER <> {self.current_url[:width - 30]} "
        
        available_width = width - len(time_text)
        padded_title = title_content[:available_width].ljust(available_width)
        full_title = padded_title + time_text
        
        try:
            stdscr.addstr(0, 0, full_title[:width], curses.color_pair(3))
        except curses.error:
            pass
        
        # Page content
        content_start_y = 2
        visible_height = height - 3
        
        for i in range(visible_height):
            line_idx = self.scroll_offset + i
            if line_idx < len(self.page_content):
                line = self.page_content[line_idx]
                try:
                    stdscr.addstr(content_start_y + i, 0, line[:width])
                except curses.error:
                    pass
        
        # Help bar
        help_y = height - 1
        scroll_info = f"[Line {self.scroll_offset + 1}/{len(self.page_content)}] "
        help_text = f" ↑/↓: Scroll | PgUp/PgDn: Page | Backspace: Back | ^N: New Search | Esc: Exit {scroll_info}"
        full_line = help_text[:width].ljust(width)
        try:
            stdscr.addstr(help_y, 0, full_line[:width], curses.color_pair(3))
        except curses.error:
            pass
        
        stdscr.refresh()
    
    def get_search_input(self, stdscr):
        """Get search query from user"""
        height, width = stdscr.getmaxyx()
        search_bar_y = 2
        search_prompt = "Search: "
        
        query = ""
        cursor_pos = len(search_prompt)
        
        curses.curs_set(1)  # Show cursor
        stdscr.timeout(-1)  # Blocking mode
        
        while True:
            self.draw_search_screen(stdscr, query)
            
            try:
                stdscr.move(search_bar_y, 2 + cursor_pos)
            except curses.error:
                pass
            
            stdscr.refresh()
            
            ch = stdscr.getch()
            
            if ch in (ord('\n'), ord('\r'), curses.KEY_ENTER, 10, 13):
                break
            elif ch == 27:  # Escape
                query = ""
                break
            elif ch in (curses.KEY_BACKSPACE, 127, 8):
                if query:
                    query = query[:-1]
                    cursor_pos -= 1
            elif 32 <= ch <= 126:
                query += chr(ch)
                cursor_pos += 1
        
        curses.curs_set(0)  # Hide cursor
        stdscr.timeout(100)  # Restore non-blocking mode
        
        return query
    
    def run(self, stdscr):
        """Main browser loop"""
        # Setup curses
        stdscr.attrset(0)
        stdscr.bkgd(' ')
        stdscr.clear()
        stdscr.refresh()
        
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_YELLOW, -1)
        curses.init_pair(2, curses.COLOR_MAGENTA, -1)
        try:
            curses.init_pair(3, 15, 5)
        except:
            curses.init_pair(3, 7, 5)
        
        curses.curs_set(0)
        stdscr.keypad(True)
        stdscr.timeout(100)
        
        # Get initial search query
        self.search_query = self.get_search_input(stdscr)
        
        if not self.search_query:
            return
        
        # Perform search
        self.search_results = self.google_search(self.search_query)
        self.selected_index = 0
        self.current_page = 0
        
        while True:
            height, width = stdscr.getmaxyx()
            
            if self.mode == "search":
                self.draw_search_screen(stdscr)
                
                ch = stdscr.getch()
                
                if ch == -1:
                    continue
                
                # Get keyname for shift detection
                try:
                    keyname = curses.keyname(ch).decode()
                except:
                    keyname = ''
                
                # Navigation
                if keyname in ('KEY_UP', 'KEY_A2') or ch in (curses.KEY_UP, 259, 450):
                    if self.selected_index > 0:
                        self.selected_index -= 1
                        if self.selected_index < self.current_page * self.results_per_page:
                            self.current_page -= 1
                
                elif keyname in ('KEY_DOWN', 'KEY_C2') or ch in (curses.KEY_DOWN, 258, 456):
                    if self.selected_index < len(self.search_results) - 1:
                        self.selected_index += 1
                        if self.selected_index >= (self.current_page + 1) * self.results_per_page:
                            self.current_page += 1
                
                elif keyname in ('KEY_LEFT', 'KEY_B1') or ch in (curses.KEY_LEFT, 260, 452):
                    if self.current_page > 0:
                        self.current_page -= 1
                        self.selected_index = self.current_page * self.results_per_page
                
                elif keyname in ('KEY_RIGHT', 'KEY_B3') or ch in (curses.KEY_RIGHT, 261, 454):
                    total_pages = (len(self.search_results) + self.results_per_page - 1) // self.results_per_page
                    if self.current_page < total_pages - 1:
                        self.current_page += 1
                        self.selected_index = min(self.current_page * self.results_per_page, len(self.search_results) - 1)
                
                elif ch in (ord('\n'), ord('\r'), curses.KEY_ENTER, 10, 13):
                    if self.search_results and self.selected_index < len(self.search_results):
                        result = self.search_results[self.selected_index]
                        if result['url']:
                            self.current_url = result['url']
                            self.page_content = self.fetch_page(self.current_url)
                            self.scroll_offset = 0
                            self.mode = "page"
                
                elif ch == 14:  # Ctrl+N
                    self.search_query = self.get_search_input(stdscr)
                    if self.search_query:
                        self.search_results = self.google_search(self.search_query)
                        self.selected_index = 0
                        self.current_page = 0
                
                elif ch == 27:  # Escape
                    break
            
            elif self.mode == "page":
                self.draw_page_screen(stdscr)
                
                ch = stdscr.getch()
                
                if ch == -1:
                    continue
                
                try:
                    keyname = curses.keyname(ch).decode()
                except:
                    keyname = ''
                
                visible_height = height - 3
                
                if keyname in ('KEY_UP', 'KEY_A2') or ch in (curses.KEY_UP, 259, 450):
                    if self.scroll_offset > 0:
                        self.scroll_offset -= 1
                
                elif keyname in ('KEY_DOWN', 'KEY_C2') or ch in (curses.KEY_DOWN, 258, 456):
                    if self.scroll_offset < len(self.page_content) - visible_height:
                        self.scroll_offset += 1
                
                elif keyname in ('KEY_PPAGE', 'KEY_A3') or ch in (curses.KEY_PPAGE, 451):
                    self.scroll_offset = max(0, self.scroll_offset - visible_height)
                
                elif keyname in ('KEY_NPAGE', 'KEY_C3') or ch in (curses.KEY_NPAGE, 457):
                    self.scroll_offset = min(len(self.page_content) - visible_height, 
                                            self.scroll_offset + visible_height)
                
                elif ch in (curses.KEY_BACKSPACE, 127, 8):
                    self.mode = "search"
                    self.scroll_offset = 0
                
                elif ch == 14:  # Ctrl+N
                    self.search_query = self.get_search_input(stdscr)
                    if self.search_query:
                        self.search_results = self.google_search(self.search_query)
                        self.selected_index = 0
                        self.current_page = 0
                        self.mode = "search"
                
                elif ch == 27:  # Escape
                    break
                
class CommandRegistry:
    commands = {}
    
    @staticmethod
    def register(name, category="MISC", description="", usage="", examples=None):
        def decorator(func):
            CommandRegistry.commands[name] = {
                'func': func,
                'category': category,
                'description': description,
                'usage': usage,
                'examples': examples or []
            }
            return func
        return decorator

class Command:
    @staticmethod
    def valid_commands():
        """Get list of valid commands from registry"""
        return list(CommandRegistry.commands.keys())

    # Generate commands dict dynamically from registry
    @staticmethod
    def get_commands():
        commands = {}
        for cmd_name, cmd_info in CommandRegistry.commands.items():
            category = cmd_info['category']
            if category not in commands:
                commands[category] = []
            commands[category].append(cmd_name)
        return commands

    @staticmethod
    def is_valid_command(command_str):
        """Check if a string starts with a valid command"""
        parts = command_str.strip().split()
        if not parts:
            return False
        return parts[0].lower() in CommandRegistry.commands
    
    @staticmethod
    def is_numeric_expression(expr):
        """Check if expression is purely numeric/mathematical"""
        expr = expr.strip()
        # Remove spaces and check if it's a simple numeric expression
        expr_clean = expr.replace(' ', '')
        
        # Allow digits, operators, parentheses, and decimal points
        allowed_chars = set('0123456789+-*/.%()')
        
        # Must contain at least one digit
        has_digit = any(c.isdigit() for c in expr_clean)
        
        # All characters must be allowed
        all_allowed = all(c in allowed_chars for c in expr_clean)
        
        return has_digit and all_allowed

    @staticmethod  
    def get_command_list():
        commands = Command.get_commands()
        result_lines = []
        
        # Define max width for command display
        max_line_width = 100
        
        category_count = 0
        total_categories = len(commands)
        
        for category, cmd_list in commands.items():
            category_count += 1
            
            # Start the category line
            category_prefix = Text.INDENT + f"\n{category:<{9}} : "
            current_line = category_prefix
            line_length = len(category_prefix)
            
            for i, cmd in enumerate(cmd_list):
                colored_cmd = f"/> {Fore.MAGENTA}{cmd.ljust(10)}{Style.RESET_ALL}"
                cmd_display_length = len(f"/> {cmd.ljust(10)}")
                
                if line_length + cmd_display_length > max_line_width and i > 0:
                    result_lines.append(current_line)
                    current_line = "\n" + Text.INDENT + " " * 7 + ": "
                    line_length = len(current_line)

                current_line += colored_cmd
                line_length += cmd_display_length
            
            result_lines.append(current_line)
            
            # Add visual separation after each category except the last
            if category_count <= total_categories:
                result_lines.append("\n" + "─" * 85)
        
        return "\n".join(result_lines)

    @staticmethod
    def show_command_help(command_name):
        """Show detailed help for a specific command"""
        if command_name not in CommandRegistry.commands:
            System.throw_error(f"COMMAND '{command_name}' NOT FOUND")
            return
        
        cmd_info = CommandRegistry.commands[command_name]
        help_text = f"{Fore.MAGENTA}<_ {command_name.upper()} _>{Style.RESET_ALL}\n"
        help_text += f"\n{cmd_info['category']} <> "
        help_text += f"{cmd_info['description']}\n\n"
        
        # Format usage with magenta color for command text
        usage_lines = cmd_info['usage'].split('\n')
        help_text += "<_ USAGE _>\n"
        for usage_line in usage_lines:
            if usage_line.strip():
                help_text += f"{Text.INDENT}/> {Fore.MAGENTA}{usage_line.strip()}{Style.RESET_ALL}\n"
        
        if cmd_info['examples']:
            help_text += f"\n<_ EXAMPLES _>"
            for example in cmd_info['examples']:
                # Add "/> " prefix and apply magenta color to the command
                help_text += f"\n{Text.INDENT}/> {Fore.MAGENTA}{example}{Style.RESET_ALL}"

        Sound.play_and_print("help", help_text)

    @staticmethod
    def resolve_inline_commands(command, user):
        """Resolve inline commands for no-argument commands"""
        global last_command_result
        
        no_arg_commands = ["date", "time", "dir"]
        words = command.split()
        
        # Don't process if it's just a standalone command or dir with navigation arguments
        if len(words) == 1 and words[0].lower() in no_arg_commands:
            return command
        elif len(words) >= 2 and words[0].lower() == "dir":
            return command
        # Don't process if it's a help command - preserve the argument as-is
        elif len(words) >= 2 and words[0].lower() == "help":
            return command
        
        result_command = []
        
        for word in words:
            if word.lower() in no_arg_commands:
                prev_result = last_command_result
                
                if Command.process_single_command(word, user=True):
                    if last_command_result:
                        if last_command_result[1] == DataType.STRING:
                            result_command.append(f'"{last_command_result[0]}"')
                        else:
                            result_command.append(str(last_command_result[0]))
                    else:
                        result_command.append(word)
                else:
                    result_command.append(word)
            else:
                result_command.append(word)
        
        return ' '.join(result_command)

    @staticmethod
    def process_single_command(command):
        """Process a single command and return success status"""
        global last_command_result
        
        prev_result = last_command_result
        
        try:
            parts = command.split()
            if not parts:
                last_command_result = ("NULL", DataType.NULL)  # FAILED - set NULL
                return False

            cmd = parts[0].lower()
            args = parts[1:]

            # Use registry for validation
            if cmd not in CommandRegistry.commands:
                last_command_result = ("NULL", DataType.NULL)  # FAILED - set NULL
                return False

            # Get command category from registry
            cmd_category = CommandRegistry.commands[cmd]['category']

            # Execute the command through registry
            try:
                # Math commands: don't print when nested
                if cmd_category == "MATH":
                    Command.process_math_command(cmd, args, should_print=False)
                    if last_command_result is None or last_command_result[1] == DataType.NULL:
                        last_command_result = ("NULL", DataType.NULL)
                        return False
                    return True
                # I/O commands: always print their output
                elif cmd_category == "I/O":
                    Command.process_io_command(cmd, args)
                    # Check if command actually succeeded
                    if last_command_result is None or last_command_result[1] == DataType.NULL:
                        last_command_result = ("NULL", DataType.NULL)
                        return False
                    return True
                # Date and time: store result but DON'T print (will be printed at outermost level if needed)
                elif cmd == "date":
                    result = datetime.datetime.now().strftime('%m-%d-%Y')
                    last_command_result = (result, DataType.STRING)
                    return True
                elif cmd == "time":
                    result = datetime.datetime.now().strftime('%I:%M:%S %p')
                    last_command_result = (result, DataType.STRING)
                    return True
                else:
                    # For other commands, try the registry
                    success = CommandRegistry.commands[cmd]['func'](args)
                    if not success:
                        last_command_result = ("NULL", DataType.NULL)  # FAILED - set NULL
                    return success
                    
            except Exception as e:
                last_command_result = ("NULL", DataType.NULL)  # FAILED - set NULL
                return False
                
        except Exception:
            last_command_result = ("NULL", DataType.NULL)  # FAILED - set NULL
            return False
        
    @staticmethod
    def process_math_command(cmd, args, should_print=True):
        """Process mathematical commands
        
        Args:
            should_print: If True, print the result. If False, only store in last_command_result
        """
        global last_command_result
        
        try:
            if cmd == "calc":
                if not args:
                    System.throw_error("EXPRESSION REQUIRED FOR 'calc'")
                    return
                
                expression = ' '.join(args)
                
                # Only resolve parentheses that contain valid COMMANDS, not mathematical expressions
                while '(' in expression and ')' in expression:
                    start = -1
                    command_found = False
                    
                    for i, char in enumerate(expression):
                        if char == '(':
                            start = i
                        elif char == ')' and start != -1:
                            inner = expression[start+1:i].strip()
                            
                            # Check if it's a valid command (starts with a command word)
                            inner_parts = inner.split()
                            if inner_parts and Command.is_valid_command(inner):
                                # It's a command - resolve it
                                prev_result = last_command_result

                                if Command.process_single_command(inner):
                                    if last_command_result and last_command_result[1] == DataType.NUMBER:
                                        result_value = last_command_result[0]
                                        expression = expression[:start] + str(result_value) + expression[i+1:]
                                        last_command_result = prev_result
                                        command_found = True
                                        break
                                    else:
                                        System.throw_error(f"Command '{inner}' did not produce a numeric result")
                                        return
                                else:
                                    System.throw_error(f"Command '{inner}' failed")
                                    return
                            else:
                                # It's not a command - it's regular math, leave it alone
                                break
                    
                    if not command_found:
                        # No more commands found in parentheses
                        break
                
                # Now remove spaces for mathematical processing
                expression = expression.replace(' ', '')
                
                # Handle "result" keyword
                if "result" in expression.lower():
                    if last_command_result and last_command_result[1] == DataType.NUMBER:
                        expression = re.sub(r'\bresult\b', str(last_command_result[0]), 
                                        expression, flags=re.IGNORECASE)
                    else:
                        System.throw_error("NO NUMERIC RESULT AVAILABLE OR RESULT NOT A NUMBER")
                        return

                # Handle variables
                for var_name in re.findall(r'[\$#]\w+', expression):
                    var = VariableManager.get_variable(var_name)
                    if var and var.type == DataType.NUMBER:
                        expression = expression.replace(var_name, str(var.value))
                    else:
                        System.throw_error(f"Variable '{var_name}' not found or not a number")
                        return
                
                # Validate and calc
                expression = expression.replace('^', '**')
                allowed_chars = set('0123456789+-*/.%()')
                if not all(char in allowed_chars for char in expression):
                    System.throw_error("INVALID CHARACTERS IN EXPRESSION")
                    return
                
                try:
                    result = eval(expression)
                    last_command_result = (result, DataType.NUMBER)
                    if should_print:
                        System.show_result(result)
                except ZeroDivisionError:
                    System.throw_error("DIVISION BY ZERO NOT ALLOWED")
                except:
                    System.throw_error("INVALID EXPRESSION")
                return

            try:
                numbers = []
                for arg in args:
                    numbers.append(ArgumentResolver.resolve_argument(arg, DataType.NUMBER))
                
                min_args = 2 if cmd not in ["sqrt", "factorial"] else 1
                if len(numbers) < min_args:
                    System.throw_error(f"AT LEAST {min_args} NUMBER(S) REQUIRED FOR '{cmd}'")
                    return

                if cmd == "add":
                    result = sum(numbers)
                elif cmd == "subtract":
                    result = numbers[0] - sum(numbers[1:])
                elif cmd == "multiply":
                    result = 1
                    for num in numbers:
                        result *= num
                elif cmd == "divide":
                    result = numbers[0]
                    for num in numbers[1:]:
                        if num == 0:
                            System.throw_error("DIVISION BY ZERO NOT ALLOWED")
                            return
                        result /= num
                elif cmd == "exponent":
                    result = numbers[0]
                    for num in numbers[1:]:
                        result = result ** num
                elif cmd == "sqrt":
                    if len(numbers) != 1:
                        System.throw_error("SQRT REQUIRES EXACTLY 1 NUMBER")
                        return
                    if numbers[0] < 0:
                        System.throw_error("CANNOT TAKE SQUARE ROOT OF NEGATIVE NUMBER")
                        return
                    result = numbers[0] ** 0.5
                elif cmd == "factorial":
                    if len(numbers) != 1:
                        System.throw_error("FACTORIAL REQUIRES EXACTLY 1 NUMBER")
                        return
                    if numbers[0] < 0:
                        System.throw_error("FACTORIAL REQUIRES NON-NEGATIVE NUMBER")
                        return
                    if numbers[0] != int(numbers[0]):
                        System.throw_error("FACTORIAL REQUIRES INTEGER")
                        return
                    result = 1.0  # Start with float
                    for i in range(1, int(numbers[0]) + 1):
                        result *= i
                elif cmd == "average":
                    result = sum(numbers) / len(numbers)
                    
                last_command_result = (result, DataType.NUMBER)
                if should_print:
                    System.show_result(result)
                    
            except ValueError as e:
                System.throw_error(str(e).upper())
                
        except Exception as e:
            System.throw_error(f"ERROR: {str(e).upper()}")
        
    @staticmethod
    def process_io_command(cmd, args):
        """Process I/O file commands - always displays visual output"""

        global current_directory, last_command_result, clipboard_file, current_user
        
        def print_file_content(display_name, full_path=None, lines_array=None):
            """Helper function to display file content with line numbers - preserves all formatting"""
            if lines_array is not None:
                System.print_slow(f"\n{display_name}:")
                System.print_instant(f"{'-'*50}")
                
                for i, line in enumerate(lines_array, 1):
                    System.print_instant(f"{i:<4}| {line}")
                
                System.print_instant(f"{'-'*50}")

        def show_directory_tree():
            """Show directory tree from user's home directory"""
            base_user_dir = VariableManager.get_user_root(current_user)
            relative_path = VariableManager.get_relative_path(current_directory)
            
            System.print_instant(f"\nCURRENT DIRECTORY: {relative_path}")
            System.print_instant("\nDIRECTORY TREE:")
            System.print_instant("=" * 50)

            def print_tree(directory, prefix="", is_root=True, parent_color="", depth_from_current=None):
                try:
                    items = sorted(os.listdir(directory))
                    dirs = [item for item in items if os.path.isdir(os.path.join(directory, item))]
                    files = [item for item in items if os.path.isfile(os.path.join(directory, item))]
                    
                    dir_abs_path = os.path.abspath(directory)
                    current_abs_path = os.path.abspath(current_directory)
                    
                    is_current = dir_abs_path == current_abs_path
                    
                    # Initialize depth tracking
                    if depth_from_current is None:
                        depth_from_current = 0 if is_current else None
                    
                    if is_root:
                        if is_current:
                            System.print_instant(f"{Fore.YELLOW}HOME/{Style.RESET_ALL}")
                        else:
                            System.print_instant("HOME/")
                    
                    # Determine the color for items in this directory
                    if is_current:
                        item_color = Fore.MAGENTA
                        connector_color = Fore.YELLOW  # Current dir uses yellow connectors
                    else:
                        item_color = parent_color
                        connector_color = parent_color
                    
                    # Process directories first
                    for i, dir_name in enumerate(dirs):
                        is_last_dir = (i == len(dirs) - 1) and len(files) == 0
                        connector = "└── " if is_last_dir else "├── "
                        
                        dir_path = os.path.join(directory, dir_name)
                        child_abs_path = os.path.abspath(dir_path)
                        
                        # Check if this child is the current directory
                        child_is_current = child_abs_path == current_abs_path
                        
                        # Calculate depth from current directory
                        if depth_from_current is not None:
                            child_depth = depth_from_current + 1
                        else:
                            child_depth = None
                        
                        # Determine child's display color based on depth
                        if child_is_current:
                            display_color = Fore.YELLOW
                            child_inherit_color = Fore.YELLOW
                        elif depth_from_current == 0:  # Direct child of current directory
                            display_color = Fore.MAGENTA
                            child_inherit_color = Fore.MAGENTA
                        elif depth_from_current == 1:  # Grandchild of current directory - RESET TO DEFAULT
                            display_color = Style.RESET_ALL
                            child_inherit_color = Style.RESET_ALL
                        else:
                            display_color = item_color
                            child_inherit_color = item_color
                        
                        # Print with proper coloring
                        System.print_instant(f"{prefix}{connector_color}{connector}{Style.RESET_ALL}{display_color}{dir_name}/{Style.RESET_ALL}")
                        
                        # Build prefix for children
                        extension = "    " if is_last_dir else "│   "
                        new_prefix = f"{prefix}{connector_color}{extension}{Style.RESET_ALL}"
                        
                        # Recursively print tree, passing depth information
                        print_tree(dir_path, new_prefix, False, child_inherit_color, child_depth)
                    
                    # Process files  
                    for i, file_name in enumerate(files):
                        is_last = i == len(files) - 1
                        connector = "└── " if is_last else "├── "
                        
                        # Determine file color based on depth
                        if depth_from_current is not None and depth_from_current >= 1:
                            file_color = Style.RESET_ALL
                        else:
                            file_color = item_color
                        
                        # Print file with proper coloring
                        System.print_instant(f"{prefix}{connector_color}{connector}{Style.RESET_ALL}{file_color}{file_name}{Style.RESET_ALL}")
                                
                except PermissionError:
                    System.print_instant(f"{prefix}└── [Permission Denied]", is_error=True)
                except Exception as e:
                    System.print_instant(f"{prefix}└── [Error: {str(e)}]", is_error=True)

            # Always show tree from HOME (base_user_dir), not current_directory
            print_tree(base_user_dir)
            System.print_instant("=" * 50)

        try:
            if cmd == "copy":
                if len(args) == 1:
                    # Single argument - copy to clipboard
                    source_name = args[0]
                    source_path, source_type = PathResolver.resolve_file_or_directory_argument(
                        source_name, current_directory
                    )
                    if source_path is None:
                        System.throw_error(f"'{source_name}' NOT FOUND")
                        return
                    clipboard_file = (source_path, source_type)
                    last_command_result = (VariableManager.get_relative_path(source_path), source_type)
                    System.show_result(f"'{os.path.basename(source_path)}' COPIED TO CLIPBOARD")
                        
                elif len(args) == 2:
                    # Two arguments - copy source to destination
                    source_name, dest_name = args[0], args[1]
                    source_path, source_type = PathResolver.resolve_file_or_directory_argument(
                        source_name, current_directory
                    )
                    if source_path is None:
                        System.throw_error(f"'{source_name}' NOT FOUND")
                        return
                    
                    dest_path = PathResolver.resolve_directory_argument(
                        dest_name, current_directory
                    )
                    if dest_path is None:
                        System.throw_error(f"DIRECTORY '{dest_name}' NOT FOUND")
                        return
                    
                    # Determine destination file/folder path
                    source_basename = os.path.basename(source_path)
                    final_dest_path = os.path.join(dest_path, source_basename)
                    
                    # Perform copy operation
                    if source_type == DataType.FILE:
                        shutil.copy2(source_path, final_dest_path)
                    else:  # DIRECTORY
                        shutil.copytree(source_path, final_dest_path)
                    
                    last_command_result = (VariableManager.get_relative_path(final_dest_path), source_type)
                    show_directory_tree()
                    System.show_result(f"'{source_basename}' COPIED TO '{os.path.basename(dest_path)}'")
                else:
                    System.throw_error("COPY REQUIRES 1 OR 2 ARGUMENTS")
            
            elif cmd == "paste":
                if clipboard_file is None:
                    System.throw_error("NO FILE IN CLIPBOARD - USE 'copy' OR 'cut' FIRST")
                    return
                
                # Handle both copy and cut
                if len(clipboard_file) == 3:
                    source_path, source_type, is_cut = clipboard_file
                else:
                    source_path, source_type = clipboard_file
                    is_cut = False
                
                if len(args) == 0:
                    # No arguments - paste to current directory
                    dest_path = current_directory
                elif len(args) == 1:
                    # One argument - paste to specified directory
                    dest_path = PathResolver.resolve_directory_argument(
                        args[0], current_directory
                    )
                    if dest_path is None:
                        System.throw_error(f"DIRECTORY '{args[0]}' NOT FOUND")
                        return
                else:
                    System.throw_error("PASTE REQUIRES 0 OR 1 ARGUMENTS")
                    return
                
                try:
                    # Determine destination file/folder path
                    source_basename = os.path.basename(source_path)
                    final_dest_path = os.path.join(dest_path, source_basename)
                    
                    # Check if destination already exists
                    if os.path.exists(final_dest_path):
                        System.throw_error(f"'{source_basename}' ALREADY EXISTS IN DESTINATION")
                        return
                    
                    # Perform paste operation
                    if source_type == DataType.FILE:
                        shutil.copy2(source_path, final_dest_path)
                    else:  # DIRECTORY
                        shutil.copytree(source_path, final_dest_path)
                    
                    # If it was a cut operation, remove the original file
                    if is_cut:
                        try:
                            if source_type == DataType.FILE:
                                os.remove(source_path)
                            else:
                                shutil.rmtree(source_path)
                            # Clear clipboard after successful cut-paste
                            clipboard_file = None
                            action_word = "MOVED"
                        except Exception as e:
                            System.throw_error(f"PASTE SUCCEEDED BUT ORIGINAL REMOVAL FAILED: {str(e).upper()}")
                            action_word = "COPIED"
                    else:
                        action_word = "PASTED"

                    last_command_result = (VariableManager.get_relative_path(final_dest_path), source_type)
                    dest_display = os.path.basename(dest_path) if dest_path != current_directory else "current directory"
                    show_directory_tree()
                    System.show_result(f"'{source_basename}' {action_word} TO '{dest_display}'")
                        
                except Exception as e:
                    System.throw_error(f"PASTE FAILED: {str(e).upper()}")

            elif cmd == "rename":
                if len(args) != 2:
                    System.throw_error("RENAME REQUIRES EXACTLY 2 ARGUMENTS: SOURCE AND NEW_NAME")
                    return
                    
                source_name, new_name_arg = args[0], args[1]
                
                try:
                    source_name, new_name_arg = args[0], args[1]
    
                    # Resolve source path
                    source_path, source_type = PathResolver.resolve_file_or_directory_argument(
                        source_name, current_directory
                    )
                    if source_path is None:
                        System.throw_error(f"'{source_name}' NOT FOUND")
                        return
                    
                    # Resolve new name (must be a string)
                    if new_name_arg.startswith('"') and new_name_arg.endswith('"'):
                        new_name = new_name_arg[1:-1]  # Remove quotes
                    elif new_name_arg.startswith('$') or new_name_arg.startswith('#'):
                        var = VariableManager.get_variable(new_name_arg)
                        if var and var.type == DataType.STRING:
                            new_name = var.value
                        else:
                            System.throw_error(f"Variable '{new_name_arg}' not found or not a string")
                            return
                    elif new_name_arg.lower() == "result":
                        if last_command_result and last_command_result[1] == DataType.STRING:
                            new_name = last_command_result[0]
                        else:
                            System.throw_error("No string result available for new name")
                            return
                    else:
                        new_name = new_name_arg  # Treat as literal string
                    
                    # Construct new path in same directory
                    source_dir = os.path.dirname(source_path)
                    new_path = os.path.join(source_dir, new_name)
                    
                    # Check if target already exists
                    if os.path.exists(new_path):
                        System.throw_error(f"'{new_name}' ALREADY EXISTS IN TARGET LOCATION")
                        return
                    
                    # Perform rename
                    os.rename(source_path, new_path)
                    
                    last_command_result = (VariableManager.get_relative_path(new_path), source_type)
                    show_directory_tree()
                    System.show_result(f"'{os.path.basename(source_path)}' RENAMED TO '{new_name}'")

                except Exception as e:
                    System.throw_error(f"RENAME FAILED: {str(e).upper()}")

            elif cmd == "move":
                if len(args) != 2:
                    System.throw_error("MOVE REQUIRES EXACTLY 2 ARGUMENTS: SOURCE AND DESTINATION")
                    return
                    
                source_name, dest_name = args[0], args[1]
                
                try:
                    source_name, dest_name = args[0], args[1]
    
                    # Resolve source path
                    source_path, source_type = PathResolver.resolve_file_or_directory_argument(
                        source_name, current_directory
                    )
                    if source_path is None:
                        System.throw_error(f"'{source_name}' NOT FOUND")
                        return
                    
                    # Resolve destination directory
                    dest_path = PathResolver.resolve_directory_argument(
                        dest_name, current_directory
                    )
                    if dest_path is None:
                        System.throw_error(f"DIRECTORY '{dest_name}' NOT FOUND")
                        return
                    
                    # Resolve destination directory
                    dest_path = PathResolver.resolve_directory_argument(
                        dest_name, current_directory
                    )
                    
                    # Determine final destination path
                    source_basename = os.path.basename(source_path)
                    final_dest_path = os.path.join(dest_path, source_basename)
                    
                    # Check if destination already exists
                    if os.path.exists(final_dest_path):
                        System.throw_error(f"'{source_basename}' ALREADY EXISTS IN DESTINATION")
                        return
                    
                    # Perform move operation
                    shutil.move(source_path, final_dest_path)
                    
                    last_command_result = (VariableManager.get_relative_path(final_dest_path), source_type)
                    dest_display = os.path.basename(dest_path) if dest_path != current_directory else "current directory"
                    show_directory_tree()
                    System.show_result(f"'{source_basename}' MOVED TO '{dest_display}'")

                except Exception as e:
                    System.throw_error(f"MOVE FAILED: {str(e).upper()}")

            elif cmd == "cut":
                if len(args) != 1:
                    System.throw_error("CUT REQUIRES EXACTLY 1 ARGUMENT: SOURCE")
                    return
                    
                source_name = args[0]
                
                try:
                    source_name = args[0]
    
                    # Resolve source path
                    source_path, source_type = PathResolver.resolve_file_or_directory_argument(
                        source_name, current_directory
                    )
                    if source_path is None:
                        System.throw_error(f"'{source_name}' NOT FOUND")
                        return
                    
                    # Store in clipboard with cut flag
                    clipboard_file = (source_path, source_type, True)  # True indicates cut operation
                    
                    last_command_result = (VariableManager.get_relative_path(source_path), source_type)
                    System.show_result(f"'{os.path.basename(source_path)}' CUT TO CLIPBOARD")
                        
                except ValueError as e:
                    System.throw_error(str(e).upper())

            elif cmd == "dir":
                base_user_dir = VariableManager.get_user_root(current_user)
                
                if not args:
                    # Show directory tree only
                    show_directory_tree()
                    
                    # Build relative path with proper casing
                    if current_directory == base_user_dir:
                        relative_path = "/"
                    else:
                        relative_path = current_directory[len(base_user_dir):].replace(os.sep, '/')
                        if not relative_path.startswith('/'):
                            relative_path = '/' + relative_path
                    
                    last_command_result = (relative_path, DataType.DIRECTORY)
                    System.show_result("DIRECTORY LISTING COMPLETE")
                    
                    return
                
                # Navigation functionality
                arg = args[0]
                
                if arg.lower() == "home":
                    current_directory = base_user_dir
                    show_directory_tree()
                    last_command_result = ("/", DataType.DIRECTORY)
                    System.show_result("CHANGED TO HOME DIRECTORY")
                
                elif arg == "-":
                    parent_dir = os.path.dirname(current_directory)
                    if os.path.commonpath([parent_dir, base_user_dir]) == base_user_dir and parent_dir != base_user_dir:
                        current_directory = parent_dir
                    elif parent_dir == base_user_dir:
                        current_directory = base_user_dir
                    else:
                        System.throw_error("CANNOT GO ABOVE HOME DIRECTORY")
                        return
                    
                    show_directory_tree()
                    full_relative_path = current_directory[len(base_user_dir):].replace(os.sep, '/') if current_directory != base_user_dir else ""
                    full_relative_path = '/' + full_relative_path if full_relative_path and not full_relative_path.startswith('/') else full_relative_path or '/'
                    last_command_result = (full_relative_path, DataType.DIRECTORY)
                    System.show_result(f"CHANGED TO DIRECTORY: {full_relative_path}")
                
                elif arg == "+":
                    subdirs = sorted([d for d in os.listdir(current_directory) if os.path.isdir(os.path.join(current_directory, d))])
                    if subdirs:
                        first_dir = os.path.join(current_directory, subdirs[0])
                        current_directory = first_dir
                    else:
                        System.throw_error("NO SUBDIRECTORIES AVAILABLE")
                        return
                    
                    show_directory_tree()
                    full_relative_path = current_directory[len(base_user_dir):].replace(os.sep, '/') if current_directory != base_user_dir else ""
                    full_relative_path = '/' + full_relative_path if full_relative_path and not full_relative_path.startswith('/') else full_relative_path or '/'
                    last_command_result = (full_relative_path, DataType.DIRECTORY)
                    System.show_result(f"CHANGED TO DIRECTORY: {full_relative_path}")
                
                else:
                    try:
                        if arg.startswith('$') or arg.startswith('#'):
                            var = VariableManager.get_variable(arg)
                            if var and var.type == DataType.DIRECTORY:
                                target_dir = VariableManager.resolve_path(var.value)
                            else:
                                System.throw_error(f"Variable '{arg}' not found or not a directory")
                                return
                        elif arg.startswith('/'):
                            target_dir = VariableManager.resolve_path(arg)
                        else:
                            # Case-insensitive search that preserves actual directory name
                            found_dir = None
                            search_path = os.path.join(current_directory, arg)
                            
                            # First try exact match
                            if os.path.exists(search_path) and os.path.isdir(search_path):
                                found_dir = search_path
                            else:
                                # Case-insensitive search
                                try:
                                    for item in os.listdir(current_directory):
                                        if item.lower() == arg.lower():
                                            test_path = os.path.join(current_directory, item)
                                            if os.path.isdir(test_path):
                                                found_dir = test_path
                                                break
                                except:
                                    pass
                            
                            if found_dir:
                                target_dir = found_dir
                            else:
                                System.throw_error(f"DIRECTORY '{arg}' NOT FOUND")
                                return
                        
                        if os.path.exists(target_dir) and os.path.isdir(target_dir):
                            if os.path.commonpath([target_dir, base_user_dir]) == base_user_dir:
                                # ✅ Normalize to real filesystem casing
                                def normalize_path_casing(path):
                                    """Return the actual filesystem path with correct casing from the OS."""
                                    if not os.path.exists(path):
                                        return path
                                    drive, path_rest = os.path.splitdrive(os.path.abspath(path))
                                    parts = path_rest.strip(os.sep).split(os.sep)
                                    cur = drive + os.sep if drive else os.sep
                                    for p in parts:
                                        try:
                                            entries = os.listdir(cur)
                                            match = next((e for e in entries if e.lower() == p.lower()), p)
                                            cur = os.path.join(cur, match)
                                        except (FileNotFoundError, PermissionError):
                                            cur = os.path.join(cur, p)
                                    return os.path.normpath(cur)

                                # ✅ Use normalized version instead of raw user-typed path
                                current_directory = normalize_path_casing(target_dir)
                                
                                # Show tree and result
                                show_directory_tree()
                                full_relative_path = current_directory[len(base_user_dir):].replace(os.sep, '/') if current_directory != base_user_dir else ""
                                full_relative_path = '/' + full_relative_path if full_relative_path and not full_relative_path.startswith('/') else full_relative_path or '/'
                                last_command_result = (full_relative_path, DataType.DIRECTORY)
                                System.show_result(f"CHANGED TO DIRECTORY: {full_relative_path}")
                            else:
                                System.throw_error("ACCESS DENIED - OUTSIDE USER DIRECTORY")
                                return
                        else:
                            System.throw_error(f"DIRECTORY '{arg}' NOT FOUND")
                            return
                    except ValueError as e:
                        System.throw_error(str(e).upper())

            elif cmd == "create":
                if not args:
                    System.throw_error("NAME REQUIRED FOR 'create'")
                    return
                
                # Parse arguments respecting quotes
                parsed_names = ArgumentParser.parse_args_with_quotes(args)
                
                created_count = 0
                created_items = []  # Track what was created
                for name in parsed_names:
                    full_path = os.path.join(current_directory, name)
                    
                    if os.path.exists(full_path):
                        System.print_instant(f"\n'{name}' ALREADY EXISTS", is_error=True)
                        continue
                    
                    try:
                        if '.' in name:
                            with open(full_path, 'w') as f:
                                f.write("")
                            created_items.append((name, "FILE"))
                            created_count += 1
                        else:
                            os.makedirs(full_path)
                            created_items.append((name, "DIRECTORY"))
                            created_count += 1
                    except Exception as e:
                        System.print_instant(f"\nERROR CREATING '{name}': {str(e).upper()}", is_error=True)
                        continue

                if created_count > 0:
                    # Set last result to the last created item
                    last_command_result = (VariableManager.get_relative_path(full_path), 
                                        DataType.FILE if '.' in name else DataType.DIRECTORY)
                    
                    show_directory_tree()
                    
                    # Show creation messages after tree
                    for item_name, item_type in created_items:
                        System.print_instant(f"\n{item_type} '{item_name}' CREATED")
                    
                    Sound.play_and_print("enter")
                
            elif cmd == "delete":
                if not args:
                    System.throw_error("NAME REQUIRED FOR 'delete'")
                    return
                
                # Parse arguments respecting quotes
                parsed_names = ArgumentParser.parse_args_with_quotes(args)
                
                # Get user's home directory for protection
                user_home = VariableManager.get_user_root(current_user)
                
                deleted_count = 0
                deleted_items = []  # Track what was deleted
                current_dir_deleted = False  # Track if current directory was deleted
                
                for name in parsed_names:
                    source_path, source_type = PathResolver.resolve_file_or_directory_argument(
                        name, current_directory
                    )
                    if source_path is None:
                        System.throw_error(f"'{name}' NOT FOUND")
                        continue
                    
                    try:
                        
                        # CRITICAL: Protect home directory from deletion
                        if os.path.abspath(source_path) == os.path.abspath(user_home):
                            System.throw_error(f"CANNOT DELETE HOME DIRECTORY - ACCESS DENIED")
                            continue
                        
                        # CRITICAL: Protect any parent directories of home directory
                        if os.path.abspath(user_home).startswith(os.path.abspath(source_path)):
                            System.throw_error(f"CANNOT DELETE PARENT OF HOME DIRECTORY - ACCESS DENIED")
                            continue
                        
                        # Check if we're deleting current directory or one of its parents
                        current_abs = os.path.abspath(current_directory)
                        source_abs = os.path.abspath(source_path)
                        
                        if current_abs == source_abs or current_abs.startswith(source_abs + os.sep):
                            current_dir_deleted = True
                        
                        # Store info before deletion
                        item_name = os.path.basename(source_path)
                        item_type = "FILE" if source_type == DataType.FILE else "DIRECTORY"
                        
                        # Perform deletion
                        if source_type == DataType.FILE:
                            os.remove(source_path)
                        else:
                            shutil.rmtree(source_path)
                        
                        deleted_items.append((item_name, item_type))
                        deleted_count += 1
                        
                    except Exception as e:
                        System.print_instant(f"ERROR DELETING '{name}': {str(e).upper()}", is_error=True)
                        continue

                if deleted_count > 0:
                    # If current directory was deleted, reset to home
                    if current_dir_deleted:
                        current_directory = user_home
                    
                    show_directory_tree()
                    
                    # Show deletion messages after tree
                    for item_name, item_type in deleted_items:
                        System.print_instant(f"\n{item_type} '{item_name}' DELETED")
                    
                    if current_dir_deleted:
                        System.print_instant(f"\nCURRENT DIRECTORY WAS DELETED - RESET TO HOME")
                    
                    Sound.play_and_print("enter")

            elif cmd == "read":
                if not args:
                    System.throw_error("FILENAME REQUIRED FOR 'read'")
                    return

                filename = args[0]
                
                full_path = PathResolver.resolve_file_argument(filename, last_command_result, current_directory)
                if full_path is None:
                    System.throw_error(f"FILE '{filename}' NOT FOUND OR CANNOT BE READ")
                    return
                display_name = os.path.basename(full_path)
                
                try:
                    # Read file content
                    with open(full_path, 'r') as f:
                        content = f.read()
                    
                    # Store content as string result
                    last_command_result = (content, DataType.STRING)
                    
                    # Display file with line numbers
                    if content == '':
                        lines = ['']
                    else:
                        lines = content.split('\n')
                    
                    print_file_content(display_name, lines_array=lines)
                    System.show_result(f"FILE '{display_name}' READ SUCCESSFULLY")

                except Exception as e:
                    System.throw_error(f"FILE '{filename}' NOT FOUND OR CANNOT BE READ")
            elif cmd == "forget":
                if not args:
                    System.throw_error("VARIABLE NAME(S) REQUIRED FOR 'forget'")
                    return
                
                deleted_count = 0
                System.print_instant("")
                for var_name in args:
                    if not (var_name.startswith('$') or var_name.startswith('#')):
                        System.throw_error(f"INVALID VARIABLE NAME: '{var_name}' - MUST START WITH $ OR #")
                        continue
                    
                    if var_name.startswith('$'):
                        if var_name in persistent_variables:
                            del persistent_variables[var_name]
                            VariableManager.save_persistent_variables(current_user)
                            System.print_instant(f"DELETED PERSISTENT VARIABLE: {var_name}")
                            deleted_count += 1
                        else:
                            System.print_instant(f"PERSISTENT VARIABLE NOT FOUND: {var_name}", is_error=True)
                    else:  # var_name.startswith('#')
                        if var_name in session_variables:
                            del session_variables[var_name]
                            System.print_instant(f"DELETED SESSION VARIABLE: {var_name}")
                            deleted_count += 1
                        else:
                            System.print_instant(f"SESSION VARIABLE NOT FOUND: {var_name}", is_error=True)

                Sound.play_and_print("enter")

            elif cmd == "vars":
                output = "VARIABLES:\n"
                output += "=" * 50 + "\n"
                
                # Display persistent variables
                if persistent_variables:
                    output += "PERSISTENT ($):\n"
                    for name, var in sorted(persistent_variables.items()):
                        type_str = var.type.value.upper()
                        output += f"{Text.INDENT}{Fore.MAGENTA}{name:<15}{Style.RESET_ALL} {Fore.MAGENTA}[{type_str:<9}]{Style.RESET_ALL} = {var.value}\n"
                else:
                    output += "PERSISTENT ($): None\n"
                
                output += "\n"
                
                # Display session variables
                if session_variables:
                    output += "SESSION (#):\n"
                    for name, var in sorted(session_variables.items()):
                        type_str = var.type.value.upper()
                        output += f"{Text.INDENT}{Fore.MAGENTA}{name:<15}{Style.RESET_ALL} {Fore.MAGENTA}[{type_str:<9}]{Style.RESET_ALL} = {var.value}\n"
                else:
                    output += "SESSION (#): None\n"
                
                output += "=" * 50
                
                Sound.play_and_print("enter", output)

        except PermissionError:
            System.throw_error("PERMISSION DENIED")
        except Exception as e:
            System.throw_error(f"OPERATION FAILED: {str(e).upper()}")

    @staticmethod
    def process_variable_assignment(command, user=False):
        """Process variable assignment from command result"""
        global last_command_result, current_user
        
        if "->" not in command:
            return False
        
        parts = command.split("->")
        if len(parts) < 2:
            return False
        
        left_part = parts[0].strip()
        var_names = [part.strip() for part in parts[1:]]
        
        # Validate all variable names first
        for var_name in var_names:
            if not (var_name.startswith('$') or var_name.startswith('#')):
                System.throw_error("VARIABLE NAMES MUST START WITH $ OR #")
                return True
            
            if not re.match(r'^[\$#]\w+$', var_name):
                System.throw_error("INVALID VARIABLE NAME")
                return True
        
        # Get the value to assign
        value = None
        var_type = None
        
        # Handle direct value assignment
        if left_part:
            try:
                # Check for quoted strings - detect multiple values
                quote_count = left_part.count('"')
                if quote_count >= 4:  # At least 2 complete quoted strings
                    System.throw_error("CANNOT ASSIGN MULTIPLE VALUES TO A VARIABLE - USE SINGLE VALUE ONLY")
                    return True
                
                # Check if left_part contains multiple space-separated unquoted values
                # that aren't part of a command
                if not Command.is_valid_command(left_part) and not left_part.startswith('/'):
                    # Check if it's NOT a variable reference or "result"
                    if not (left_part.startswith('$') or left_part.startswith('#') or left_part.lower() == "result"):
                        # Check if it's NOT a single quoted string
                        if not (left_part.startswith('"') and left_part.endswith('"')):
                            # Check if it's NOT a single number
                            if not re.match(r'^-?\d+\.?\d*$', left_part):
                                # Split and check for multiple tokens (excluding operators in expressions)
                                tokens = left_part.split()
                                if len(tokens) > 1:
                                    # It's multiple unquoted words - could be multiple strings
                                    # But allow if it looks like a path or file
                                    if not ('/' in left_part or '.' in left_part):
                                        System.throw_error("CANNOT ASSIGN MULTIPLE VALUES TO A VARIABLE - USE SINGLE VALUE ONLY")
                                        return True
                
                # Check for "result" keyword
                if left_part.lower() == "result":
                    if last_command_result is None:
                        System.throw_error("NO PREVIOUS COMMAND RESULT TO ASSIGN")
                        return True
                    value, var_type = last_command_result
                
                # Check if left_part is a variable reference
                elif left_part.startswith('$') or left_part.startswith('#'):
                    var = VariableManager.get_variable(left_part)
                    if var is not None:
                        value = var.value
                        var_type = var.type
                    else:
                        System.throw_error(f"VARIABLE '{left_part}' NOT FOUND")
                        return True
                
                # Check if it's ANY valid command
                elif Command.is_valid_command(left_part):
                    if Command.process_single_command(left_part):
                        if last_command_result:
                            value, var_type = last_command_result
                        else:
                            System.throw_error(f"COMMAND '{left_part}' DID NOT PRODUCE A RESULT")
                            return True
                    else:
                        System.throw_error(f"COMMAND '{left_part}' FAILED")
                        return True

                # Check for NULL literal
                elif left_part.lower() == "null":
                    value = "NULL"
                    var_type = DataType.NULL

                # Try to parse as number
                elif re.match(r'^-?\d+\.?\d*$', left_part):
                    value = float(left_part)
                    var_type = DataType.NUMBER
                
                # Try to parse as quoted string
                elif left_part.startswith('"') and left_part.endswith('"'):
                    value = left_part[1:-1]
                    var_type = DataType.STRING
                
                # Try to parse as directory path
                elif left_part.startswith('/'):
                    user_root = VariableManager.get_user_root(current_user)
                    path_parts = left_part.strip('/').split('/')
                    current_path = user_root
                    
                    for part in path_parts:
                        if not part:
                            continue
                        found_item = None
                        try:
                            for item in os.listdir(current_path):
                                if item.lower() == part.lower():
                                    found_item = item
                                    current_path = os.path.join(current_path, item)
                                    break
                        except:
                            pass
                        
                        if not found_item:
                            System.throw_error(f"PATH '{left_part}' NOT FOUND")
                            return True
                    
                    # Normalize to actual case
                    current_path = PathResolver.normalize_to_actual_case(current_path)
                    value = VariableManager.get_relative_path(current_path)
                    if os.path.isfile(current_path):
                        var_type = DataType.FILE
                    elif os.path.isdir(current_path):
                        var_type = DataType.DIRECTORY
                    else:
                        System.throw_error(f"PATH '{left_part}' NOT FOUND")
                        return True
                
                # Try as relative file in current directory OR treat as string if not found
                else:
                    full_path = os.path.join(current_directory, left_part)
                    actual_full_path = None
                    found_as_path = False
                    
                    # First check exact match
                    if os.path.exists(full_path):
                        actual_full_path = full_path
                        found_as_path = True
                    else:
                        # Try case-insensitive search
                        try:
                            for item in os.listdir(current_directory):
                                if item.lower() == left_part.lower():
                                    test_path = os.path.join(current_directory, item)
                                    if os.path.exists(test_path):
                                        actual_full_path = test_path
                                        found_as_path = True
                                        break
                        except:
                            pass
                    
                    if found_as_path and actual_full_path:
                        # Normalize to actual case
                        actual_full_path = PathResolver.normalize_to_actual_case(actual_full_path)
                        
                        # It's a valid file or directory
                        if os.path.isfile(actual_full_path):
                            value = VariableManager.get_relative_path(actual_full_path)
                            var_type = DataType.FILE
                        elif os.path.isdir(actual_full_path):
                            value = VariableManager.get_relative_path(actual_full_path)
                            var_type = DataType.DIRECTORY
                        else:
                            # Shouldn't reach here but treat as string
                            value = left_part
                            var_type = DataType.STRING
                    else:
                        # Not a valid path - treat as unquoted string
                        value = left_part
                        var_type = DataType.STRING

            except Exception as e:
                System.throw_error(f"FAILED TO DETERMINE VALUE: {str(e).upper()}")
                return True
        
        # Handle assignment from last command result (when no left_part)
        else:
            if last_command_result is None:
                System.throw_error("NO PREVIOUS COMMAND RESULT TO ASSIGN")
                return True
            
            value, var_type = last_command_result
        
        # Assign to all variables in the chain
        try:
            for var_name in var_names:
                VariableManager.set_variable(var_name, value, var_type)
            
            # Show the assignment message (NOT the value itself)
            if len(var_names) == 1:
                System.show_result(f"VARIABLE '{var_names[0]}' SET TO {value}")
            else:
                var_list = ", ".join(var_names)
                System.show_result(f"VARIABLES {var_list} SET TO {value}")
            
            # Set last_command_result to the assigned value for potential chaining
            last_command_result = (value, var_type)

        except Exception as e:
            System.throw_error(f"FAILED TO SET VARIABLE: {str(e).upper()}")
        
        return True
        
    @staticmethod
    def resolve_parentheses(command_str):
        """
        Resolve parentheses depth-first, executing commands and replacing with their values.
        Returns tuple: (fully resolved string, last_command_executed)
        Returns ("", None) if a command fails (error already displayed)
        """
        global last_command_result
        
        # Count parentheses
        open_count = command_str.count('(')
        close_count = command_str.count(')')
        
        if open_count != close_count:
            raise ValueError("MISMATCHED PARENTHESES")
        
        if open_count == 0:
            return command_str, None  # No parentheses to resolve
        
        # Track the last actual command executed (not variable assignment)
        last_command_executed = None
        
        # Find all parentheses with their depth levels
        def find_deepest_parentheses(s):
            """Find the positions of the deepest (innermost) parentheses"""
            max_depth = 0
            current_depth = 0
            positions = []
            
            for i, char in enumerate(s):
                if char == '(':
                    current_depth += 1
                    if current_depth > max_depth:
                        max_depth = current_depth
                        positions = []
                    if current_depth == max_depth:
                        positions.append(i)
                elif char == ')':
                    current_depth -= 1
            
            # Now find matching closing parentheses for each opening at max depth
            pairs = []
            for open_pos in positions:
                depth = 0
                for i in range(open_pos, len(s)):
                    if s[i] == '(':
                        depth += 1
                    elif s[i] == ')':
                        depth -= 1
                        if depth == 0:
                            pairs.append((open_pos, i))
                            break
            
            return pairs
        
        # Recursively resolve from deepest to shallowest
        while '(' in command_str:
            pairs = find_deepest_parentheses(command_str)
            
            if not pairs:
                break
            
            # Process each pair from right to left (to preserve positions)
            for open_pos, close_pos in sorted(pairs, reverse=True):
                inner_content = command_str[open_pos+1:close_pos].strip()
                
                # Check if it's a variable assignment
                if "->" in inner_content:
                    # It's a variable assignment - track it as "->"
                    last_command_executed = "->"
                    
                    # Execute the assignment silently
                    try:
                        Command.process_variable_assignment(inner_content, user=False)
                        if last_command_result:
                            result_value, result_type = last_command_result
                            if result_type == DataType.NUMBER:
                                replacement = str(result_value)
                            elif result_type == DataType.STRING:
                                replacement = f'"{result_value}"'
                            elif result_type == DataType.NULL:
                                replacement = ""
                            elif result_type in [DataType.FILE, DataType.DIRECTORY]:
                                replacement = f'"{result_value}"'
                            else:
                                replacement = str(result_value)
                        else:
                            replacement = ""
                    except Exception as e:
                        raise ValueError(f"Variable assignment failed: {str(e)}")
                
                # Check if it's a valid command
                elif Command.is_valid_command(inner_content):
                    # Extract the command name
                    cmd_parts = inner_content.split()
                    cmd_name = cmd_parts[0].lower() if cmd_parts else ""
                    
                    # Update last_command_executed with actual command name
                    last_command_executed = cmd_name
                    
                    # Execute the command silently (no try-catch, let errors propagate naturally)
                    if Command.process_single_command(inner_content):
                        if last_command_result:
                            result_value, result_type = last_command_result
                            
                            # Check if command returned NULL - this means it FAILED
                            if result_type == DataType.NULL:
                                # Command failed - error already shown, stop processing
                                return "", None
                            
                            # Format the result appropriately
                            if result_type == DataType.NUMBER:
                                replacement = str(result_value)
                            elif result_type == DataType.STRING:
                                replacement = f'"{result_value}"'
                            elif result_type in [DataType.FILE, DataType.DIRECTORY]:
                                replacement = f'"{result_value}"'
                            else:
                                replacement = str(result_value)
                        else:
                            replacement = ""
                    else:
                        # Command returned False - it failed, error already shown
                        return "", None
                else:
                    # It's just a value, keep it as-is (don't update last_command_executed)
                    replacement = inner_content
                
                # Replace the parenthetical expression with its result
                command_str = command_str[:open_pos] + replacement + command_str[close_pos+1:]
        
        return command_str.strip(), last_command_executed

    @staticmethod
    def resolve_calc_parentheses(calc_command):
        """
        Special resolver for calc command that executes commands in parentheses
        but preserves mathematical parentheses.
        """
        global last_command_result
        
        # Extract the calc expression
        parts = calc_command.strip().split(None, 1)
        if len(parts) < 2:
            return calc_command
        
        expression = parts[1]
        
        # Find command patterns in parentheses
        while True:
            # Look for patterns like (command args)
            found_command = False
            
            i = 0
            while i < len(expression):
                if expression[i] == '(':
                    # Find matching closing parenthesis
                    depth = 1
                    j = i + 1
                    while j < len(expression) and depth > 0:
                        if expression[j] == '(':
                            depth += 1
                        elif expression[j] == ')':
                            depth -= 1
                        j += 1
                    
                    if depth == 0:
                        inner = expression[i+1:j-1].strip()
                        
                        # Check if inner content is a valid command
                        if Command.is_valid_command(inner):
                            # Execute the command
                            prev_result = last_command_result

                            try:
                                # Execute command without parentheses
                                Command.process_single_command(inner)
                                
                                if last_command_result and last_command_result[1] == DataType.NUMBER:
                                    result_value = last_command_result[0]
                                    expression = expression[:i] + str(result_value) + expression[j:]
                                    found_command = True
                                    break
                                else:
                                    raise ValueError(f"Command '{inner}' did not produce a numeric result")
                            except Exception as e:
                                raise ValueError(f"Failed to execute command in calc: {str(e)}")
                    
                    i = j if depth == 0 else i + 1
                else:
                    i += 1
            
            if not found_command:
                break
        
        return f"calc {expression}"

    @staticmethod
    def process_command(command, _recursion_depth=0):
        """Process user commands with proper parentheses resolution"""
        global last_command_result
        
        # Store original command
        original_command = command.strip()
        
        # Check for mismatched parentheses
        open_count = original_command.count('(')
        close_count = original_command.count(')')
        
        if open_count != close_count:
            System.throw_error("INVALID COMMAND SYNTAX - MISMATCHED PARENTHESES")
            return True
        
        # Define commands that should print their result when in parentheses
        do_print_result = [
            "add", "subtract", "multiply", "divide", "exponent", 
            "calc", "sqrt", "average", "factorial", "date", "time"
        ]
        
        # Track last command executed in parentheses
        last_command_in_parens = None
        
        # STEP 1: Resolve all parentheses first (except for calc command)
        try:
            # Check if this is a calc command - if so, handle it specially
            parts = original_command.strip().split(None, 1)
            if parts and parts[0].lower() == 'calc' and '(' in original_command:
                # For calc, resolve commands in parentheses but keep math parentheses
                resolved_command = Command.resolve_calc_parentheses(original_command)
            elif '(' in original_command:
                # Resolve all parentheses for non-calc commands
                resolved_command, last_command_in_parens = Command.resolve_parentheses(original_command)
                
                # Check if parentheses resolution failed (empty string + None means error occurred)
                if resolved_command == "" and last_command_in_parens is None:
                    # Error already displayed by the failed command, just return
                    return True
            else:
                resolved_command = original_command
        except ValueError as e:
            System.throw_error(str(e).upper())
            return True
        
        # STEP 2: Check for variable assignment
        if "->" in resolved_command:
            return Command.process_variable_assignment(resolved_command, user=False)

        # NEW: Check if command resolved to empty (like from help)
        if not resolved_command or not resolved_command.strip():
            return True

        # STEP 3: Check if it's a simple value
        command_trimmed = resolved_command.strip()

        # Handle quoted strings first (before splitting)
        if command_trimmed.startswith('"') and command_trimmed.endswith('"'):
            result = command_trimmed[1:-1]
            last_command_result = (result, DataType.STRING)
            # FIXED: Always print at outermost level
            if _recursion_depth == 0:
                System.show_result(result)
            return True

        parts = command_trimmed.split()

        if len(parts) == 1 and not parts[0].lower() in CommandRegistry.commands:
            try:
                if re.match(r'^-?\d+\.?\d*$', command_trimmed):
                    result = float(command_trimmed)
                    last_command_result = (result, DataType.NUMBER)
                    # FIXED: Always print at outermost level
                    if _recursion_depth == 0:
                        System.show_result(result)
                    return True
                elif command_trimmed.lower() == "result":
                    if last_command_result:
                        # FIXED: Print even if NULL
                        if _recursion_depth == 0:
                            System.show_result(last_command_result[0])
                        return True
                    else:
                        System.throw_error("NO PREVIOUS COMMAND RESULT AVAILABLE")
                        return True
                elif command_trimmed.startswith('$') or command_trimmed.startswith('#'):
                    var = VariableManager.get_variable(command_trimmed)
                    if var:
                        last_command_result = (var.value, var.type)
                        # FIXED: Always print at outermost level (even NULL)
                        if _recursion_depth == 0:
                            System.show_result(var.value)
                        return True
                    else:
                        System.throw_error(f"VARIABLE '{command_trimmed}' NOT FOUND")
                        return True
                else:
                    System.throw_error("COMMAND NOT FOUND")
                    return True
            except Exception as e:
                System.throw_error(f"ERROR PROCESSING VALUE: {str(e).upper()}")
                return True
        
        # STEP 4: Process command normally
        parts = resolved_command.split()
        if not parts:
            System.throw_error("ENTER A VALID COMMAND")
            return True

        cmd = parts[0].lower()
        args = parts[1:]

        if cmd in CommandRegistry.commands:
            try:
                cmd_info = CommandRegistry.commands[cmd]
                return cmd_info['func'](args)
            except Exception as e:
                System.throw_error(f"COMMAND ERROR: {str(e).upper()}")
                return True
        else:
            System.throw_error("COMMAND NOT FOUND")
            return True
           
@CommandRegistry.register("exit", "SYSTEM", 
    "Shuts down the system and exits the program.",
    "exit",
    ["exit"])
def cmd_exit(args):
    global last_command_result
    System.print_instant(Message.SHUTDOWN)
    System.show_loading_bar("shutdown", Fore.RED)
    System.clear_screen()
    last_command_result = ("NULL", DataType.NULL)
    return False

@CommandRegistry.register("reboot", "SYSTEM",
    "Restarts the system session, clearing temporary variables and resetting to boot state.",
    "reboot",
    ["reboot"])
def cmd_reboot(args):
    global last_command_result
    # Reset the terminal state buffer on reboot
    TerminalState.reset()
    System.welcome(current_user)
    last_command_result = ("NULL", DataType.NULL)
    return True

@CommandRegistry.register("help", "SYSTEM",
    "Shows command list or detailed help for specific commands.",
    "help [command_name]",
    ["help", "help copy", "help calc"])
def cmd_help(args):
    global last_command_result
    if args:
        Command.show_command_help(args[0])
    else:
        help_text = (f"<_ COMMANDS _>\n" + Command.get_command_list() + 
                 "\n\n<_ MORE HELP _>\n" +
                 Text.INDENT + f"/> Type '{Fore.MAGENTA}help <command>{Style.RESET_ALL}' for detailed information\n" +
                 Text.INDENT + f"/> Example: {Fore.MAGENTA}help edit{Style.RESET_ALL}, {Fore.MAGENTA}help calc{Style.RESET_ALL}, {Fore.MAGENTA}help copy{Style.RESET_ALL}\n" +
                 "\n<_ VARIABLES _>\n" +
                 Text.INDENT + f"/> Types: {Fore.MAGENTA}number{Style.RESET_ALL}, {Fore.MAGENTA}\"string\"{Style.RESET_ALL}, {Fore.MAGENTA}/directory{Style.RESET_ALL}, {Fore.MAGENTA}file{Style.RESET_ALL}\n" +
                 Text.INDENT + f"/> Assign: {Fore.MAGENTA}value -> $var{Style.RESET_ALL} | {Fore.MAGENTA}-> $var{Style.RESET_ALL} (last command)\n" + 
                 Text.INDENT + f"/> {Fore.MAGENTA}$var{Style.RESET_ALL} for persistent vars | {Fore.MAGENTA}#var{Style.RESET_ALL} for session vars")
        Sound.play_and_print("help", help_text)
    
    # Set NULL result so help doesn't print extra output
    last_command_result = ("NULL", DataType.NULL)
    return True

@CommandRegistry.register("add", "MATH",
    "Adds two or more numbers together.",
    "add <number> <number> [number...]",
    ["add 5 3", "add $num1 $num2 10", "add result 5"])
def cmd_add(args):
    Command.process_math_command("add", args, should_print=True)
    return True

@CommandRegistry.register("subtract", "MATH",
    "Subtracts numbers from the first number.",
    "subtract <number> <number> [number...]",
    ["subtract 10 3", "subtract $num1 $num2", "subtract result 5"])
def cmd_subtract(args):
    Command.process_math_command("subtract", args, should_print=True)
    return True

@CommandRegistry.register("multiply", "MATH",
    "Multiplies two or more numbers together.",
    "multiply <number> <number> [number...]",
    ["multiply 4 5", "multiply $num1 $num2 2", "multiply result 3"])
def cmd_multiply(args):
    Command.process_math_command("multiply", args, should_print=True)
    return True

@CommandRegistry.register("divide", "MATH",
    "Divides the first number by subsequent numbers.",
    "divide <number> <number> [number...]",
    ["divide 20 4", "divide $num1 $num2", "divide result 2"])
def cmd_divide(args):
    Command.process_math_command("divide", args, should_print=True)
    return True

@CommandRegistry.register("exponent", "MATH",
    "Raises the first number to the power of subsequent numbers.",
    "exponent <number> <number> [number...]",
    ["exponent 2 3", "exponent $base $power", "exponent result 2"])
def cmd_exponent(args):
    Command.process_math_command("exponent", args, should_print=True)
    return True

@CommandRegistry.register("calc", "MATH",
    "Evaluates mathematical expressions with support for variables and commands in parentheses.",
    "calc <expression>",
    ["calc 2 + 3 * 4", "calc ($num1 + $num2) * 2", "calc (add 5 3) / 2"])
def cmd_calc(args):
    Command.process_math_command("calc", args, should_print=True)
    return True

@CommandRegistry.register("sqrt", "MATH",
    "Calculates the square root of a number.",
    "sqrt <number>",
    ["sqrt 16", "sqrt $number", "sqrt result"])
def cmd_sqrt(args):
    Command.process_math_command("sqrt", args, should_print=True)
    return True

@CommandRegistry.register("average", "MATH",
    "Calculates the average of two or more numbers.",
    "average <number> <number> [number...]",
    ["average 10 20 30", "average $num1 $num2 $num3", "average result 15"])
def cmd_average(args):
    Command.process_math_command("average", args, should_print=True)
    return True

@CommandRegistry.register("factorial", "MATH",
    "Calculates the factorial of a non-negative integer.",
    "factorial <number>",
    ["factorial 5", "factorial $num", "factorial result"])
def cmd_factorial(args):
    Command.process_math_command("factorial", args, should_print=True)
    return True

@CommandRegistry.register("create", "I/O",
    "Creates a new file (with extension) or directory (without extension) in the current directory.",
    "create <name>",
    ["create myfile.txt", "create mydirectory", "create data.json"])
def cmd_create(args):
    Command.process_io_command("create", args)
    return True

@CommandRegistry.register("delete", "I/O",
    "Deletes one or more files or directories. Accepts variables, paths, or names.",
    "delete <item> [item...]",
    ["delete file.txt", "delete $myfile", "delete /path/to/file", "delete dir1 dir2 file.txt"])
def cmd_delete(args):
    Command.process_io_command("delete", args)
    return True

@CommandRegistry.register("copy", "I/O",
    "Copies files/directories. Two modes:\n" +
    Text.INDENT + "1) Copy source to destination directory\n" +
    Text.INDENT + "2) Copy source to clipboard for later pasting",
    "copy <source> [destination]\ncopy <source>",
    ["copy file.txt /backup", "copy $myfile", 'copy "My File.txt" mydirectory'])
def cmd_copy(args):
    if not args:
        System.throw_error("SOURCE REQUIRED FOR 'copy'")
        return True
    
    # Parse arguments to handle quoted names
    parsed_args = ArgumentParser.parse_args_with_quotes(args)
    Command.process_io_command("copy", parsed_args)
    return True

@CommandRegistry.register("paste", "I/O",
    "Pastes the last copied file/directory from clipboard to current or specified directory.",
    "paste [destination]",
    ["paste", "paste mydirectory", 'paste "My Folder"'])
def cmd_paste(args):
    # Parse arguments to handle quoted names (even if empty)
    parsed_args = ArgumentParser.parse_args_with_quotes(args) if args else []
    Command.process_io_command("paste", parsed_args)
    return True

@CommandRegistry.register("edit", "I/O",
    "Opens a file in interactive curses-based editor (nano-style interface).",
    "edit <filename>",
    ["edit file.txt", "edit $myfile", 'edit "My File.txt"'])
def cmd_edit(args):
    global current_directory, last_command_result
    
    if not args:
        System.throw_error("FILENAME REQUIRED FOR 'edit'")
        return True

    parsed_args = ArgumentParser.parse_args_with_quotes(args)
    if not parsed_args:
        System.throw_error("FILENAME REQUIRED FOR 'edit'")
        return True
    
    filename = parsed_args[0]
    
    if filename.lower() == "result":
        if last_command_result and last_command_result[1] == DataType.FILE:
            full_path = VariableManager.resolve_path(last_command_result[0])
        else:
            System.throw_error("NO FILE RESULT AVAILABLE")
            return True
    elif filename.startswith('$') or filename.startswith('#'):
        var = VariableManager.get_variable(filename)
        if var and var.type == DataType.FILE:
            full_path = VariableManager.resolve_path(var.value)
        else:
            System.throw_error(f"VARIABLE '{filename}' NOT FOUND OR NOT A FILE")
            return True
    elif filename.startswith('/'):
        full_path = VariableManager.resolve_path(filename)
    else:
        full_path = os.path.join(current_directory, filename)
    
    display_name = os.path.basename(full_path)
    file_existed_before = os.path.exists(full_path)
    
    try:
        AsciiArt.stop_animation()
        time.sleep(0.1)
        System.clear_screen()
        
        editor = CursesEditor(full_path)
        Curses.wrapper(editor.run)
        
        new_path = editor.filepath
        final_name = os.path.basename(new_path)
        
        TerminalState.restore()
        
        last_command_result = (VariableManager.get_relative_path(new_path), DataType.FILE)
        
        if editor.was_deleted:
            if file_existed_before:
                System.show_result(f"FILE '{display_name}' DELETED")
            else:
                System.show_result(f"FILE CREATION CANCELLED - '{display_name}' NOT CREATED")
        elif editor.was_renamed and editor.was_saved:
            if file_existed_before:
                System.show_result(f"FILE RENAMED FROM '{display_name}' TO '{final_name}' AND SAVED")
            else:
                System.show_result(f"FILE '{final_name}' CREATED AND SAVED")
        elif editor.was_renamed and not editor.was_saved:
            System.show_result(f"FILE '{final_name}' WAS NOT CREATED")
        elif editor.was_saved:
            if file_existed_before:
                System.show_result(f"FILE '{final_name}' SAVED")
            else:
                System.show_result(f"FILE '{final_name}' CREATED")
        elif editor.modified:
            System.show_result(f"FILE '{final_name}' CHANGES NOT SAVED")
        else:
            System.show_result(f"FILE '{final_name}' CLOSED - NO CHANGES")
        
    except Exception as e:
        TerminalState.restore()
        System.throw_error(f"EDITOR ERROR: {str(e).upper()}")
    
    return True

@CommandRegistry.register("editor", "I/O",
    "Opens a file in the system's default text editor (notepad on Windows, nano/vim on Unix).",
    "editor <filename>",
    ["editor file.txt", "editor $myfile", "editor /path/to/file.txt", 'editor "My File.txt"'])
def cmd_editor(args):
    global current_directory, last_command_result
    
    if not args:
        System.throw_error("FILENAME REQUIRED FOR 'editor'")
        return True

    # Parse arguments to handle quoted filenames
    parsed_args = ArgumentParser.parse_args_with_quotes(args)
    if not parsed_args:
        System.throw_error("FILENAME REQUIRED FOR 'editor'")
        return True
    
    filename = parsed_args[0]
    
    full_path = PathResolver.resolve_file_argument(filename, last_command_result, current_directory)
    if full_path is None:
        System.throw_error(f"FILE '{filename}' NOT FOUND OR CANNOT BE ACCESSED")
        return True
    display_name = os.path.basename(full_path)

    try:
        # Ensure file exists
        if not os.path.exists(full_path):
            System.throw_error(f"FILE '{filename}' NOT FOUND")
            return True
        
        # Open file in system's text editor
        if os.name == 'nt':  # Windows
            os.system(f'notepad "{full_path}"')
        else:  # Unix-like (Linux, macOS)
            editors = ['nano', 'vim', 'vi']
            editor_found = False
            
            for editor in editors:
                if shutil.which(editor) is not None:
                    os.system(f'{editor} "{full_path}"')
                    editor_found = True
                    break
            
            if not editor_found:
                if shutil.which('xdg-open') is not None:
                    os.system(f'xdg-open "{full_path}"')
                elif shutil.which('open') is not None:
                    os.system(f'open "{full_path}"')
                else:
                    System.throw_error("NO TEXT EDITOR FOUND ON SYSTEM")
                    return True
        
        last_command_result = (VariableManager.get_relative_path(full_path), DataType.FILE)
        System.show_result(f"FILE '{display_name}' EDIT COMPLETE")
        
    except Exception as e:
        System.throw_error(f"COULD NOT OPEN EDITOR: {str(e).upper()}")
    
    return True

@CommandRegistry.register("read", "I/O",
    "Displays the contents of a file with line numbers.",
    "read <filename>",
    ["read file.txt", "read $myfile", "read /path/to/file.txt"])
def cmd_read(args):
    if not args:
        System.throw_error("FILENAME REQUIRED FOR 'read'")
        return True

    # Parse arguments to handle quoted filenames
    parsed_args = ArgumentParser.parse_args_with_quotes(args)
    if not parsed_args:
        System.throw_error("FILENAME REQUIRED FOR 'read'")
        return True
    
    filename = parsed_args[0]
    
    Command.process_io_command("read", [filename])
    return True

@CommandRegistry.register("dir", "I/O",
    "Shows directory tree or navigates to directories.\n" +
    Text.INDENT + "No arguments: Show directory tree\n" +
    Text.INDENT + "Navigation: 'home', '+' (first subdir), '-' (parent), or directory name",
    "dir [navigation]\ndir <directory>",
    ["dir", "dir home", "dir +", "dir -", "dir mydirectory", 'dir "My Folder"'])
def cmd_dir(args):
    # Parse arguments to handle quoted directory names
    parsed_args = ArgumentParser.parse_args_with_quotes(args) if args else []
    Command.process_io_command("dir", parsed_args)
    return True

@CommandRegistry.register("vars", "I/O",
    "Displays all current variables (both persistent $ and session # variables).",
    "vars",
    ["vars"])
def cmd_vars(args):
    Command.process_io_command("vars", args)
    return True

@CommandRegistry.register("forget", "I/O",
    "Deletes one or more variables from memory.",
    "forget <variable> [variable...]",
    ["forget $myvar", "forget #temp1 #temp2", "forget $file $dir"])
def cmd_forget(args):
    if not args:
        System.throw_error("VARIABLE NAME(S) REQUIRED FOR 'forget'")
        return True
    
    # Variables don't typically need quoted parsing, but we'll use it for consistency
    parsed_args = ArgumentParser.parse_args_with_quotes(args)
    Command.process_io_command("forget", parsed_args)
    return True

@CommandRegistry.register("date", "SYSTEM",
    "Returns the current date in MM-DD-YYYY format.",
    "date",
    ["date", "date -> $today"])
def cmd_date(args):
    global last_command_result
    result = datetime.datetime.now().strftime('%m-%d-%Y')
    last_command_result = (result, DataType.STRING)
    System.show_result(result)
    return True

@CommandRegistry.register("time", "SYSTEM",
    "Returns the current time in 12-hour format with AM/PM.",
    "time",
    ["time", "time -> $current_time"])
def cmd_time(args):
    global last_command_result
    result = datetime.datetime.now().strftime('%I:%M:%S %p')
    last_command_result = (result, DataType.STRING)
    System.show_result(result)
    return True

@CommandRegistry.register("print", "SYSTEM",
    "Prints text, variables, or command results to the screen.",
    "print <text/variables...>",
    ["print \"Hello World\"", "print $myvar", "print result", "print \"Value:\" $number"])
def cmd_print(args):
    global last_command_result
    # Reconstruct the full command line after "print"
    full_command = " ".join(args) if args else ""
    
    if not full_command.strip():
        System.print_instant("")
        return True
    
    parsed_args = []
    
    if '"' in full_command:
        parts = full_command.split('"')
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # Outside quotes - split on spaces
                words = [w.strip() for w in part.split() if w.strip()]
                parsed_args.extend(words)
            else:
                # Inside quotes - unescape the string and keep as single argument
                unescaped = part.replace('\\n', '\n').replace('\\\\', '\\').replace('\\"', '"')
                parsed_args.append(unescaped)
    else:
        parsed_args = [arg for arg in full_command.split() if arg.strip()]
    
    if not parsed_args:
        parsed_args = [full_command]
    
    output_parts = []
    for arg in parsed_args:
        if arg.lower() == "result":
            if last_command_result:
                output_parts.append(str(last_command_result[0]))
            else:
                System.throw_error("NO PREVIOUS COMMAND RESULT AVAILABLE")
                return True
        elif arg.startswith('$') or arg.startswith('#'):
            var = VariableManager.get_variable(arg)
            if var:
                # Special handling for FILE variables - read and print contents
                if var.type == DataType.FILE:
                    try:
                        file_path = VariableManager.resolve_path(var.value)
                        with open(file_path, 'r') as f:
                            content = f.read()
                        output_parts.append(content)
                    except Exception as e:
                        System.throw_error(f"ERROR READING FILE: {str(e).upper()}")
                        return True
                else:
                    output_parts.append(str(var.value))
            else:
                System.throw_error(f"VARIABLE '{arg}' NOT FOUND")
                return True
        else:
            output_parts.append(arg)
    
    if output_parts:
        # Store result FIRST
        last_command_result = ("\n".join(output_parts), DataType.STRING)
        
        # Print each part on its own line
        System.print_instant("")
        for part in output_parts:
            System.print_instant(part)
    
    return True

@CommandRegistry.register("rename", "I/O",
    "Renames a file or directory to a new name in the same location.",
    "rename <source> <new_name>",
    ["rename file.txt newfile.txt", "rename $myfile \"new name.txt\"", 'rename "old name.txt" "new name.txt"'])
def cmd_rename(args):
    if not args or len(args) < 2:
        System.throw_error("RENAME REQUIRES EXACTLY 2 ARGUMENTS: SOURCE AND NEW_NAME")
        return True
    
    # Parse arguments to handle quoted names
    parsed_args = ArgumentParser.parse_args_with_quotes(args)
    if len(parsed_args) != 2:
        System.throw_error("RENAME REQUIRES EXACTLY 2 ARGUMENTS: SOURCE AND NEW_NAME")
        return True
    
    Command.process_io_command("rename", parsed_args)
    return True

@CommandRegistry.register("move", "I/O",
    "Moves a file or directory to a different location (cut and paste in one operation).",
    "move <source> <destination_directory>",
    ["move file.txt /backup", "move $myfile mydirectory", 'move "My File.txt" "My Folder"'])
def cmd_move(args):
    if not args or len(args) < 2:
        System.throw_error("MOVE REQUIRES EXACTLY 2 ARGUMENTS: SOURCE AND DESTINATION")
        return True
    
    # Parse arguments to handle quoted names
    parsed_args = ArgumentParser.parse_args_with_quotes(args)
    if len(parsed_args) != 2:
        System.throw_error("MOVE REQUIRES EXACTLY 2 ARGUMENTS: SOURCE AND DESTINATION")
        return True
    
    Command.process_io_command("move", parsed_args)
    return True

@CommandRegistry.register("cut", "I/O",
    "Cuts (copies to clipboard and marks for removal) a file or directory for later pasting.",
    "cut <source>",
    ["cut file.txt", "cut $myfile", 'cut "My File.txt"'])
def cmd_cut(args):
    if not args:
        System.throw_error("CUT REQUIRES EXACTLY 1 ARGUMENT: SOURCE")
        return True
    
    # Parse arguments to handle quoted names
    parsed_args = ArgumentParser.parse_args_with_quotes(args)
    if len(parsed_args) != 1:
        System.throw_error("CUT REQUIRES EXACTLY 1 ARGUMENT: SOURCE")
        return True
    
    Command.process_io_command("cut", parsed_args)
    return True

@CommandRegistry.register("nav", "I/O",
    "Opens an interactive file navigator with arrow key navigation.\n" +
    Text.INDENT + "Arrow Keys: Navigate | Enter: Open/Change directory\n" +
    Text.INDENT + "Space: Expand/collapse directories | Esc: Exit",
    "nav",
    ["nav"])
def cmd_nav(args):
    global current_directory, last_command_result, current_user
    
    base_user_dir = VariableManager.get_user_root(current_user)
    
    try:
        AsciiArt.stop_animation()
        time.sleep(0.1)
        System.clear_screen()
        
        navigator = InteractiveNavigator(base_user_dir, current_directory)
        result = Curses.wrapper(navigator.run)
        
        if result is None:
            action, path = 'exit', None
        else:
            action, path = result
        
        TerminalState.restore()
        
        if action == 'edit' and path:
            display_name = os.path.basename(path)
            
            try:
                AsciiArt.stop_animation()
                time.sleep(0.1)
                System.clear_screen()
                
                editor = CursesEditor(path)
                Curses.wrapper(editor.run)
                
                new_path = editor.filepath
                final_name = os.path.basename(new_path)
                
                TerminalState.restore()
                
                last_command_result = (VariableManager.get_relative_path(new_path), DataType.FILE)
                
                if editor.was_saved:
                    System.show_result(f"FILE '{final_name}' EDIT COMPLETE")
                else:
                    System.show_result(f"EDIT CANCELLED")
                
            except Exception as e:
                TerminalState.restore()
                System.throw_error(f"EDITOR ERROR: {str(e).upper()}")
        
        elif action == 'exit':
            current_directory = navigator.current_dir
            relative_path = VariableManager.get_relative_path(current_directory)
            last_command_result = (relative_path, DataType.DIRECTORY)
            
            System.print_instant(f"\nCURRENT DIRECTORY: {relative_path}")
            System.show_result("NAVIGATOR CLOSED")
    
    except KeyboardInterrupt:
        TerminalState.restore()
        System.show_result("NAVIGATOR CANCELLED")
    except Exception as e:
        TerminalState.restore()
        System.throw_error(f"NAVIGATOR ERROR: {str(e).upper()}")
    
    return True

@CommandRegistry.register("browser", "WEB",
    "Opens an interactive terminal-based web browser powered by Google.\n" +
    Text.INDENT + "Search for content, navigate results with arrow keys, and visit pages.\n" +
    Text.INDENT + "Requires: pip install requests beautifulsoup4 html2text",
    "browser",
    ["browser"])
def cmd_browser(args):
    global last_command_result
    
    if not requests or not BeautifulSoup or not html2text:
        System.throw_error("WEB BROWSER DEPENDENCIES NOT INSTALLED\n" +
                          "INSTALL WITH: pip install requests beautifulsoup4 html2text")
        return True
    
    try:
        AsciiArt.stop_animation()
        time.sleep(0.1)
        System.clear_screen()
        
        browser = WebBrowser()
        Curses.wrapper(browser.run)
        
        TerminalState.restore()
        
        last_command_result = ("NULL", DataType.NULL)
        
        System.show_result("BROWSER CLOSED")
    
    except KeyboardInterrupt:
        TerminalState.restore()
        System.show_result("BROWSER CANCELLED")
    except Exception as e:
        TerminalState.restore()
        System.throw_error(f"BROWSER ERROR: {str(e).upper()}")
    
    return True

def main():
    global current_directory, last_command_result, session_variables, persistent_variables, current_user
    init()

    SplashScreen.show()
    
    # User data lives in platform-specific location (e.g., %APPDATA%/Kairo on Windows)
    user_data_dir = get_user_data_path()
    users_file = os.path.join(user_data_dir, "users.dat")
    
    # On first run, copy the template users.dat from the app bundle
    if not os.path.exists(users_file):
        template_file = os.path.join(get_app_path(), "data", "users.dat")
        if os.path.exists(template_file):
            shutil.copy(template_file, users_file)
        else:
            # Create a default users file with guest account
            default_users = {"users": [{"username": "guest", "password": "guest"}]}
            with open(users_file, 'w') as f:
                json.dump(default_users, f, indent=4)
    
    users = UserManager.load_users(users_file)
    
    while True:  # Loop to return to menu after create/remove
        System.clear_screen()
        user = None
        
        # Use curses login screen
        try:
            login_screen = CursesLoginScreen(users)
            action, data = Curses.wrapper(login_screen.run)
            
            if action == "exit":
                System.clear_screen()
                sys.exit(0)
            
            elif action == "login":
                current_user = data
                current_directory = System.create_user_directory(current_user)
                VariableManager.load_persistent_variables(current_user)
                System.clear_screen()
                System.welcome(current_user)
                break  # Exit the login loop, enter main command loop
            
            elif action == "create":
                username, password = data
                users.append(User(username, password))
                UserManager.save_users(users, users_file)
                System.create_user_directory(username)
                
                # Show success message for 2 seconds
                System.clear_screen()
                print(f"\n{Fore.GREEN}✓ User '{username}' created successfully!{Style.RESET_ALL}")
                time.sleep(2)
                
                # Reload users and continue loop (return to menu)
                users = UserManager.load_users(users_file)
                continue
            
            elif action == "remove":
                username = data
                users = [u for u in users if u.username.lower() != username.lower()]
                UserManager.save_users(users, users_file)
                
                # Show success message for 2 seconds
                System.clear_screen()
                print(f"\n{Fore.GREEN}✓ User '{username}' removed successfully!{Style.RESET_ALL}")
                time.sleep(2)
                
                # Continue loop (return to menu)
                continue
        
        except KeyboardInterrupt:
            System.clear_screen()
            sys.exit(0)
        except Exception as e:
            System.clear_screen()
            print(f"Login error: {e}")
            sys.exit(1)
        
    session_variables = {}
    last_command_result = None
    
    # Track terminal size for resize detection
    prev_terminal_size = shutil.get_terminal_size()
    
    while True:
        try:
            # Check for terminal resize
            current_terminal_size = shutil.get_terminal_size()
            if current_terminal_size != prev_terminal_size:
                prev_terminal_size = current_terminal_size
                AsciiArt.handle_terminal_resize()
            
            command = System.colored_input("\n_> ")
            if not Command.process_command(command):
                break
        except KeyboardInterrupt:
            System.handle_shutdown()
        except Exception as e:
            System.throw_error(f"UNEXPECTED ERROR: {str(e).upper()}")
                     
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        System.handle_shutdown()