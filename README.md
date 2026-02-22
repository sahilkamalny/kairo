<div align="center">

# 📟 KAIRO

### Retro-Futuristic Interactive OS Shell

*Functional programming, file management, system utilities, and an immersive retro-futuristic TUI experience*

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Curses](https://img.shields.io/badge/Curses-TUI-4B8BBE?style=for-the-badge&logo=gnu-bash&logoColor=white)](https://docs.python.org/3/library/curses.html)
[![Cross-Platform](https://img.shields.io/badge/Cross_Platform-Win_|_Mac_|_Linux-00D9FF?style=for-the-badge&logo=windows-terminal&logoColor=white)](https://github.com/sahilkamalny/Kairo)
[![PyInstaller](https://img.shields.io/badge/PyInstaller-Portable-FF6B6B?style=for-the-badge&logo=pypi&logoColor=white)](https://pyinstaller.org/)

---

**[💼 LinkedIn](https://linkedin.com/in/sahilkamalny)** · **[🌍 Portfolio](https://sahilkamal.dev)** · **[📧 Contact](mailto:sahilkamal.dev@gmail.com)**

**[📖 Architecture](docs/ARCHITECTURE.md)** · **[⌨️ Commands](docs/COMMANDS.md)** · **[✨ Features](docs/FEATURES.md)**

</div>

---

## ✨ Features

### 🎨 Immersive Retro-Futuristic Interface
- Animated splash screen with matrix-style rain effects
- Glassmorphic login screen with curses-based TUI
- Real-time animated status bar with clock
- Color-coded outputs and error messages

### 📁 Complete File Management
- **Navigation**: `cd`, `ls`, `pwd`, `tree` commands
- **File Operations**: `touch`, `mkdir`, `rm`, `copy`, `move`, `rename`
- **Clipboard System**: `copy`, `cut`, `paste` with cross-session support
- **File Viewing**: `cat`, `head`, `tail`, `wc` (word count)

### ✏️ Built-in Text Editor
- Full-featured nano-like editor using curses
- Syntax-aware editing with keyboard shortcuts
- Save, discard, and navigation controls

### 🧮 Math & Variables
- Expression evaluation with `calc`
- Variable system with `$persistent` and `#session` variables
- String manipulation commands
- File search with `find` and `grep`

### 🌐 Built-in Web Browser
- Terminal-based web browsing with `browser` command
- HTML-to-text rendering with link navigation
- Bookmark support

### 👤 Multi-User System
- User authentication with login/password
- Per-user file directories and variables
- User creation and removal from menu

---

## 🛠️ Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation
```bash
# Clone the repository
git clone https://github.com/sahilkamalny/Kairo.git
cd Kairo

# Install dependencies
pip install colorama playsound windows-curses

# Optional: Web browser support
pip install requests beautifulsoup4 html2text

# Run
python app.py
```

### Build Portable Executable (Windows)
```batch
build.bat
# Find executable in dist/Kairo.exe
```

---

## 📁 Project Structure

```
kairo/
├── app.py                    # Main application
├── kairo/                    # Modular package
│   ├── config.py             # Path utilities
│   ├── state.py              # Global state
│   ├── models/               # Data classes
│   ├── core/                 # System utilities
│   ├── managers/             # Business logic
│   └── utils/                # Helpers
├── sounds/                   # Audio assets
├── data/                     # User data templates
└── docs/                     # Documentation
    ├── ARCHITECTURE.md
    ├── COMMANDS.md
    └── FEATURES.md
```

---

## 📊 Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Core** | Python 3.8+, Standard Library |
| **TUI** | Curses (windows-curses on Windows) |
| **Audio** | playsound, mutagen |
| **Styling** | colorama (cross-platform ANSI) |
| **Web** | requests, BeautifulSoup, html2text |
| **Build** | PyInstaller |

---

## 🔧 Technical Highlights

- **6,500+ lines** of Python with modular architecture
- **40+ commands** for file ops, math, search, and more
- **Cross-platform** support (Windows, macOS, Linux)
- **Threaded audio** for non-blocking sound effects
- **Curses-based** TUI with responsive terminal detection
- **Portable builds** via PyInstaller bundling

---

## 📬 Contact

**Sahil Kamal** - Full-Stack Developer

- 🌐 Portfolio: [sahilkamal.dev](https://sahilkamal.dev)
- 💼 LinkedIn: [linkedin.com/in/sahilkamalny](https://linkedin.com/in/sahilkamalny)
- 📧 Email: [sahilkamal.dev@gmail.com](mailto:sahilkamal.dev@gmail.com)
- 🐙 GitHub: [github.com/sahilkamalny](https://github.com/sahilkamalny)

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

<div align="center">

### 📖 Additional Documentation

**[Architecture →](docs/ARCHITECTURE.md)** · **[Commands →](docs/COMMANDS.md)** · **[Features →](docs/FEATURES.md)**

---

**© 2026 Sahil Kamal**

</div>
