# System Architecture

Detailed technical documentation of Kairo's architecture, design patterns, and module organization.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │SplashScreen │ │LoginScreen  │ │CursesEditor │ │WebBrowser   ││
│  │(Animation)  │ │(Auth TUI)   │ │(nano-like)  │ │(HTML render)││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
├─────────────────────────────────────────────────────────────────┤
│                       COMMAND LAYER                              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  40+ Commands: file ops, math, search, variables, etc.   │  │
│  │  ArgumentParser → Command Execution → Result Display     │  │
│  └───────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                        CORE LAYER                                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │   System    │ │   Sound     │ │TerminalState│ │  AsciiArt   ││
│  │ (I/O, clear)│ │ (threaded)  │ │  (buffer)   │ │ (animation) ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
├─────────────────────────────────────────────────────────────────┤
│                      MANAGER LAYER                               │
│  ┌───────────────────────────┐ ┌───────────────────────────────┐│
│  │      UserManager          │ │      VariableManager          ││
│  │ (auth, persistence)       │ │ (session/$persistent vars)    ││
│  └───────────────────────────┘ └───────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│                       MODEL LAYER                                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │    User     │ │  Variable   │ │  DataType   │ │   Message   ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
├─────────────────────────────────────────────────────────────────┤
│                      CONFIG LAYER                                │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  get_app_path() · get_user_data_path() · Platform detect  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Module Organization

### Package Structure

```
kairo/
├── __init__.py           # Package metadata, version
├── config.py             # Cross-platform path utilities
├── state.py              # Global state (current_user, variables)
├── main.py               # Application entry point
│
├── models/               # Data classes (pure, no dependencies)
│   ├── user.py           # User(username, password)
│   ├── variable.py       # Variable, DataType enum
│   └── text.py           # Message constants, MenuOption
│
├── core/                 # System utilities
│   ├── sound.py          # Threaded audio playback
│   ├── system.py         # Terminal I/O, loading bars
│   ├── terminal.py       # TerminalState, AsciiArt
│   └── curses_wrapper.py # Curses initialization helper
│
├── managers/             # Business logic
│   ├── user_manager.py   # Load/save users, authentication
│   └── variable_manager.py # Session/persistent variable handling
│
└── utils/                # Helper utilities
    ├── input.py          # Cross-platform keyboard input
    └── formatting.py     # NumberFormatter, ArgumentParser
```

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Modular Package** | Separation of concerns, testable units, professional structure |
| **State Module** | Centralized mutable state prevents circular imports |
| **Cross-Platform Paths** | `get_user_data_path()` uses OS-appropriate locations |
| **Threaded Audio** | Non-blocking sound playback for smooth UX |
| **Curses TUI** | Rich terminal UI with color, animation, input handling |
| **Legacy Compatibility** | `app.py` imports from package, maintains backward compat |

---

## Data Flow

### User Authentication Flow

```
┌──────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────┐
│  Splash  │ ──▶ │ LoginScreen  │ ──▶ │ UserManager │ ──▶ │ Welcome  │
│  Screen  │     │ (curses TUI) │     │ (validate)  │     │ Message  │
└──────────┘     └──────────────┘     └─────────────┘     └──────────┘
                        │                    │
                        ▼                    ▼
                 ┌────────────┐       ┌────────────┐
                 │ users.dat  │       │ Create Dir │
                 │ (JSON)     │       │ (per-user) │
                 └────────────┘       └────────────┘
```

### Command Execution Flow

```
User Input ──▶ ArgumentParser ──▶ Command Lookup ──▶ Execute
                    │                                   │
                    ▼                                   ▼
              Quote handling              VariableManager.resolve()
              Variable expansion          System.show_result()
```

---

## Cross-Platform Support

### Path Handling

| Platform | App Resources | User Data |
|----------|--------------|-----------|
| **Windows** | `./` or PyInstaller `_MEIPASS` | `%APPDATA%\Kairo` |
| **macOS** | `./` or PyInstaller `_MEIPASS` | `~/Library/Application Support/Kairo` |
| **Linux** | `./` or PyInstaller `_MEIPASS` | `~/.local/share/Kairo` |

### Terminal Input

| Platform | Module | Method |
|----------|--------|--------|
| **Windows** | `msvcrt` | `getch()` for raw input |
| **Unix** | `termios` + `tty` | Raw mode terminal |
| **Both** | `curses` | TUI screens |

---

## Performance Considerations

- **Threaded Sound**: Audio plays in background thread, UI never blocks
- **Terminal State Buffer**: Records output for restoration after curses screens
- **Lazy Imports**: Optional dependencies (web browser) loaded only when needed
- **Animation Threading**: Status bar runs in daemon thread

---

## Security

- **User Isolation**: Each user has separate directory and variables
- **Password Storage**: Stored in JSON (note: not hashed - educational project)
- **File Sandboxing**: Users can only access their own directory tree
