# Feature Deep Dive

Comprehensive documentation of Kairo's core features and implementation details.

---

## 🎨 Cyberpunk Interface

### Animated Splash Screen
The splash screen creates an immersive first impression with:

- **Matrix Rain Effect**: Vertical streams of hex characters with gradient coloring
- **Side Streams**: Horizontal animated streams from screen edges
- **Glowing Title**: "KAIRO" with breathing animation effect
- **Responsive Scaling**: Adapts to any terminal size

**Technical Implementation:**
- Direct ANSI escape sequences for cursor positioning
- Frame-based animation loop at ~20 FPS
- Thread-safe terminal resizing detection
- Column-by-column fade-out transition

### Curses Login Screen
A full TUI authentication interface:

| Feature | Description |
|---------|-------------|
| ASCII Title | Block-style "KAIRO" header |
| Menu Navigation | Arrow keys + Enter selection |
| Input Fields | Username/password with cursor |
| Visual Feedback | Error messages, field highlighting |

---

## 📁 File Management System

### User Sandboxing
Each user has an isolated file system:

```
%APPDATA%/Kairo/           # Windows
~/Library/Application Support/Kairo/  # macOS
~/.local/share/Kairo/      # Linux
└── users/
    └── <username>/
        └── (user files here)
```

### Clipboard System
Cross-command clipboard for file operations:

```bash
copy myfile.txt      # Stores path + "copy" mode
paste                # Duplicates file

cut myfile.txt       # Stores path + "cut" mode  
paste                # Moves file (removes original)
```

### Directory Navigation
- Relative paths: `cd subfolder`
- Parent navigation: `cd ..`
- Absolute from root: `cd /path/to/dir`
- Path resolution handles edge cases

---

## ✏️ Text Editor

A nano-inspired curses editor with:

| Feature | Implementation |
|---------|----------------|
| Line numbering | Left gutter with line count |
| Cursor movement | Arrow keys, Home/End |
| Text editing | Insert, backspace, newlines |
| Scrolling | Viewport follows cursor |
| Status bar | Filename, modified indicator |

**Keyboard Shortcuts:**
- `Ctrl+S` - Save file
- `Ctrl+Q` - Quit (with save prompt)
- `Ctrl+G` - Go to line

---

## 🧮 Variable System

### Two Variable Types

| Prefix | Type | Persistence | Use Case |
|--------|------|-------------|----------|
| `$` | Persistent | Saved to disk | User preferences, counters |
| `#` | Session | Memory only | Temporary calculations |

### Storage Format
```json
// variables/<username>.var
{
  "$counter": {
    "value": 42,
    "type": "number"
  },
  "$name": {
    "value": "John",
    "type": "string"
  }
}
```

### Special `?` Variable
Automatically stores the last command result:
```bash
calc 10 * 5
get ?              # Returns 50.0
len "hello"
get ?              # Returns 5
```

---

## 🌐 Web Browser

Terminal-based web browsing with:

- **HTML Rendering**: BeautifulSoup parsing → plain text
- **Link Detection**: Numbered links for keyboard navigation
- **History**: Back button support
- **Bookmarks**: Save frequently visited sites

**Architecture:**
```
URL Input → requests.get() → BeautifulSoup → html2text → Display
                                   ↓
                            Extract links
                                   ↓
                         Number + display
```

---

## 🔊 Audio System

### Threaded Playback
Sound effects play without blocking:

```python
# In sound.py
def play(sound: str):
    thread = threading.Thread(target=_play_file, args=(path,))
    thread.start()
```

### Sound Events
| Event | Sound |
|-------|-------|
| Boot | `boot.mp3` |
| Shutdown | `shutdown.mp3` |
| Command result | `enter.mp3` |
| Error | `error.mp3` |
| Glitch effect | `glitch.mp3` |

### Synchronized Loading Bar
Loading bars sync with sound duration:
```
[████████████████████████████████████████] 100%
```

---

## 🔐 User Management

### Authentication Flow
1. Load `users.dat` JSON file
2. Display curses login screen
3. Validate username/password
4. Create user directory if new
5. Load persistent variables
6. Show welcome message

### User Operations
| Action | Process |
|--------|---------|
| Create | Add to JSON, create directory |
| Remove | Delete from JSON (keeps files) |
| Login | Validate, load state |
| Logout | Save variables, clear state |

---

## 🖥️ Terminal State Management

### Output Recording
All output is buffered for restoration:

```python
class TerminalState:
    _output_buffer = []
    _recording = False
    
    def write(text, color, end):
        # Write to stdout
        # Also append to buffer if recording
```

### Screen Restoration
After curses screens (editor, browser), the shell reconstructs its previous state by replaying the output buffer.

---

## ⚡ Performance Features

| Feature | Technique |
|---------|-----------|
| Non-blocking audio | Daemon threads |
| Responsive UI | Terminal size detection |
| Fast startup | Lazy dependency loading |
| Memory efficient | Stream-based file reading |
