import json
import os
import io
from typing import Union, Any

class GameSettings:
    def __init__(self):
        # Setting up variables
        self.movement_keys = None
        self.all_settings = None

        # Settings files
        self.defaults_file = fr"config\default_settings.json"
        self.settings_file = fr"config\settings_saved.json"

        # Load defaults and settings
        self.defaults = self.load_defaults()
        loaded_settings = self.load_settings(self.settings_file) or {}

        # Extract sections or use defaults
        self.paths = loaded_settings.get("game_configurations", {}).get("paths",
                                                                           self.defaults.get("game_configurations",
                                                                                             {}).get("paths", {}))

        self.settings = loaded_settings.get("game_configurations", {}).get("settings",
                                                                           self.defaults.get("game_configurations",
                                                                                             {}).get("settings", {}))
        self.config = loaded_settings.get("game_configurations", {}).get("config",
                                                                         self.defaults.get("game_configurations",
                                                                                           {}).get("config", {}))
        # Apply settings
        self.apply_settings()

    def load_defaults(self):
        if os.path.exists(self.defaults_file):
            with open(self.defaults_file, 'r') as file:
                return json.load(file)
        print("Default settings file not found.")
        return {}

    def load_settings(self, file_path):
        try:
            with open(file_path, "r") as file:
                print("Settings file found, loading...")
                return json.load(file)
        except FileNotFoundError:
            print(f"Error: '{file_path}' not found. Using default settings.")
            return None
        except json.JSONDecodeError:
            print(f"Error: '{file_path}' is not a valid JSON file. Using default settings.")
            return None
        except Exception as e:
            print(f"An error occurred while loading '{file_path}': {e}. Using default settings.")
            return None


    @staticmethod
    def convert_to_bool(value: Union[str, bool, Any]) -> Union[bool, Any]:
        """Convert 'true'/'false' strings to booleans."""
        if isinstance(value, str):
            if value.lower() == "true":
                return True
            elif value.lower() == "false":
                return False
        return value  # Return the value unchanged if it's not a string

    def apply_settings(self):
        # Loop through settings categories (debug, gameplay, video, etc.)
        for category, options in self.settings.items():
            for key, value in options.items():
                options[key] = self.convert_to_bool(value)
            setattr(self, category, options)

    def save_all(self, file_path):
        try:
            game_config = {"game_configurations": {"paths": self.paths, "settings": self.settings, "config": self.config}}
            self.all_settings = {**game_config}  # Merge the two dictionaries
            # Check if the file already exists
            if os.path.exists(file_path):
                with open(file_path, "r") as file:  # Load existing data
                    try:
                        existing_data = json.load(file)
                    except json.JSONDecodeError:
                        existing_data = None  # Handle corrupted or empty files
            else:
                existing_data = None
    
            # Compare new data with existing data
            if existing_data == self.all_settings:
                return
            with open(file_path, "w") as file: # type: io.TextIOWrapper
                # Save the settings to the file
                json.dump(self.all_settings, file, indent=4)
                print(f"Settings saved to {file_path}.")
        except IOError:
            print(f"Failed to save settings to {file_path}.")

    def get_settings(self, category, key, default=None):
        """Get a specific setting value."""
        return self.settings.get(category, {}).get(key, default)

    def get_config(self, category, key, default=None):
        """Get a specific config value."""
        return self.config.get(category, {}).get(key, default)

    def set_settings(self, category, key, value):
        """Set a specific setting value."""
        if category in self.settings:
            self.settings[category][key] = value

    def set_config(self, category, key, value):
        """Set a specific config value."""
        if category in self.config:
            self.config[category][key] = value

    def get_player_settings(self):
        return self.config.get("player_settings", {})

    def get_enemy_settings(self):
        return self.config.get("enemy_settings", {})



