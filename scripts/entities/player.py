# Importing python modules
import os

import pygame
from pygame import Surface
from itertools import chain


def load_animations(base_folder, frame_size):
    animations = {}

    # Iterate through subfolders in the base animation folder
    for animation_name in os.listdir(base_folder):
        animation_path = os.path.join(base_folder, animation_name)

        # Only process directories (e.g., walk, jump, idle)
        if os.path.isdir(animation_path):
            frames = []
            for filename in sorted(os.listdir(animation_path)):
                if filename.endswith(".png"):  # Adjust for your image format
                    frame_path = os.path.join(animation_path, filename)
                    frame = pygame.image.load(frame_path).convert_alpha()
                    frame = pygame.transform.scale(frame, frame_size)  # Adjust for your frame size
                    frames.append(frame)
            animations[animation_name] = frames

    return animations

# Defining Player class
class Player:
    """
    Represents the player character in the game.

    Attributes:
        pos (pygame.Vector2): The player's position in the game world.
        vel (pygame.Vector2): The player's velocity vector.
        rect (pygame.Rect): The player's rectangular hitbox.
        onPlatform (bool): Indicates if the player is on a platform.
        climbing (bool): Indicates if the player is climbing a ladder.
        animation_dict (dict): Contains the player's animation frames.
        curr_animation (str): The current animation being displayed.
    """

    def __init__(self, player_settings, handler, lives) -> None:
        """
        Initializes the Player class.

        Args:
            player_settings (dict): A dictionary containing player settings.
        """
        # Settings
        self._initialise_settings(player_settings, lives)
        self._initialise_position_and_movement(handler)
        self._initialise_animation(handler)
        self._initialise_key_bindings()
        start_pos_y = int((self.rect.y+15)/int(30*self.scale_x))
        start_pos_x = int((self.rect.x+15)/int(30*self.scale_x))
        self.grid_pos = [start_pos_y, start_pos_x]

    def _initialise_settings(self, player_settings: dict, lives) -> None:
        self.player_settings = player_settings
        self.movement_settings = player_settings["movement"]
        self.dimensions = player_settings["player_dimensions"]
        self.lives = lives

        # Load player colour from settings
        self.colour = self.player_settings["player_colour"]

    def _initialise_position_and_movement(self, handler) -> None:

        self.game_width, self.game_height = handler.game_screen.get_width(), handler.game_screen.get_height()
        self.org_x, self.org_y = 1920, 1080
        self.scale_x, self.scale_y = self.game_width / self.org_x, self.game_height / self.org_y
        stretched = True if self.org_x / self.org_y != self.scale_x / self.scale_y else False
        y_move = -150 if stretched else 0
        # Initialize position and velocity
        self.pos = pygame.Vector2(int(self.player_settings["spawn_position"][0]*self.scale_x), int(self.player_settings["spawn_position"][1]*self.scale_y) + y_move)
        self.vel = pygame.Vector2(0, 0)

        # Define the hitbox dimensions and create the hitbox (rect)
        self.width, self.height = int(self.dimensions["hitbox_size"][0]*self.scale_x), int(self.dimensions["hitbox_size"][1]*self.scale_y)
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)

        # Movement attributes
        self.walk_speed = int(self.movement_settings["walk_speed"] * self.scale_x)
        self.gravity_speed = self.movement_settings["gravity_speed"] * self.scale_y
        self.terminal_velocity = self.movement_settings["terminal_velocity"] * self.scale_y
        self.jump_speed = self.movement_settings["jump_speed"] * self.scale_y
        self.climb_speed = self.movement_settings["climb_speed"] * self.scale_y

        # Collision buffer for vertical adjustments
        self.vertical_collision_buffer = int(self.player_settings["collision_buffer"]["vertical"] * self.scale_y) # Used to prevent clipping during vertical collisions

        # State attributes
        self.onPlatform = False
        self.can_wall_jump = False
        self.climbing = False
        self.onLadder = False
        self.falling = False

    def _initialise_animation(self, handler) -> None:
        # Load animation frames based on the player's dimensions
        frame_size = int(self.dimensions["frame_size"][0]*self.scale_x), int(self.dimensions["frame_size"][1]*self.scale_y)


        self.sprite_path = f"{handler.assets_dir}\\{handler.paths["player_sprite"]}"

        self.animation_dict = load_animations(self.sprite_path, frame_size)

        self.combat_path = f"{handler.assets_dir}\\{handler.paths["player_sprite"]}\\Combat"
        self.combat_dict = load_animations(self.combat_path, frame_size)
        for combat in self.combat_dict.keys():
            self.animation_dict[combat] = self.combat_dict[combat]

        # Set default animation state
        self.curr_animation = "Idle"
        self.curr_animation_type = ""
        self.curr_frame = 0
        self.flip_animation = False
        self.finished_die_animation = False
        self.die = False

    def _initialise_key_bindings(self) -> None:
        # Map main movement keys from settings to Pygame key constants
        self.main_movement_keys = self._map_keys(self.movement_settings["main_keys"])

        # Map alternative movement keys if provided; use an empty dictionary otherwise
        self.alternative_movement_keys = self._map_keys(
            self.movement_settings.get("alternative_keys", {})
        )

    @staticmethod
    def _map_keys(key_mapping: dict) -> dict:
        """
        Maps key actions to Pygame key constants.

        Args:
            key_mapping (dict): A dictionary of actions and key strings.

        Returns:
            dict: A dictionary with actions mapped to Pygame key constants.
        """
        return {
            action: getattr(pygame, key_str.split(".")[1], None)
            for action, key_str in key_mapping.items()
        }

    def draw(self, screen: Surface, handler) -> None:
        # Draws the player's rect onto the screen
        if handler.game_settings.settings["debug_settings"]["display_player_hitbox"]:
            pygame.draw.rect(screen, self.colour, self.rect, 2)
        self.animations(screen)

    def animations(self, screen):

        if self.curr_frame < len(self.animation_dict[self.curr_animation]) -1:
            if self.curr_animation != "Die":
                self.curr_frame += 0.4
            else:
                self.curr_frame += 0.17
        else:
            if self.curr_animation == "Die":
                self.finished_die_animation = True
                self.die = False
            self.curr_frame = 0

        # Flip the frame if moving left
        frame = self.animation_dict[self.curr_animation][int(self.curr_frame)]
        if self.flip_animation:
            frame = pygame.transform.flip(self.animation_dict[self.curr_animation][int(self.curr_frame)], True, False)  # Flip horizontally
        screen.blit(frame, (self.rect.x - 60*self.scale_x, self.rect.y - 70*self.scale_y))

    def draw_vel_lines(self, screen: Surface) -> None:
        if self.vel.x > 0 or self.vel.x < 0:
            pygame.draw.line(screen, (155, 15, 100), (self.rect.x, self.rect.y+16), (self.rect.x+self.vel.x*25, self.rect.y+16), 2)

        if self.vel.y > 0 or self.vel.y < 0:
            pygame.draw.line(screen, (155, 15, 100), (self.rect.x, self.rect.y + 16),
                             (self.rect.x, self.rect.y + 16 + self.vel.y * 10), 2)

    def get_grid_pos(self, world_size):
        start_pos_y = int((self.rect.y+15)/world_size[0])
        start_pos_x = int((self.rect.x+15)/world_size[1])
        self.grid_pos = [start_pos_y, start_pos_x]

    def update_animation(self):
        if self.die:
            self.curr_animation = "Die"
        elif self.climbing:
            self.curr_animation = "LadderClimb"
        elif self.falling:
            self.curr_animation = "JumpFall"
        elif self.vel.y < 0:  # Player is jumping or falling
            self.curr_animation = f"{self.curr_animation_type}Jump" if self.curr_animation_type == "Sword" else "Jump"
        elif self.vel.x != 0:  # Player is moving horizontally
            self.curr_animation = f"{self.curr_animation_type}Run" if self.curr_animation_type == "Sword" else "Run"
        elif not (self.curr_animation == "SwordCombo01" and self.curr_frame <= len(
                self.animation_dict[self.curr_animation]) - 1):
            self.curr_animation = f"{self.curr_animation_type}Idle" if self.curr_animation_type == "Sword" else "Idle"

    def handle_jump_climb(self, keys):
        if keys[self.main_movement_keys["jump"]] or keys[self.alternative_movement_keys["jump"]]:
            self.jump()
            self.climbing = False

        elif (keys[self.main_movement_keys["climb"]] or keys[
            self.alternative_movement_keys["climb"]]) and self.onLadder:
            self.vel.y = -self.climb_speed
            self.climbing = True
            self.pos.x = self.ladder.rect.x

    def handle_mouse_buttons(self, mouse_buttons):
        if mouse_buttons[0] and self.curr_animation != "SwordCombo01":
            self.curr_frame = 0
            self.curr_animation = "SwordCombo01"
        elif not mouse_buttons[0] and not self.curr_animation == "SwordCombo01":
            self.curr_animation = "Idle"


    def handle_left_right_movement(self, keys):
        if keys[self.main_movement_keys["move_right"]] or keys[self.alternative_movement_keys["move_right"]]:
            self.walk_right()
            self.flip_animation = False
            self.climbing = False

        elif keys[self.main_movement_keys["move_left"]] or keys[self.alternative_movement_keys["move_left"]]:
            self.walk_left()
            self.flip_animation = True
            self.climbing = False

        else:
            self.vel.x = 0

    def handle_inputs(self) -> None:
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()

        if not self.die and not self.finished_die_animation:

            self.handle_mouse_buttons(mouse_buttons)

            self.handle_jump_climb(keys)

            self.handle_left_right_movement(keys)


        self.update_animation()

    # Handles x-axis collisions with platforms, coins, wall jump tiles, and doors
    def collisions_x(self, platforms: list, wall_jump_tiles, coins_list, door_list) -> None:
        # Ensure lists are not None
        wall_jump_tiles = wall_jump_tiles or []
        coins_list = coins_list or []
        door_list = door_list or []
    
        for tile in chain(platforms, wall_jump_tiles, coins_list, door_list):
            if tile is None:
                continue
    
            predicted_rect = self.rect.move(self.vel.x, 0)
            if tile.rect.colliderect(predicted_rect):
                self._handle_tile_collision_x(tile, coins_list, wall_jump_tiles, door_list)
    
        # Update the rect's x-coordinate to match the new position
        self.rect.x = int(self.pos.x)
    
    # Handle the collision for each type of tile on the x-axis
    def _handle_tile_collision_x(self, tile, coins_list, wall_jump_tiles, door_list):
        if tile in coins_list:
            self._handle_coin_pickup(tile)
            return
        elif tile in wall_jump_tiles:
            self._enable_wall_jump()
        elif tile in door_list and tile.open:
            self._handle_door_collision()
            return
    
        # Prevent clipping and stop movement if colliding with any platform
        self.pos.x -= self.vel.x
        self.vel.x = 0
    
    # Handle coin pickup
    def _handle_coin_pickup(self, tile):
        tile.pickup = True
    
    # Enable wall jump
    def _enable_wall_jump(self):
        self.can_wall_jump = True
    
    # Handle door collision
    def _handle_door_collision(self):
        return

    # Handles y-axis collisions with platforms, coins, wall jump tiles, and doors
    def collisions_y(self, platforms: list, wall_jump_tiles: list, coins_list: list, door_list: list) -> None:
        
        self.onPlatform = False
        # Ensure lists are not None
        wall_jump_tiles = wall_jump_tiles or []
        coins_list = coins_list or []
        door_list = door_list or []
    
        predicted_rect = self.rect.move(0, self.vel.y)
    
        for tile in chain(platforms, wall_jump_tiles, coins_list, door_list):
            if tile is None or not tile.rect.colliderect(predicted_rect):
                continue
    
            if self._handle_tile_collision_y(tile, coins_list, wall_jump_tiles, door_list):
                break
    
    def _handle_tile_collision_y(self, tile, coins_list, wall_jump_tiles, door_list):
        if tile in coins_list:
            self._handle_coin_pickup(tile)
            return False
        elif tile in door_list and tile.open:
            self._handle_door_collision()
            return False
    
        if self.vel.y > 0:  # Falling
            self._handle_fall_collision(tile, wall_jump_tiles)
            return True
        elif self.vel.y < 0:  # Jumping
            self._handle_jump_collision(tile)
            return True

    # Handles y-axis collisions with platforms


    def _handle_fall_collision(self, tile, wall_jump_tiles):
        """Handle collision when falling onto a platform."""
        if self.rect.bottom - self.height // 2 <= tile.rect.top + self.vertical_collision_buffer:
            self.vel.y = 0  # Stop vertical velocity
            self.pos.y = tile.rect.top - self.height  # Align on the platform
            self.onPlatform = True

            if tile in wall_jump_tiles:
                self.can_wall_jump = True

    def _handle_jump_collision(self, tile):
        """Handle collision when jumping up into a platform."""
        self.vel.y = 0  # Stop vertical velocity
        self.pos.y = tile.rect.bottom  # Align below the platform
        self.climbing = False


    def collisions_ladders(self, ladders):
        self.climbing = False
        self.onLadder = False
        for ladder in ladders:


            # Checks if the player's rect is going to collide with the platform's rect
            if ladder.rect.colliderect(self.rect.move(0, self.vel.y+30)):
                for other_ladder in ladders:
                    if ladder.rect.colliderect(other_ladder.rect.move(0, self.vel.y)):
                        self.curr_animation = "LadderClimbFinish"

                self.onLadder = True
                self.ladder = ladder

                break





    def gravity(self) -> None:
        # Checks whether the g acting on the player < terminal velocity
        if not self.onPlatform and self.vel.y < self.terminal_velocity:
            # Applies gravity to the player
            self.vel.y += self.gravity_speed


    def jump(self) -> None:
        # If the player is on a platform
        if self.onPlatform or self.can_wall_jump:
            # Sets the player's y velocity to -10
            self.vel.y = -self.jump_speed
            self.onPlatform = False  # Reset onPlatform flag after jumping
            self.can_wall_jump = False  # Reset wall jump flag after jumping

    def walk_right(self) -> None:
        # Moves the player's position to the right
        self.vel.x = self.walk_speed

    def walk_left(self) -> None:
        # Move the player's position to the left
        self.vel.x = -self.walk_speed

    def update(self, platforms, ladders, wall_jump_tiles, coins_list, door_list, dt) -> None:

        # Prevent player from going off the left side of the screen
        if self.pos.x <= 0:
            self.pos.x = 1

        # Update horizontal position and handle collisions
        if not self.climbing:
            self.pos.x += self.vel.x * dt
        self.rect.x = int(self.pos.x)
        self.collisions_x(platforms, wall_jump_tiles, coins_list, door_list)

        # Update vertical position and handle collisions
        self.pos.y += self.vel.y * dt
        self.rect.y = int(self.pos.y)
        self.collisions_ladders(ladders)
        self.collisions_y(platforms, wall_jump_tiles, coins_list, door_list)

        # Apply gravity if the player is not on a platform
        if not self.onPlatform:
            self.gravity()

        else:
            self.vel.y = 0
            self.falling = False

        # Update the rectangle's position to match the player's position
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)

