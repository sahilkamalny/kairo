"""Text formatting constants and system messages for Kairo."""
from enum import Enum


class Text:
    """Text formatting constants."""
    INDENT = 3 * " "


class Message:
    """System message templates with cyberpunk aesthetics."""
    MENU = "█▓▒░ SYSTEM MENU ░▒▓█"
    BOOT = "█▓▒░ BOOTING SYSTEM ░▒▓█"
    SHUTDOWN = "\n█▓▒░ SYSTEM SHUTDOWN ░▒▓█"
    MALFUNCTION = "\n░▒▓█ SYSTEM MALFUNCTION █▓▒░"
    GLITCH = "░▒▓█ ┊⧗͡͠҉͘͢͏̀҉G͏̴L҉̷͘͞͏̀͞͡I̷͡҉̴T̵C͟H͜ █▓▒░"
    ERROR = (
        "⊠⊡⧗͡҉⧛͜⚠͠ ⬢ ERROR C͏͝O̷͏D͘E: 0xA͠C4D32 ⬢ ⚠⧛⧗⊡⊠\n"
        "U̴͢S̸̛E̶͝R̷͝ ̷͘D̵͟O̸͡E̸̛S̶͟ ̵͡N̶̸O̵͜T̵͡ ̴͜Ę̵X̵͢I̵̡S̶͝T̷͡\n"
        "▒▓▒▒͠▓▒▒░▒▓ ▒▒░▓▒░░▓▒▒▒▒▒▓▒▒▒▒▒▒▒▒▒▓▒▒▒▒▒▒▒▒▒▓▒▒▒▒ "
        "▒▒▒▒▓▒▒▒▒▒▒▒▒▒▓▒▒▒▒▒▒▒▒▒▓▒▒▒▒▒▒▒▒▒▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░"
    )


class MenuOption(Enum):
    """Menu option enumeration for login screen."""
    EXISTING = 0
    NEW = 1
    REMOVE = 2
