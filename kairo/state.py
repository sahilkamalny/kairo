"""
Global application state for Kairo.
Centralizes mutable state that needs to be shared across modules.
"""
from kairo.models.variable import DataType

# Current logged-in user
current_user = None

# Current working directory (absolute path)
current_directory = None

# Result of the last executed command (value, type)
last_command_result = None

# Session variables (cleared on exit, prefix #)
session_variables = {}

# Persistent variables (saved to disk, prefix $)
persistent_variables = {}


def reset_session():
    """Reset session state (called on logout/reboot)."""
    global session_variables, last_command_result
    session_variables = {}
    last_command_result = None
