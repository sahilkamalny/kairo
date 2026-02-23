<div align="center">

# KAIRO

**Retro-futuristic interactive OS shell — file management, system utilities, a built-in text editor, and an immersive curses-based TUI.**

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org/)
[![Curses](https://img.shields.io/badge/Curses-TUI-4B8BBE?style=flat-square&logo=gnu-bash&logoColor=white)](https://docs.python.org/3/library/curses.html)
[![Cross-Platform](https://img.shields.io/badge/Cross_Platform-Win_|_Mac_|_Linux-00D9FF?style=flat-square&logo=windows-terminal&logoColor=white)](https://github.com/sahilkamalny/Kairo)
[![PyInstaller](https://img.shields.io/badge/PyInstaller-Portable-FF6B6B?style=flat-square&logo=pypi&logoColor=white)](https://pyinstaller.org/)

[Portfolio](https://sahilkamal.dev) · [LinkedIn](https://linkedin.com/in/sahilkamalny) · [Contact](mailto:sahilkamal.dev@gmail.com)

[Architecture](docs/ARCHITECTURE.md) · [Commands](docs/COMMANDS.md) · [Features](docs/FEATURES.md)

</div>

---

## Overview

KAIRO is a cross-platform terminal application written in Python that emulates an interactive OS shell with a retro-futuristic aesthetic. It provides 40+ commands spanning file navigation, text editing, recursive descent parsing, expression evaluation, persistent variables, and terminal web browsing — all rendered through a curses-based TUI with animated splash screens, a real-time status bar, and color-coded output. Multi-user authentication with per-user file directories is included out of the box. Portable Windows executables can be produced via PyInstaller.

---

## Features

**Interface**
- Animated splash screen with matrix-style rain effect
- Curses-based TUI with real-time clock and color-coded status bar
- Cross-platform ANSI styling via colorama; threaded audio for non-blocking sound effects

**File Management**
- Navigation: `cd`, `ls`, `pwd`, `tree`
- File operations: `touch`, `mkdir`, `rm`, `copy`, `move`, `rename`
- Clipboard system: `copy`, `cut`, `paste` with cross-session persistence
- File viewing: `cat`, `head`, `tail`, `wc`

**Text Editor**
- Full-featured nano-style editor built on curses
- Keyboard shortcuts for save, discard, and cursor navigation

**Math & Variables**
- Expression evaluation via `calc`
- Persistent (`$var`) and session-scoped (`#var`) variable system
- String manipulation, `find`, and `grep` utilities

**Web Browser**
- Terminal web browsing via `browser` command
- HTML-to-text rendering with link navigation and bookmark support

**Multi-User System**
- Login / password authentication with per-user file directories and variable scopes
- User creation and removal from the application menu

---

## Project Structure

```
kairo/
├── app.py                 # Application entry point
├── kairo/                 # Core package
│   ├── config.py          # Path utilities
│   ├── state.py           # Global state management
│   ├── models/            # Data classes
│   ├── core/              # System-level utilities
│   ├── managers/          # Business logic layer
│   └── utils/             # Shared helpers
├── sounds/                # Audio assets
├── data/                  # User data templates
└── docs/
    ├── ARCHITECTURE.md
    ├── COMMANDS.md
    └── FEATURES.md
```

---

## Getting Started

**Prerequisites:** Python 3.8+, pip

```bash
# Clone and install
git clone https://github.com/sahilkamalny/Kairo.git
cd Kairo
pip install colorama playsound windows-curses

# Optional: web browser support
pip install requests beautifulsoup4 html2text

# Run
python app.py
```

**Build a portable Windows executable**

```batch
build.bat
# Output: dist/Kairo.exe
```

---

## Tech Stack

| Layer | Technologies |
|---|---|
| Core | Python 3.8+, standard library |
| TUI | curses (windows-curses on Windows) |
| Audio | playsound, mutagen |
| Styling | colorama (cross-platform ANSI) |
| Web | requests, BeautifulSoup4, html2text |
| Build | PyInstaller |

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

## Contact

**Sahil Kamal** — Full-Stack Developer

[sahilkamal.dev](https://sahilkamal.dev) · [linkedin.com/in/sahilkamalny](https://linkedin.com/in/sahilkamalny) · [sahilkamal.dev@gmail.com](mailto:sahilkamal.dev@gmail.com)

---

<div align="center">

[Architecture](docs/ARCHITECTURE.md) · [Commands](docs/COMMANDS.md) · [Features](docs/FEATURES.md)

*© 2026 Sahil Kamal*

</div>
