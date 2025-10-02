# Importing python modules
from __future__ import annotations
#from pathlib import Path
import sys
import os

import pygame

# Add the directory containing platform_game to sys.path
from scripts.entities.TileMap import load_tmx_to_array # Importing the load_scaled_tile_map and load_tmx_to_array from TileMap.py
from scripts.utils.handler import Handler
from scripts.game.game_settings import GameSettings




def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller exe"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

# Checks if the script is being run directly
if __name__ == "__main__":

    # Initialises Pygame modules
    pygame.init()

    # Get the absolute path to the project directory
    # project_dir = Path(__file__).resolve().parent.parent

    # Construct the full path to the assets folder
    assets_dir = resource_path("assets/")

    game_settings = GameSettings()
    paths = game_settings.paths

    level_path_dict = paths["levels_paths"]
    # print(project_dir)
    # print(level_path_dict)
    # print(f"{assets_dir}\\{level_path_dict['base_path']}")
    base_path = f"{assets_dir}/{level_path_dict['base_path']}"


    # Paths to the tile maps
    levels_paths = [f"{base_path}{level_path_dict['files'][path]}" for path in level_path_dict['files']]
    levels_grids = [load_tmx_to_array(level_path) for level_path in levels_paths]

    # Initialises the handler object
    handler = Handler(levels_paths, levels_grids, game_settings, paths, assets_dir)
    if not handler.loading_complete:
        handler.run()
    # Sets the games state to the main menu
    handler.set_menu("main")
    # Runs the main menu
    handler.run()



