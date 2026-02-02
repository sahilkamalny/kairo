"""Variable and DataType models for Kairo."""
from enum import Enum


class DataType(Enum):
    """Enumeration of data types for variables and command results."""
    NUMBER = "number"
    STRING = "string"
    DIRECTORY = "directory"
    FILE = "file"
    NULL = "null"


class Variable:
    """Represents a user-defined variable in Kairo.
    
    Variables can be:
    - Session variables (prefix #): Cleared on exit
    - Persistent variables (prefix $): Saved to disk
    """
    
    def __init__(self, name: str, value, var_type: DataType, is_persistent: bool = True):
        self.name = name
        self.value = value
        self.type = var_type
        self.is_persistent = is_persistent
    
    def __repr__(self):
        return f"Variable(name='{self.name}', value={self.value}, type={self.type.value})"
