"""Input utilities for Kairo."""
import sys
import os

# Platform-specific imports
if os.name == 'nt':
    import msvcrt
else:
    import tty
    import termios


class Input:
    """Handles keyboard input including hidden password input."""
    
    @staticmethod
    def get_key():
        """Get a single keypress from the user."""
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
        """Get password input with asterisk masking."""
        # Import here to avoid circular import
        from kairo.core.system import System
        
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
