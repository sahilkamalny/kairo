"""Curses wrapper for Kairo."""
import curses


class Curses:
    """Helper class for curses screen management."""
    
    @staticmethod
    def wrapper(func):
        """Wrapper that resets terminal and returns the function's return value."""
        try:
            stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            stdscr.keypad(True)
            curses.start_color()
            curses.use_default_colors()
            
            return func(stdscr)
        finally:
            stdscr.keypad(False)
            curses.echo()
            curses.nocbreak()
            curses.endwin()
