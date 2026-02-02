"""
Configuration and path utilities for Kairo.
Provides cross-platform path resolution for application resources and user data.
"""
import os
import sys


def get_app_path():
    """Get the application's base directory (for bundled resources like sounds)."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_user_data_path():
    """Get the user data directory (cross-platform).
    
    Returns:
        Windows: %APPDATA%/Kairo
        macOS: ~/Library/Application Support/Kairo
        Linux: ~/.local/share/Kairo
    """
    if sys.platform == 'win32':
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
    elif sys.platform == 'darwin':
        base = os.path.expanduser('~/Library/Application Support')
    else:  # Linux and other Unix-like
        base = os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
    
    data_dir = os.path.join(base, 'Kairo')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir
