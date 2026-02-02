"""
Kairo - Interactive OS Shell
Main entry point that imports from the kairo package.
"""
from kairo.main import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        from kairo.core.system import System
        System.handle_shutdown()
