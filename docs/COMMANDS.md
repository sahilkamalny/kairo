# Command Reference

Complete documentation of all Kairo shell commands with usage examples.

---

## Navigation Commands

### `cd` - Change Directory
```bash
cd <directory>     # Navigate to directory
cd ..              # Go up one level
cd /               # Go to user root
```

### `ls` - List Directory
```bash
ls                 # List current directory
ls <directory>     # List specific directory
```

### `pwd` - Print Working Directory
```bash
pwd                # Show current path
```

### `tree` - Directory Tree
```bash
tree               # Show directory structure
tree <directory>   # Show specific directory tree
```

---

## File Operations

### `touch` - Create File
```bash
touch <filename>   # Create empty file
```

### `mkdir` - Create Directory
```bash
mkdir <dirname>    # Create new directory
```

### `rm` - Remove
```bash
rm <file>          # Delete file
rm <directory>     # Delete directory (recursive)
```

### `copy` - Copy to Clipboard
```bash
copy <path>        # Copy file/directory to clipboard
```

### `cut` - Cut to Clipboard
```bash
cut <path>         # Cut file/directory to clipboard
```

### `paste` - Paste from Clipboard
```bash
paste              # Paste in current directory
paste <newname>    # Paste with new name
```

### `move` - Move File/Directory
```bash
move <source> <destination>
```

### `rename` - Rename
```bash
rename <oldname> <newname>
```

---

## File Viewing

### `cat` - Display File Contents
```bash
cat <filename>     # Print entire file
```

### `head` - Show Beginning
```bash
head <filename>           # First 10 lines
head <filename> <lines>   # First N lines
```

### `tail` - Show End
```bash
tail <filename>           # Last 10 lines
tail <filename> <lines>   # Last N lines
```

### `wc` - Word Count
```bash
wc <filename>      # Lines, words, characters
```

---

## Text Editor

### `edit` - Open Editor
```bash
edit <filename>    # Open file in curses editor
```

**Editor Controls:**
| Key | Action |
|-----|--------|
| `Ctrl+S` | Save file |
| `Ctrl+Q` | Quit (prompts to save) |
| `Arrow keys` | Navigate |
| `Backspace` | Delete character |

---

## Search Commands

### `find` - Find Files
```bash
find <pattern>     # Search for files by name
```

### `grep` - Search in Files
```bash
grep <pattern> <file>   # Search content in file
```

---

## Variable System

### Variable Types
- `$variable` - Persistent (saved to disk)
- `#variable` - Session-only (cleared on exit)

### `set` - Set Variable
```bash
set $name "John"       # Persistent string
set #count 42          # Session number
```

### `get` - Get Variable
```bash
get $name              # Display variable value
```

### `del` - Delete Variable
```bash
del $name              # Remove variable
```

### `vars` - List Variables
```bash
vars                   # Show all variables
```

---

## Math Commands

### `calc` - Calculate Expression
```bash
calc 5 + 3 * 2         # Returns 11.0
calc (10 - 4) / 2      # Returns 3.0
```

### Basic Operations
```bash
add 5 3                # 8.0
sub 10 4               # 6.0
mul 3 7                # 21.0
div 20 4               # 5.0
```

### Advanced Math
```bash
pow 2 8                # 256.0 (power)
sqrt 16                # 4.0 (square root)
mod 17 5               # 2.0 (modulo)
abs -42                # 42.0 (absolute)
```

---

## String Commands

### `len` - String Length
```bash
len "hello world"      # 11
```

### `upper` / `lower` - Case Conversion
```bash
upper "hello"          # HELLO
lower "WORLD"          # world
```

### `concat` - Concatenate
```bash
concat "Hello" " " "World"  # Hello World
```

---

## System Commands

### `clear` - Clear Screen
```bash
clear                  # Clear terminal
```

### `help` - Show Help
```bash
help                   # List all commands
help <command>         # Command-specific help
```

### `exit` - Exit Shell
```bash
exit                   # Logout and exit
```

### `reboot` - Restart Shell
```bash
reboot                 # Restart with login screen
```

---

## Web Browser

### `browser` - Open Web Browser
```bash
browser                # Launch browser interface
browser <url>          # Open specific URL
```

**Browser Controls:**
| Key | Action |
|-----|--------|
| `g` | Go to URL |
| `b` | Back |
| `r` | Reload |
| `q` | Quit browser |
| `1-9` | Follow link by number |

---

## Result Variables

Commands store results in the special `?` variable:
```bash
calc 5 + 3
get ?                  # Returns 8.0

len "hello"
get ?                  # Returns 5
```

---

## Examples

### File Management Workflow
```bash
mkdir projects
cd projects
touch readme.txt
edit readme.txt
cat readme.txt
```

### Variable Workflow
```bash
set $counter 0
calc $counter + 1
set $counter ?
get $counter           # 1.0
```

### Search Workflow
```bash
find *.txt             # Find all .txt files
grep "TODO" notes.txt  # Find TODO in file
```
