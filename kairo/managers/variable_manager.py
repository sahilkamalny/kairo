"""Variable management for Kairo."""
import os
import json

from kairo.config import get_user_data_path
from kairo.models.variable import Variable, DataType
import kairo.state as state


class VariableManager:
    """Manages session and persistent variables."""
    
    @staticmethod
    def get_user_root(username: str) -> str:
        """Get the user's root directory path."""
        return os.path.join(get_user_data_path(), "users", username)
    
    @staticmethod
    def get_variables_file(username: str) -> str:
        """Get the path to the user's variables file."""
        variables_dir = os.path.join(get_user_data_path(), "variables")
        if not os.path.exists(variables_dir):
            os.makedirs(variables_dir)
        return os.path.join(variables_dir, f"{username}.var")
    
    @staticmethod
    def load_persistent_variables(username: str):
        """Load persistent variables from file."""
        from kairo.core.system import System
        
        variables_file = VariableManager.get_variables_file(username)
        
        try:
            if os.path.exists(variables_file):
                with open(variables_file, 'r') as f:
                    data = json.load(f)
                    state.persistent_variables = {}
                    for name, var_data in data.items():
                        state.persistent_variables[name] = Variable(
                            name, var_data['value'], 
                            DataType(var_data['type']), 
                            True
                        )
        except Exception as e:
            System.print_instant(f"Warning: Could not load variables: {e}", is_error=True)
    
    @staticmethod
    def save_persistent_variables(username: str):
        """Save persistent variables to file."""
        from kairo.core.system import System
        
        variables_file = VariableManager.get_variables_file(username)
        
        try:
            data = {}
            for name, var in state.persistent_variables.items():
                data[name] = {
                    'value': var.value,
                    'type': var.type.value
                }
            
            with open(variables_file, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            System.print_instant(f"Warning: Could not save variables: {e}", is_error=True)
    
    @staticmethod
    def set_variable(name: str, value, var_type: DataType):
        """Set a variable (session or persistent)."""
        variable = Variable(name, value, var_type, name.startswith('$'))
        
        if name.startswith('$'):
            state.persistent_variables[name] = variable
            VariableManager.save_persistent_variables(state.current_user)
        elif name.startswith('#'):
            state.session_variables[name] = variable
        else:
            raise ValueError("Variable names must start with $ or #")
    
    @staticmethod
    def get_variable(name: str):
        """Get a variable value."""
        if name.startswith('$'):
            return state.persistent_variables.get(name)
        elif name.startswith('#'):
            return state.session_variables.get(name)
        return None
    
    @staticmethod
    def resolve_path(path: str) -> str:
        """Convert relative path to absolute path."""
        user_root = VariableManager.get_user_root(state.current_user)
        if path.startswith('/'):
            return os.path.join(user_root, path[1:])
        else:
            return os.path.join(user_root, path)
    
    @staticmethod
    def get_relative_path(absolute_path: str) -> str:
        """Convert absolute path to relative path from user root."""
        user_root = VariableManager.get_user_root(state.current_user)
        if absolute_path.startswith(user_root):
            relative = absolute_path[len(user_root):]
            if relative.startswith(os.sep):
                relative = relative[1:]
            return relative
        return absolute_path
