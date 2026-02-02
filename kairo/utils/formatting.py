"""Number and argument formatting utilities for Kairo."""
import re


class NumberFormatter:
    """Formats numbers for consistent display."""
    
    @staticmethod
    def format_number(value) -> str:
        """Consistently format numbers to always show decimal point."""
        if isinstance(value, (int, float)):
            if value == int(value):
                return f"{int(value)}.0"
            else:
                return str(float(value))
        return str(value)


class ArgumentParser:
    """Parses command arguments with quote support."""
    
    @staticmethod
    def parse_args_with_quotes(args_list: list) -> list:
        """Parse argument list, treating quoted strings as single arguments."""
        if not args_list:
            return []
        
        args_str = ' '.join(args_list)
        parsed = []
        current_arg = ""
        in_quotes = False
        quote_char = None
        
        i = 0
        while i < len(args_str):
            char = args_str[i]
            
            if char in ('"', "'") and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
            elif char == ' ' and not in_quotes:
                if current_arg:
                    parsed.append(current_arg)
                    current_arg = ""
            else:
                current_arg += char
            
            i += 1
        
        if current_arg:
            parsed.append(current_arg)
        
        return parsed
