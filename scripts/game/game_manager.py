from __future__ import annotations

# Standard library imports
import sys
import time
from typing import List

# Third-party imports
import pygame
import pytmx

# Local imports
from scripts.entities.enemy import Enemy
from scripts.entities.player import Player
from scripts.entities.coin import Coin
from scripts.utils.game_utils import create_text

# Constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
DEBUG_SURFACE_DIMENSIONS = (200, 100)
DEBUG_TEXT_COLOR = (0, 0, 0)

# User events
PATH_FIND = pygame.USEREVENT + 1
UPDATE_TEXT = pygame.USEREVENT + 2
UPDATE_LASERS = pygame.USEREVENT + 3

# Initialize the Pygame mixer
pygame.mixer.init()


# Game class that holds game objects, handles events, runs the main game loop and renders the game screen.
class Game:
    """
    Game class that holds game objects, handles events, runs the main game loop,
    and renders the game screen.
    """

    def __init__(self,
                game_screen: pygame.Surface,
                player_obj: object,
                handler,
                lever,
                door,
                laser_door,
                enemies_list: List[object],
                coins_list: List[object],
                level_grid: List[List[int]],
                tile_map: pytmx.TiledMap,
                player_settings: dict,
                enemy_settings: dict) -> None:

        """
        Initializes the Game class.

        Args:
            game_screen (pygame.Surface): The Pygame screen object.
            player_obj (Player): The player object.
            enemies_list (List[Enemy]): A list of enemy instances.
            tile_map: The tile map object that holds the sprite groups.
            level_grid (List[List[int]]): 2D array representing the level grid.
            handler: Object managing game settings and utilities.
            player_settings (dict): Dictionary of settings for the player.
            enemy_settings (dict): Dictionary of settings for the enemy.
        """
        weights = [0.02060230877969804, 0.02160400835505302, 14.080069779418773, 0.08301209550434605, 6.5301252366308455, 1.3595540305914868]
        times_taken = [0.3863438606262207, 0.47954583168029785, 0.4688273429870605]
        weight_per_level = [time_taken / sum(times_taken) * 3 for time_taken in times_taken]
        weights = [weight * weight_per_level[handler.level-1] for weight in weights]
        
        handler.target_progress += weights[0]
        # Set up scaling and core attributes
        self._setup_core_attributes(game_screen, handler, player_settings, enemy_settings)

        handler.target_progress += weights[1]
        # Set up game objects and unpack tile map
        self._setup_game_objects(player_obj, lever, door, laser_door, enemies_list, coins_list, tile_map, level_grid)

        handler.target_progress += weights[2]
        # Set up the background and other visual surfaces
        self._setup_visual_elements()

        handler.target_progress += weights[3]
        # Set up clock, delta time, and user events
        self._setup_time_management()

        handler.target_progress += weights[4]
        # Set up debugging text surfaces
        self._setup_debugging_info()

        handler.target_progress += weights[5]
        # Set up sound effects
        self._setup_audio()

        self.last_time = time.time()

    # Setup Functions
    def _setup_core_attributes(self, game_screen, handler, player_settings, enemy_settings):
        # Scaling
        self.running = False
        self.game_width, self.game_height = game_screen.get_width(), game_screen.get_height()
        self.scale_x, self.scale_y = self.game_width / SCREEN_WIDTH, self.game_height / SCREEN_HEIGHT

        # Core attributes
        self.game_screen = game_screen
        self.handler = handler
        self.player_settings = player_settings
        self.enemy_settings = enemy_settings
        self.points = 0

    def _setup_game_objects(self, player_obj, lever, door, laser_door, enemies_list, coins_list, tile_map, level_grid):
        # Game objects
        self.player = player_obj
        self.enemies_list = enemies_list
        self.coins_list = coins_list
        self.lever = lever
        self.door = door
        self.laser_door = laser_door
        self.in_range = False
        self.respawn = False

        # Unpack tile_map
        self.bg1_tiles = tile_map.bg_layer_1
        self.bg2_tiles = tile_map.bg_layer_2
        self.door_tiles = tile_map.mechanical_door
        self.sword_position = tile_map.sword_position
        self.ladders = tile_map.ladders
        self.wall_jump_tiles = tile_map.wall_jump
        self.tiles = tile_map.tiles
        self.background_group = tile_map.background_group

        # Grid layout of the current level
        self.level_grid = level_grid

    def _setup_visual_elements(self):
        # Visual elements
        self.background = pygame.Surface((self.game_width, self.game_height))
        # Create surfaces for debugging information (e.g., player position, FPS)
        self.debug_surface = self.create_debug_surface(self.scale)
        self.rect_surf = self.create_rect_surface(self.scale)
        self.player_name_tag, _ = create_text("Player", (255, 255, 255), int(20*self.scale_x))
        self.enemy_name_tag, _ = create_text("Enemy", (255, 255, 255), int(20*self.scale_x))

        self.heart_image = self._load_image(f"{self.handler.assets_dir}\\Basic_GUI_Bundle\Icons\Icon_Large_HeartFull_SeethroughOutline.png", (30, 30))
        self.heart_empty_image = self._load_image(f"{self.handler.assets_dir}\\Basic_GUI_Bundle\Icons\Icon_Large_HeartEmpty_SeethroughOutline.png", (30, 30))

    def _setup_time_management(self):
        # Time management
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.last_update_time = 0

        # Set up timer game events
        pygame.time.set_timer(PATH_FIND, 100)
        pygame.time.set_timer(UPDATE_TEXT, 500)
        pygame.time.set_timer(UPDATE_LASERS, 2000)

    def _setup_debugging_info(self):
        # Debugging text and text surfaces
        # Get the players position
        self.player_pos_text = f"Player Position: {self.player.pos.x:.2f}, {self.player.pos.y:.2f}"
        # Create text surface
        self.player_pos_surface, _ = create_text(self.player_pos_text, (0, 0, 0), int(16*self.scale_x))
        # Get the FPS
        self.fps_text = f"FPS: {self.clock.get_fps():.2f}"
        # Create text surface
        self.fps_surface, _ = create_text(self.fps_text, (0, 0, 0), int(16*self.scale_x))

    def _setup_audio(self):
        # Sound effects
        self.die_sound = pygame.mixer.Sound(r"assets\audio\HALFTONE SFX Pack LITE\Gameplay\2. Loose\Loose_22.wav")
        self.channel = pygame.mixer.find_channel()
        self.die_sound.set_volume(self.handler.volume)


    # Utility Methods
    @staticmethod
    def _load_image(path: str, size: tuple[int, int]) -> pygame.Surface:
        return pygame.transform.scale(pygame.image.load(path), size)
    
    @staticmethod
    def create_debug_surface(scale) -> pygame.Surface:
        """Creates and returns the debug surface."""
        return pygame.Surface(scale(200, 100), pygame.SRCALPHA)

    @staticmethod
    def create_rect_surface(scale) -> pygame.Surface:
        """Creates a semi-transparent rectangle surface for debug info."""
        rect_surf = pygame.Surface(scale(200, 100), pygame.SRCALPHA)
        pygame.draw.rect(
            rect_surf, (200, 200, 200, 200), (0, 0, 200, 100), border_radius=15
        )
        return rect_surf

    @staticmethod
    def create_debug_text_surface(text: str, font_size: int) -> pygame.Surface:
        """Creates a text surface for debugging information."""
        surface, _ = create_text(text, (0, 0, 0), font_size)
        return surface

    def scale(self, x, y):
        """
        Scales the x or width and y or height values based on the screen size.
        """
        return int(x * self.scale_x), int(y * self.scale_y)

    def create_background(self) -> pygame.Surface:
        """Creates and returns the game background surface."""
        background = pygame.Surface(self.game_screen.get_size())
        background.fill((200, 200, 200))
        return background


    # Event Handling
    def handle_events(self, event) -> None:
        """
        Handles events in the Pygame window.

        Processes pygame events, if a QUIT event is detected,
        it quits Pygame and exits the program. It also processes input
        events for the player and manages interactions with enemies.
        """
        self.process_window_events(event)


    def handle_enemy_collisions(self) -> None:
        """
        Resets the player and enemies when a collision is detected.
        """
        self._check_player_enemy_collisions()
        self._check_enemy_door_collisions()
        self._check_laser_door_collisions()
    
    def _check_player_enemy_collisions(self) -> None:
        """
        Check for collisions between the player and enemies.
        If a collision is detected, the player respawns.
        """
        for enemy in self.enemies_list:
            if self.player.rect.colliderect(enemy.rect):
                self.respawn = True
            enemy.allow_move = True
    
    def _check_enemy_door_collisions(self) -> None:
        """
        Check if an enemy collides with a door and prevent enemy movement.
        """
        if self.door is not None and not self.door[0].open:
            for door in self.door:
                for enemy in self.enemies_list:
                    if door.rect.colliderect(enemy.rect):
                        enemy.allow_move = False
    
    def _check_laser_door_collisions(self) -> None:
        """
        Check if the player collides with a laser door. If so, respawn the player.
        """
        if self.laser_door is not None:
            for laser in self.laser_door:
                if self.player.rect.colliderect(laser.rect) and laser.open:
                    self.respawn = True
                
        

    def handle_keydown_events(self, event) -> None:
        """
        Handles keydown events, such as pausing the game or opening menus.
        """
        if event.key == pygame.K_ESCAPE:
            self.handler.next_menu = "main"
            self.running = False  # Exit the current loop for transition
            return  # Exit the main function
        if event.key == pygame.K_e and self.in_range:
            self.lever.turn_on = True if not self.lever.on else False

    def process_window_events(self, event) -> None:
        """
        Processes window-specific Pygame events like QUIT and key presses.
        """
        if event.type == PATH_FIND:
            self._trigger_enemy_pathfinding()
        elif event.type == UPDATE_TEXT:
            self._setup_debugging_info()
        elif event.type == UPDATE_LASERS:
            self._handle_laser_switch()
        elif event.type == pygame.KEYDOWN:
            self.handle_keydown_events(event)
    
    @staticmethod
    def _handle_quit_event() -> None:
        """
        Handles the event when the user requests to close the game.
        """
        pygame.quit()
        sys.exit()
    
    def _trigger_enemy_pathfinding(self) -> None:
        """
        Triggers the enemy pathfinding logic.
        """
        self.update_enemies_pathfinding()
    
    def _handle_laser_switch(self) -> None:
        """
        Handles the laser door switching state when triggered.
        """
        if self.laser_door is not None:
            for laser_door in self.laser_door:
                laser_door.switch_state = True


    # Game State Management
    def update_game_state(self) -> None:
        """
        Updates the positions of the player and enemies.
        """
        if self.handler.stretched:
            self.player.get_grid_pos((int(30*self.scale_x), int(30*self.scale_x)))
        else:
            self.player.get_grid_pos((int(30 * self.scale_x), int(30 * self.scale_y)))
        self.player.update(self.tiles, self.ladders, self.wall_jump_tiles, self.coins_list, self.door, self.dt)
        for enemy in self.enemies_list:
            enemy.update(self.level_grid, self.player.grid_pos, self.dt)

    def update_enemies_pathfinding(self) -> None:
        """
        Updates enemy paths using A* algorithm.
        """

        enemy_positions = []

        for enemy in self.enemies_list:
            enemy_positions.append(enemy.enemy_array_pos)
        for enemy in self.enemies_list:
            enemy.run_a_star(self.level_grid, self.player.grid_pos, enemy_positions)

    def reset_player_and_enemies(self) -> None:
        """
        Resets the player to the starting position and reinitialise enemies.
        """
        lives = self.player.lives
        self.player.vel = pygame.Vector2(0, 0)
        for enemy in self.enemies_list:
            enemy.vel = pygame.Vector2(0, 0)
        if self.player.finished_die_animation:
            self.respawn = False
            self.player = Player(self.player_settings, self.handler, lives-1)
            self.enemies_list = self.handler.create_enemy_group()
        else:
            if not self.player.die and not self.channel.get_busy():  # If the channel is not playing anything
                self.channel.play(self.die_sound)
            self.player.die = True


    # Rendering/Visuals
    def draw_debug_info(self):
        """
        Draws debug information onto the debug surface.
        """
        # Clear the debug surface
        self.debug_surface.fill((100, 100, 100, 0))
        self.debug_surface.blit(self.rect_surf, (0,0))

        # Mapping of debug settings to their corresponding surfaces and positions
        debug_items = {
            "display_player_stats": (self.player_pos_surface, self.scale(10, 10)),
            "display_fps": (self.fps_surface, self.scale(10, 40)),
        }

        # Iterate through the mapping and draw enabled debug information
        for setting, (surface, position) in debug_items.items():
            if self.handler.game_settings.settings["debug_settings"].get(setting, False):
                self.debug_surface.blit(surface, position)

    def render(self) -> None:
        """
        Draws all game elements onto the screen.
        """
        # Clear the screen with the background image
        self._draw_background()
    
        # Draw different layers
        self._draw_layers()
    
        # Draw individual game elements
        self._draw_coins()
        self._draw_lever()
        self._draw_doors()
        self._draw_laser_doors()
    
        # Render enemies
        self.render_enemies()
    
        # Draw the player
        self._draw_player()
    
        # Draw player name tag
        self.draw_player_name_tag()
    
        # Conditional debug rendering
        if self.handler.game_settings.settings["debug_settings"]["debug_mode"]:
            self._draw_debug_info()
    
        # Create surface to update the screen
        self._update_screen()
    
        return self.surf
    
    
    def _draw_background(self) -> None:
        """
        Draws the background image onto the screen.
        """
        self.game_screen.blit(self.background, (0, 0))
    
    
    def _draw_layers(self) -> None:
        """
        Draws all the sprite groups (background, tiles, etc.) onto the screen.
        """

        self.draw_sprite_group(self.background_group)
        self.draw_sprite_group(self.bg2_tiles)
        self.draw_sprite_group(self.bg1_tiles)
        self.draw_sprite_group(self.wall_jump_tiles)
        self.draw_sprite_group(self.tiles)
        self.draw_sprite_group(self.ladders)
    
    
    def _draw_coins(self) -> None:
        """
        Draws all the coins onto the screen.
        """
        for coin in self.coins_list:
            coin.animations(self.game_screen, self)
    
    
    def _draw_lever(self) -> None:
        """
        Draws the lever onto the screen if it exists.
        """
        if self.lever is not None:
            self.lever.animations(self.game_screen)
    
    
    def _draw_doors(self) -> None:
        """
        Draws the doors onto the screen if they exist.
        """
        if self.door is not None:
            for door in self.door:
                door.animations(self.game_screen)
    
    
    def _draw_laser_doors(self) -> None:
        """
        Draws the laser doors onto the screen if they exist.
        """
        if self.laser_door is not None:
            for i, laser_door in enumerate(self.laser_door):
                if i % 2 == 0:
                    laser_door.animations(self.game_screen)
    
    
    def _draw_player(self) -> None:
        """
        Draws the player onto the screen.
        """
        self.player.draw(self.game_screen, self.handler)
    
    
    def _draw_debug_info(self) -> None:
        """
        Draws the debug information if debug mode is enabled.
        """
        self.draw_debug_info()  # Blit the debug surface onto the game screen
        self.game_screen.blit(self.debug_surface, self.scale(30, 30))
    
    
    def _update_screen(self) -> None:
        """
        Creates a surface and updates the game screen.
        """
        self.surf = pygame.Surface((self.game_width, self.game_height))
        self.surf.blit(self.game_screen, (0, 0))

    def draw_sprite_group(self, group) -> None:
        """
        Draws all sprites in the given sprite group onto the game screen.
        """
        draw = False
        for sprite in group:
            if sprite.draw:
                draw = True
            else:
                draw = False
        if draw:
            group.draw(self.game_screen)


    def draw_player_name_tag(self) -> None:
        """
        Draws the player's name tag above the player.
        """

        if self.handler.game_settings.settings["gameplay_settings"]["display_name_tags"]:
            name_tag_pos = (self.player.rect.x - 8 * self.scale_x, self.player.rect.y - 16 * self.scale_y)
            self.game_screen.blit(self.player_name_tag, name_tag_pos)

        if self.lever is not None:
            if self.lever.rect.colliderect(self.player.rect):
                self.in_range = True
                key_hint_pos = (self.lever.rect.x - 8 * self.scale_x + self.player.rect.x // 15, self.player.rect.y - 25 * self.scale_y)
                key_hint_text = f"Press E to interact"
                key_hint_text_surface, _ = create_text(key_hint_text, (255,255,255), 20)
                self.game_screen.blit(key_hint_text_surface, key_hint_pos)
            else:
                self.in_range = False

        if self.handler.game_settings.settings["gameplay_settings"]["display_hud"]:
            level_text = f"{self.handler.level}"
            level_text_surface, level_rect = create_text(level_text, (255,255,255), 45)
            pygame.draw.rect(self.game_screen, (30,0,120), (self.game_width-60, self.game_height-60, 40, 40), border_radius=10)
            self.game_screen.blit(level_text_surface, (self.game_width-50, self.game_height-55))

            points_text = f"SCORE: {self.points}"
            points_text_surface, _ = create_text(points_text, (255,255,255), 40)
            self.game_screen.blit(points_text_surface, (self.game_width-650, 30))


            for i in range(0, self.player.lives):
                self.game_screen.blit(self.heart_image, (self.game_width-150+i*30, 30))
            for i in range(0, 3-self.player.lives):
                self.game_screen.blit(self.heart_empty_image, (self.game_width-90-i*30, 30))

    def render_enemies(self) -> None:
        """
        Renders all enemies onto the game screen.
        """
        for enemy in self.enemies_list:
            enemy.draw(self.game_screen, self.player.pos, self.handler, self.enemy_name_tag)
    
    def _calculate_delta_time(self, last_time: float) -> None:
        """
        Calculates delta time (dt) for frame rate control.
        """
        self.dt = (time.time() - last_time) * 60
    
    def _check_level_transition(self) -> bool:
        """
        Checks if the player has reached the top of the screen to transition to the next level.
        """
        if self.player.rect.y < 0:
            self.handler.next_menu = "next_level"
            self.running = False
            return True
        return False
    
    def _update_game_objects(self) -> None:
        """
        Updates game objects such as coins, levers, doors, and laser doors.
        """
        for coin in self.coins_list:
            coin.update()
    
        if self.lever is not None:
            self.lever.update()
    
        if self.door is not None:
            for door in self.door:
                door.update(self.lever)
    
        if self.laser_door is not None:
            for laser_door in self.laser_door:
                laser_door.update(self.lever)

    def update(self) -> None:
        """
        Main function that runs the game loop.
    
        Handles:
        - Running the game loop.
        - Updating player and enemy positions.
        - Handling user input events (key presses, mouse clicks, etc.).
        - Rendering all the assets onto the game screen.
        """
        # Calculate delta time (dt)
        self._calculate_delta_time(self.last_time)
        self.last_time = time.time()

        # Update game state (player, enemies)
        self.update_game_state()

        if self._check_level_transition():
            return  # Exit the main function

        # handle_events was here
        self.handle_enemy_collisions()
        # Calls the function to handles the player's inputs
        self.player.handle_inputs()
        if self.player.lives < 1:
            self.handler.next_menu = "game_over"
            self.running = False

        if self.handler.highscore < self.points:
            self.handler.highscore = self.points
            self.handler.player_settings["highscore"] = self.points

        # Update game objects like coins, doors, lasers, etc.
        self._update_game_objects()

        if self.respawn:
            self.reset_player_and_enemies()