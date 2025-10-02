import threading
import sys
import pygame

from scripts.entities.TileMap import load_scaled_tile_map, get_layer_positions
from scripts.entities.door_lever import Lever, Door, LaserDoor
from scripts.entities.coin import Coin
from scripts.entities.enemy import Enemy
from scripts.entities.player import Player
from scripts.game.game_manager import Game
from scripts.game.game_settings import GameSettings
from scripts.menus.main_menu import MainMenu
from scripts.menus.settings_menu import SettingsMenu
from scripts.utils.game_utils import create_text
from typing import List
import time

class Handler:
    """
    The Handler class manages the menu states and shared variables between menus.
    It provides an interface to switch between menus and centralize variable management.
    """

    def __init__(self, levels_paths, levels_grids,
                 game_settings: GameSettings, paths: object, assets_dir: str) -> None:
        """
        Initialises the game handler, including video settings, player, enemies, tile maps, and menus.
        """

        # Setup video settings and screen resolution
        self._setup_video_settings(game_settings)
        self.loading_complete = False
        self.game = None
        self.current_menu = None
        self.next_menu = None
        self.level = 1
        self.progress = 0
        self.target_progress = 0
        self.stages = [game_settings.settings["loading_stages"][str(i)] for i in range(1, 8)]
        self.weights = [game_settings.settings["loading_weights"][str(i)] for i in range(1,8)]

        load_variables_thread = threading.Thread(target=self._load_variables, args=(levels_paths, levels_grids, game_settings, paths, assets_dir))
        load_variables_thread.start()
        self.clock = pygame.time.Clock()
        
        
    def _load_variables(self, levels_paths, levels_grids, game_settings, paths, assets_dir):
        self.value = 0
        self.initial_time = time.time()
        
        ## 1. Game Settings and Paths Initialization ##
        self.stage_index = 0
        self.target_progress = self.weights[self.stage_index]
        
        # Initialize game settings and paths
        self.game_settings = game_settings
        self.paths = paths
        self.assets_dir = assets_dir

        # Set volume based on game settings
        self.volume = self.game_settings.settings["audio_settings"]["sound_volume"]

        # Scaling
        self.x, self.y = self.game_screen.get_width(), self.game_screen.get_height()
        self.org_x, self.org_y = 1920, 1080
        self.scale_x, self.scale_y = self.x / self.org_x, self.y / self.org_y

        # level grids
        self.levels_grids = levels_grids
        self.levels_paths = levels_paths
        self.max_levels = len(levels_paths)
        

        ## 2. Load Tile Maps ##
        self.stage_index += 1
        self.target_progress += self.weights[self.stage_index]

        # Load tile maps for the levels
        levels_maps, stretched = self.load_tile_maps(self.game_screen, 
                                                     self.levels_paths, 
                                                     self.scale_x,
                                                     self.scale_y)
        self.levels_maps = levels_maps
        self.curr_tile_map = self.levels_maps[self.level - 1]
        self.curr_level_grid = self.levels_grids[self.level - 1]

        # Stretched resolution flag
        self.stretched = stretched

        ## 3. Player and Enemy Settings ##
        self.stage_index += 1
        self.target_progress += self.weights[self.stage_index]
        self.player_settings = self.game_settings.get_player_settings()
        self.enemy_settings = self.game_settings.get_enemy_settings()

        ## 4. Creating Player and Enemies ##
        self.stage_index += 1
        self.target_progress += self.weights[self.stage_index]
        
        # Create player and enemy instances
        self.player = Player(self.player_settings, self, 3)
        self.enemies = self.create_enemy_group()

        ## 5. Creating Game Objects and Lists ##
        self.stage_index += 1
        
        # Setup coins and highscore
        self.coins = self.create_coin_group()
        self.highscore = self.player_settings["highscore"]
        self.last_5_games = self.player_settings["last_5_games"]

        # Game objects
        self.game_list = []
        self._setup_game_list()
        self.game = self.game_list[self.level - 1]

        ## 6. Menu Initialization ##
        self.stage_index += 1
        self.target_progress += self.weights[self.stage_index]
        self.main_menu = MainMenu(self.game_screen, self)
        self.settings_menu = SettingsMenu(self.game_screen, self)

        ## 7. Finalizing and Setting Up ##
        self.stage_index += 1
        self.target_progress += self.weights[self.stage_index]
        
        # Switch to main menu and set loading complete
        self.target_progress = 100
        self.update_progress()
        self.loading_complete = True
        self.set_menu("main")
        print(f"Time to load game: {time.time() - self.initial_time}")

    def update_progress(self):

        # Calculate the distance to cover
        distance = self.target_progress - self.progress
        if abs(distance) > 0.01:  # Small threshold to prevent flickering
            # Speed proportional to the distance, clamped to a maximum speed
            speed = max(min(distance / 10, 5), 0.01)  # Adjust divisor and max speed for feel
            self.progress += speed
    
            # Ensure the value does not exceed the target
            if self.progress > self.target_progress:
                self.progress = self.target_progress
        else:
            self.progress = self.target_progress

            
    def _setup_game_list(self):
        self.game_list = []
        self.game_count = len(self.levels_paths)
        t = time.time()
        # Initialize the game state
        for i in range(len(self.levels_paths)):
            self.game_list.append(self.create_game())
            # Update progress based on the number of created instances
            self.level += 1
            
        print(f"Time to initialise level: {time.time() - t}\n")
            

        self.level = 1

        self.game = self.game_list[self.level - 1]

    def _setup_variables(self) -> None:
        # Create player and enemy objects
        self.player = Player(self.player_settings, self, 3)
        self.curr_level_grid = self.levels_grids[self.level - 1]
        self.curr_tile_map = self.levels_maps[self.level - 1]
        self.enemies = self.create_enemy_group()
        self.coins = self.create_coin_group()
        self.lever, self.door, self.laser_door = None, None, None
        if self.level == 3:
            self.laser_door = [LaserDoor(pos, (self.scale_x, self.scale_y)) for pos in get_layer_positions(self.levels_paths[self.level-1], "laser_door", 1, 1)]
        elif self.level >= 2:
            self.lever = Lever(get_layer_positions(self.levels_paths[self.level-1], "lever", 1, 1), (self.scale_x, self.scale_y)) if self.level in [2, 3] else None
            self.door = [Door(pos, (self.scale_x, self.scale_y)) if self.level in [2, 3] else None for pos in get_layer_positions(self.levels_paths[self.level-1], "mechanical_door", 1, 1)]




    def _setup_video_settings(self, game_settings) -> None:
        """
        Configures the video settings for the game screen (fullscreen or windowed).
        """
        video_settings = game_settings.settings["video_settings"]
        screen_width, screen_height = video_settings["resolution"]


        if video_settings["mode"] == "fullscreen":
            self.game_screen = pygame.display.set_mode(
                (screen_width, screen_height), pygame.DOUBLEBUF | pygame.FULLSCREEN
            )
        else:
            self.game_screen = pygame.display.set_mode(
                (screen_width, screen_height), pygame.DOUBLEBUF
            )

    @staticmethod
    def load_tile_maps(game_screen, tmx_paths: str, scale_x, scale_y) -> tuple:
        """
        Loads the tile maps for both levels and returns them.
        """
        tile_maps = []
        stretched = False
        for tmx_path in tmx_paths:
            tile_map, stretched = load_scaled_tile_map(game_screen, tmx_path, size_scale_x=scale_x, size_scale_y=scale_y)
            tile_maps.append(tile_map)

        return tile_maps, stretched

    def create_enemy_group(self) -> List[Enemy]:
        """
        Creates a list of enemies for the specified level.
        """
        enemy_positions = get_layer_positions(self.levels_paths[self.level-1], "enemies", 1, 1)
        curr_level_grid = self.levels_grids[self.level-1]
        return [Enemy(pos, curr_level_grid, self.enemy_settings, self, self.stretched) for pos in enemy_positions]

    def create_coin_group(self) -> List[Coin]:
        """
        Creates a list of enemies for the specified level.
        """
        coin_positions = get_layer_positions(self.levels_paths[self.level-1], "coins", 1, 1)
        return [Coin(pos, (self.scale_x, self.scale_y)) for pos in coin_positions]

    def create_game(self) -> Game:
        """
        Creates and returns a Game instance.
        """
        self._setup_variables()
        return Game(self.game_screen, self.player, self, self.lever, self.door, self.laser_door, self.enemies, self.coins, self.curr_level_grid, self.curr_tile_map, self.player_settings,
                    self.enemy_settings)

    def last_5(self):
        if len(self.last_5_games) > 4:
            self.last_5_games.pop(0)
        self.last_5_games.append([self.level, self.game.points])
        
    def set_menu(self, menu_name: str) -> None:
        """
        Switches the current menu to the specified one.

        Args:
            menu_name (str): The name of the menu to switch to (e.g., 'main', 'settings').
        """

        if menu_name == "main":
            self.current_menu = self.main_menu
        elif menu_name == "settings":
            self.current_menu = self.settings_menu
        elif menu_name == "game":
            self.current_menu = self.game
        elif menu_name == "next_level":
            self.level += 1 if self.level < self.max_levels else 0
            self.game.running = False
            self.game = self.game_list[self.level - 1]
            self.current_menu = self.game
        elif menu_name == "game_over":
            self.level = 1
            self.game.running = False
            self._setup_game_list()
            self.game = self.game_list[self.level-1]
            self.current_menu = self.main_menu
        else:
            raise ValueError(f"Unknown menu name: {menu_name}")
    
    def draw_loading_bar(self):
        # Whole loading bar
        pygame.draw.rect(self.game_screen, (40, 70, 190), (self.game_screen.get_width()//2 - 150, self.game_screen.get_height()//2 - 30//2, 100*3, 30), border_radius=10)
        # Outline of the whole loading bar
        pygame.draw.rect(self.game_screen, (30, 50, 100), (self.game_screen.get_width()//2 - 150, self.game_screen.get_height()//2 - 30//2, 100*3, 30), width=2, border_radius=10)
        # Progress bar
        pygame.draw.rect(self.game_screen, (100, 150, 255), (self.game_screen.get_width()//2 - 150, self.game_screen.get_height()//2 - 30//2, self.progress*3, 30), border_radius=10)
        # Outline of the progress bar
        pygame.draw.rect(self.game_screen, (30, 50, 100), (self.game_screen.get_width()//2 - 150, self.game_screen.get_height()//2 - 30//2, self.progress*3, 30), width=2, border_radius=10)


        
    def draw_menu_text(self):
        fps = self.clock.get_fps()
        stage_text, _ = create_text(f"{self.stages[self.stage_index]}", (255, 255, 255), 20)
        progress_text, _ = create_text(f"{int(self.progress)}%", (255, 255, 255), 20)
        fps_text, _ = create_text(f"{int(fps)}", (255, 255, 255), 35)
        width, height = self.game_screen.get_width(), self.game_screen.get_height()
        self.game_screen.blit(stage_text, (width//2 - 90, height//2+40))
        self.game_screen.blit(progress_text, (width//2 + 190, height//2-15))
        self.game_screen.blit(fps_text, (width//2, 50))
        
    def loading_menu(self):
        self.update_progress()
        self.game_screen.fill((50,50,50))
        self.draw_loading_bar()
        self.draw_menu_text()


        
    def run_menu(self):
        if self.current_menu is None:
            raise RuntimeError("No menu is set. Use set_menu() to specify a menu.")

        if self.next_menu:  # Check for a pending menu transition
            self.set_menu(self.next_menu)
            if self.current_menu == self.game_list[self.level-1]:
                curr_level = self.game_list[self.level-1]
                curr_level.player.vel.x = 0
                curr_level.player.vel.y = 0
                enemies = curr_level.enemies_list
                for enemy in enemies:
                    enemy.acc_dx = 0
                    enemy.acc_dy = 0

            self.next_menu = None  # Clear the transition flag

        if self.current_menu:
            self.current_menu.running = True
            self.current_menu.update()  # Update the current menu
            self.current_menu.render()  # Render the current menu
            
    def run(self) -> None:
        """
        Runs the currently active menu with slide transitions.
        """
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if self.loading_complete:
                    self.current_menu.handle_events(event)
            if not self.loading_complete or self.progress < 100:
                self.loading_menu()
            else:
                self.run_menu()

            pygame.display.flip()
            self.clock.tick(60)