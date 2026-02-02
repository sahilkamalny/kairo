"""User management for Kairo."""
import sys
import json

from kairo.models.user import User


class UserManager:
    """Handles user authentication and persistence."""
    
    @staticmethod
    def load_users(file_path: str) -> list:
        """Load users from JSON file."""
        from kairo.core.system import System
        
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                return [User(user['username'], user['password']) for user in data['users']]
        except (FileNotFoundError, json.JSONDecodeError) as e:
            error_msg = "USER DATA FILE NOT FOUND" if isinstance(e, FileNotFoundError) else "INVALID USER DATA FILE FORMAT"
            System.throw_error(error_msg)
            sys.exit(1)

    @staticmethod
    def save_users(users: list, file_path: str):
        """Save users to JSON file."""
        data = {'users': [{'username': user.username, 'password': user.password} for user in users]}
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def match_user(users: list, username_input: str):
        """Find user by username."""
        for user in users:
            if user.username.lower() == username_input.lower():
                return user
        return None


class UserOperations:
    """User creation and removal operations."""
    
    @staticmethod
    def add_new_user(users: list, file_path: str):
        """Add a new user to the system."""
        from kairo.core.system import System
        
        System.print_slow("Enter new username: ", end='')
        username = input()
        
        # Check if user already exists
        if UserManager.match_user(users, username):
            System.throw_error(f"User '{username}' already exists")
            return users
        
        System.print_slow("Enter password: ", end='')
        password = input()
        
        users.append(User(username, password))
        UserManager.save_users(users, file_path)
        System.create_user_directory(username)
        
        return users
    
    @staticmethod
    def remove_user(users: list, file_path: str):
        """Remove a user from the system."""
        from kairo.core.system import System
        
        System.print_slow("Enter username to remove: ", end='')
        username = input()
        
        user = UserManager.match_user(users, username)
        if not user:
            System.throw_error(f"User '{username}' not found")
            return users
        
        users = [u for u in users if u.username.lower() != username.lower()]
        UserManager.save_users(users, file_path)
        
        return users
