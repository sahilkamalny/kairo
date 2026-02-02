"""User model for Kairo authentication."""


class User:
    """Represents a user account in the system."""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
    
    def __repr__(self):
        return f"User(username='{self.username}')"
