"""
Kairo Main Module
Provides the main() function and application entry point.

This module re-exports commonly used components for convenience.
"""
import os
import sys
import json
import time
import shutil

from colorama import Fore, Style

from kairo.config import get_app_path, get_user_data_path
from kairo.core.system import System
from kairo.core.terminal import TerminalState, AsciiArt
from kairo.managers.user_manager import UserManager
from kairo.managers.variable_manager import VariableManager
from kairo.models.user import User
import kairo.state as state


def main():
    """Main application entry point."""
    from colorama import init
    init()
    
    # Import UI components here to avoid circular imports
    # These are still in app.py during transition
    try:
        from kairo.ui.splash import SplashScreen
        from kairo.ui.login import CursesLoginScreen
        from kairo.core.curses_wrapper import Curses
    except ImportError:
        # Fallback to app.py during transition
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from app import SplashScreen, CursesLoginScreen, Curses
    
    SplashScreen.show()
    
    # User data lives in platform-specific location
    user_data_dir = get_user_data_path()
    users_file = os.path.join(user_data_dir, "users.dat")
    
    # On first run, copy the template users.dat from the app bundle
    if not os.path.exists(users_file):
        template_file = os.path.join(get_app_path(), "data", "users.dat")
        if os.path.exists(template_file):
            shutil.copy(template_file, users_file)
        else:
            # Create a default users file with guest account
            default_users = {"users": [{"username": "guest", "password": "guest"}]}
            with open(users_file, 'w') as f:
                json.dump(default_users, f, indent=4)
    
    users = UserManager.load_users(users_file)
    
    while True:  # Loop to return to menu after create/remove
        System.clear_screen()
        
        try:
            login_screen = CursesLoginScreen(users)
            action, data = Curses.wrapper(login_screen.run)
            
            if action == "exit":
                System.clear_screen()
                sys.exit(0)
            
            elif action == "login":
                state.current_user = data
                state.current_directory = System.create_user_directory(state.current_user)
                VariableManager.load_persistent_variables(state.current_user)
                System.clear_screen()
                System.welcome(state.current_user)
                break  # Exit the login loop, enter main command loop
            
            elif action == "create":
                username, password = data
                users.append(User(username, password))
                UserManager.save_users(users, users_file)
                System.create_user_directory(username)
                
                System.clear_screen()
                print(f"\n{Fore.GREEN}✓ User '{username}' created successfully!{Style.RESET_ALL}")
                time.sleep(2)
                
                users = UserManager.load_users(users_file)
                continue
            
            elif action == "remove":
                username = data
                users = [u for u in users if u.username.lower() != username.lower()]
                UserManager.save_users(users, users_file)
                
                System.clear_screen()
                print(f"\n{Fore.GREEN}✓ User '{username}' removed successfully!{Style.RESET_ALL}")
                time.sleep(2)
                continue
        
        except KeyboardInterrupt:
            System.clear_screen()
            sys.exit(0)

    # Main command loop
    from kairo.commands.loop import command_loop
    command_loop()
