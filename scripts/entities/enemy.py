# Importing necessary Python modules
import math
from typing import List, Tuple

import pygame
from PIL.ImageChops import screen
from pygame import Surface

from scripts.game.algorithms.pathfinding import a_star


class Enemy:
    """
    The 'Enemy' class handles the behavior of enemy instances in the game, including their movement, pathfinding, and responses
    to player actions such as movement.

    Attributes:
    - rect (pygame.Rect): The rectangle (hitbox) representing the enemy's position and size for collision detection.
    - tile_array (List[List[int]]): The level's grid map used for pathfinding and navigation (0 for empty, 1 for obstacles).
    - enemy_array_pos (Tuple[int, int]): The enemy's position in the level grid, represented by grid indices (x, y).
    - current_path (List[Tuple[int, int]]): The path that the enemy follows, calculated using the A* algorithm or another pathfinding method.
    - level_width (int): The width of the level (in tiles).
    - level_height (int): The height of the level (in tiles).
    - acc_dx (float): The enemy's accumulated horizontal velocity (x-axis), representing its movement speed in the x-direction.
    - acc_dy (float): The enemy's accumulated vertical velocity (y-axis), representing its movement speed in the y-direction.
    - last_player_pos (List[int]): The player's last known position, used to update the enemy's pathfinding.

    Methods:
    - __init__: Initializes the enemy with its grid position, level grid, and initial settings.
    - update_pos: Updates the enemy's position in the grid when it is aligned to the 30x30 grid.
    """

    def __init__(self,
                 grid_position: Tuple[int, int],
                 level_grid: List[List[int]],
                 enemy_settings: dict,
                 handler,
                 stretched) -> None:

        """
       Initialises the enemy with its position and the level grid map.

       Parameters:
       - position (Tuple[int, int]): The initial position of the enemy in the level's grid (x, y).
       - level_grid (List[List[int]]): A 2D list representing the level's grid (0 for empty space, 1 for obstacles).
       """

        self.x, self.y = handler.game_screen.get_width(), handler.game_screen.get_height()
        self.org_x, self.org_y = 1920, 1080
        if stretched:
            self.scale_x, self.scale_y = self.x / self.org_x, self.x / self.org_x
        else:
            self.scale_x, self.scale_y = self.x / self.org_x, self.y / self.org_y

        self.enemy_settings = enemy_settings
        self.enemy_speed = enemy_settings["enemy_speed"] * self.scale_x
        self.enemy_colour = enemy_settings["enemy_colour"]
        # Initialize the enemy's rectangle for collision detection (scaled to fit tile size)
        self.rect = pygame.Rect(grid_position[0] * 30 * self.scale_x,
                                grid_position[1] * 30 * self.scale_y,
                                30 * self.scale_x,
                                30 * self.scale_y)

        # Store the level grid to facilitate pathfinding and movement calculations
        self.tile_array = level_grid

        # Set the enemy's position in the grid
        self.enemy_array_pos: Tuple[int, int] = grid_position

        # List for the path the enemy will follow (e.g., from A* algorithm)
        self.current_path: List[Tuple[int, int]] = []

        # Get the dimensions of the level grid (width and height in tiles)
        self.level_width: int = len(level_grid[0])  # Number of columns (tiles wide)
        self.level_height: int = len(level_grid)  # Number of rows (tiles high)

        # Initialize horizontal (dx) and vertical (dy) accelerations, used for smooth movement
        # These values represent the enemy's velocity, accumulated over time.
        # They allow for continuous movement in the respective directions, influenced by pathfinding.
        self.acc_dx: float = 0.0  # Horizontal velocity (x-direction)
        self.acc_dy: float = 0.0  # Vertical velocity (y-direction), influenced by gravity or jumping

        # Store the last known player position for pathfinding updates
        self.last_player_pos: List[int] = []
        
        self.allow_move = True
        animation_frames = [pygame.image.load(r"assets\bat_enemy\1.png"),
                            pygame.image.load(r"assets\bat_enemy\2.png"),
                            pygame.image.load(r"assets\bat_enemy\3.png"),
                            pygame.image.load(r"assets\bat_enemy\4.png"),
                            pygame.image.load(r"assets\bat_enemy\5.png"),]
        self.animation_frames = [pygame.transform.scale(frame, (int(30*self.scale_x)*2, int(30*self.scale_y)*2)) for frame in animation_frames]
        self.curr_frame = 0
        self.flip_animation = False
    def update_pos(self):

        # Update the enemy's position in the grid based on the rectangle's coordinates
        self.enemy_array_pos = [int(self.rect.y / (30*self.scale_y)), int(self.rect.x / (30*self.scale_y))]


    def move(self, dt):
        if self.allow_move:
            # Get the current target position from the path
            y2, x2 = self.current_path[0]
    
            # Calculate the distances between the current and target positions
            dx = x2 * 30*self.scale_x - self.rect.x
            dy = y2 * 30*self.scale_y - self.rect.y
    
            # Normalize the distances to ensure consistent speed
            mag = math.hypot(dx, dy)  # Euclidean distance (same as sqrt(dx^2 + dy^2))
            if mag == 0:
                return
    
            # Normalises the distances by dividing by the magnitude
            norm_dx = dx / mag
            norm_dy = dy / mag
    
            # Adds the normalised distances to the accumulated movement
            self.acc_dx += norm_dx  *self.enemy_speed*dt # Multiplier for speed
            self.acc_dy += norm_dy *self.enemy_speed*dt # Multiplier for speed
            
            if self.acc_dx > 0:
                self.flip_animation = False
            else:
                self.flip_animation = True
            # Updates the rect position with accumulated movement
            self.rect.x += int(self.acc_dx)
            self.rect.y += int(self.acc_dy)
    
            # Subtracts the integer part of the accumulated movement to keep the decimal part
            self.acc_dx -= int(self.acc_dx)
            self.acc_dy -= int(self.acc_dy)


    def run_a_star(self, current_level: list[list[int]], player_pos: list[int], enemy_positions) -> None:
        """
        Updates the enemy's path toward the player using the A* algorithm.
        """
        
        # Update path only if the player's position has changed
        if tuple(self.last_player_pos) != tuple(player_pos):
            self.last_player_pos = [int(player_pos[0]), int(player_pos[1])]
    
            # Find path from enemy to player
            self.current_path = a_star(
                current_level,
                (int(self.enemy_array_pos[0]), int(self.enemy_array_pos[1])),
                (int(player_pos[0]), int(player_pos[1])),
                enemy_positions
            )
    
            # Skip the enemy's current position in the path
            if self.current_path:
                self.current_path = self.current_path[1:]
    




    def draw_path_lines(self, game_window: Surface, player_pos) -> None:
        # Define a scaling factor for position adjustment
        scale = 30
        node_radius = scale // 2  # For center adjustments

        # Loop through the path and draw lines between consecutive nodes
        for i in range(len(self.current_path) - 1):
            start_pos = (self.current_path[i][1] * scale + node_radius, self.current_path[i][0] * scale + node_radius)
            end_pos = (
            self.current_path[i + 1][1] * scale + node_radius, self.current_path[i + 1][0] * scale + node_radius)

            # Special case for the last path segment: to player
            if i == len(self.current_path) - 2:
                pygame.draw.line(game_window, (50, 30, 100), (start_pos[1]*30*self.scale_x, start_pos[0]*30*self.scale_y),
                                 (player_pos.x, player_pos.y), 3)
            # Special case for the first path segment: from the enemy
            elif i == 0:
                pygame.draw.line(game_window, (20, 30, 100), (self.rect.x + node_radius, self.rect.y + node_radius),
                                 end_pos, 3)
            else:
                # General path lines
                pygame.draw.line(game_window, (20, 80, 100), start_pos, end_pos, 3)


    def draw_path_rects(self, game_window: Surface) -> None:
        # Loop through the path
        for something in self.current_path:
            # pygame.draw.rect(game_window, (50, 50, 50), (something[1] * 30, something[0] * 30, 30,30), 3)
            pygame.draw.circle(game_window, (50, 50, 50), ((something[1]*30*self.scale_y) + (30*self.scale_x)//2,
                                                           (something[0]*30*self.scale_x) + (30*self.scale_y)//2), 5)
    def animations(self, game_screen):

        if self.curr_frame < len(self.animation_frames) -1:
            self.curr_frame += 0.17
        else:
            self.curr_frame = 0

        # Flip the frame if moving left
        frame = self.animation_frames[int(self.curr_frame)]
        if self.flip_animation:
            frame = pygame.transform.flip(self.animation_frames[int(self.curr_frame)], True, False)  # Flip horizontally
        game_screen.blit(frame, (self.rect.x - 8, self.rect.y - 12))

    def draw(self, game_screen, player_pos, handler, enemy_name_tag):
        # Draws the enemy onto the screen
        #pygame.draw.rect(game_screen, self.enemy_colour, self.rect)
        self.animations(game_screen)
        # Draws the path of lines the enemy is following
        if handler.game_settings.settings["debug_settings"]["draw_enemy_line_path"]:
            self.draw_path_lines(game_screen, player_pos)
        # Draws the path of tiles the enemy is following
        if handler.game_settings.settings["debug_settings"]["draw_enemy_block_path"]:
            self.draw_path_rects(game_screen)
        if handler.game_settings.settings["gameplay_settings"]["display_name_tags"]:
            # Draws the text onto the screen
            game_screen.blit(enemy_name_tag, (self.rect.x - 8, self.rect.y - 16))
        

    def update(self, current_level: list[list[int]], player_pos: list[int], dt) -> None:
        """
        Updates the enemy's position, moves the enemy and creates the initial path.
        
        Args:
            current_level: The current level's grid.
            player_pos: The player's position in the grid.
            dt: Delta time used to keep movement updates smooth.
        """

        # Check if there is a path available to follow
        if len(self.current_path) >= 1:
            # Move the enemy along the path and update position
            self.move(dt)
            self.update_pos()
            # Check if the enemy has reached the next path
            if self.current_path[0] == (int(self.enemy_array_pos[0]), int(self.enemy_array_pos[1])):
                self.current_path.remove(self.current_path[0])

        else:
            # No path available, so update the position and recalculate the path
            self.update_pos()
            # Set player's last position to a different value so the path is calculated
            self.last_player_pos = [0,0]
            self.run_a_star(current_level, player_pos, [])