# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

# Get resource directories
sounds_dir = os.path.join(os.getcwd(), 'sounds')
data_dir = os.path.join(os.getcwd(), 'data')

# Bundle resources
# sounds/ - bundled with app (used by get_app_path())
# data/ - template users.dat copied to AppData on first run
datas = []
if os.path.exists(sounds_dir):
    datas.append((sounds_dir, 'sounds'))
if os.path.exists(data_dir):
    datas.append((data_dir, 'data'))

# All hidden imports
hiddenimports = [
    # Core
    '_curses', 'curses', 'curses.panel', 'curses.textpad',
    'colorama', 'playsound',
    # Audio
    'mutagen', 'mutagen.mp3', 'mutagen.mp4', 'mutagen.id3',
    # Web browser
    'requests', 'requests.adapters', 'requests.cookies',
    'requests.exceptions', 'urllib3', 'urllib3.contrib',
    'urllib3.util', 'urllib3.util.retry', 'certifi',
    'charset_normalizer', 'idna', 'bs4', 'bs4.builder',
    'bs4.builder._htmlparser', 'bs4.builder._lxml', 'html2text',
    'soupsieve', 'html', 'html.parser',
    # System
    'json', 'datetime', 'time', 'os', 'sys', 'shutil',
    'threading', 'ctypes', 're', 'random', 'math', 'enum', 'typing',
]

if sys.platform.startswith('win'):
    hiddenimports.extend(['windows-curses', 'msvcrt'])
else:
    hiddenimports.extend(['tty', 'termios', 'select'])

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas', 'scipy', 'PIL', 'PyQt5', 'wx'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='kairo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
