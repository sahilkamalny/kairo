@echo off
echo.
echo ========================================
echo Building Kairo Executable
echo ========================================
echo.

REM Use the directory where this script is located (no hardcoded path!)
cd /d "%~dp0"
echo Working directory: %CD%
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist kairo.spec del /q kairo.spec
echo ...Done
echo.

REM Create spec file with all dependencies
echo Creating spec file...
(
echo # -*- mode: python ; coding: utf-8 -*-
echo import sys
echo import os
echo.
echo block_cipher = None
echo.
echo # Get resource directories
echo sounds_dir = os.path.join^(os.getcwd^(^), 'sounds'^)
echo data_dir = os.path.join^(os.getcwd^(^), 'data'^)
echo kairo_dir = os.path.join^(os.getcwd^(^), 'kairo'^)
echo.
echo # Bundle resources
echo # sounds/ - bundled with app ^(used by get_app_path^(^)^)
echo # data/ - template users.dat copied to AppData on first run
echo # kairo/ - modular package components
echo datas = []
echo if os.path.exists^(sounds_dir^):
echo     datas.append^(^(sounds_dir, 'sounds'^)^)
echo if os.path.exists^(data_dir^):
echo     datas.append^(^(data_dir, 'data'^)^)
echo if os.path.exists^(kairo_dir^):
echo     datas.append^(^(kairo_dir, 'kairo'^)^)
echo.
echo # All hidden imports
echo hiddenimports = [
echo     # Core
echo     '_curses', 'curses', 'curses.panel', 'curses.textpad',
echo     'colorama', 'playsound',
echo     # Audio
echo     'mutagen', 'mutagen.mp3', 'mutagen.mp4', 'mutagen.id3',
echo     # Web browser
echo     'requests', 'requests.adapters', 'requests.cookies',
echo     'requests.exceptions', 'urllib3', 'urllib3.contrib',
echo     'urllib3.util', 'urllib3.util.retry', 'certifi',
echo     'charset_normalizer', 'idna', 'bs4', 'bs4.builder',
echo     'bs4.builder._htmlparser', 'bs4.builder._lxml', 'html2text',
echo     'soupsieve', 'html', 'html.parser',
echo     # System
echo     'json', 'datetime', 'time', 'os', 'sys', 'shutil',
echo     'threading', 'ctypes', 're', 'random', 'math', 'enum', 'typing',
echo ]
echo.
echo if sys.platform.startswith^('win'^):
echo     hiddenimports.extend^(['windows-curses', 'msvcrt']^)
echo else:
echo     hiddenimports.extend^(['tty', 'termios', 'select']^)
echo.
echo a = Analysis^(
echo     ['app.py'],
echo     pathex=[],
echo     binaries=[],
echo     datas=datas,
echo     hiddenimports=hiddenimports,
echo     hookspath=[],
echo     hooksconfig={},
echo     runtime_hooks=[],
echo     excludes=['tkinter', 'matplotlib', 'numpy', 'pandas', 'scipy', 'PIL', 'PyQt5', 'wx'],
echo     win_no_prefer_redirects=False,
echo     win_private_assemblies=False,
echo     cipher=block_cipher,
echo     noarchive=False,
echo     optimize=0,
echo ^)
echo.
echo pyz = PYZ^(a.pure, a.zipped_data, cipher=block_cipher^)
echo.
echo exe = EXE^(
echo     pyz,
echo     a.scripts,
echo     a.binaries,
echo     a.zipfiles,
echo     a.datas,
echo     [],
echo     name='kairo',
echo     debug=False,
echo     bootloader_ignore_signals=False,
echo     strip=False,
echo     upx=True,
echo     upx_exclude=[],
echo     runtime_tmpdir=None,
echo     console=True,
echo     disable_windowed_traceback=False,
echo     argv_emulation=False,
echo     target_arch=None,
echo     codesign_identity=None,
echo     entitlements_file=None,
echo ^)
) > kairo.spec
echo ...Done
echo.

REM Build using spec file
echo Building Kairo executable...
pyinstaller kairo.spec

REM Check if build succeeded
echo.
if exist dist\kairo.exe (
    echo ========================================
    echo Build Successful!
    echo ========================================
    echo.
    echo Executable: %CD%\dist\kairo.exe
    echo.
    echo Bundled Resources:
    if exist dist\kairo\_internal\sounds echo   - Sounds folder
    if exist dist\kairo\_internal\data echo   - Data folder ^(template users.dat^)
    echo.
    echo User data will be stored in: %%APPDATA%%\Kairo
    echo.
) else (
    echo ========================================
    echo Build Failed!
    echo ========================================
    echo.
    echo Check the output above for errors.
    echo.
)

pause
