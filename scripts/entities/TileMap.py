# Importing the Pygame module
from typing import Union, Tuple

import pygame
import pytmx
from pygame import Surface
from pygame.sprite import AbstractGroup
from pytmx.util_pygame import load_pygame

# Initialise Pygame
pygame.init()

class Tile(pygame.sprite.Sprite):
    def __init__(self,
                 pos: Tuple[int, int],
                 surf: Surface,
                 groups: Union[AbstractGroup, Tuple[AbstractGroup, ...]],
                 scale: float = 1.875,
                 stretched: bool = False) -> None:

        """
        Initialises a Tile object.

        Args:
            pos: Tuple[int, int]. Position to place the tile (top-left corner).
            surf: Surface. The image for the tile.
            groups: Union[AbstractGroup, Tuple[AbstractGroup, ...]]. The sprite group the tile belongs to.
            scale: float. Scale factor for the tile. Default is 1 (no scaling).
        """

        # Calls the __init__ method of the parent class (pygame.sprite.Sprite)
        # to ensure the sprite is correctly initialised and added to the groups.
        super().__init__(groups)
        # Original image
        self.original_image = surf
        # Scale factor
        self.scale = scale
        # Update the image with the new scale
        self.image = self.update_image()
        if self.image is not None:
            self.draw = True
            # Images rect
            self.rect = self.image.get_rect(topleft=pos)
        else:
            self.draw = False



    def update_image(self):
        """
        Updates the image of the tile by scaling it up by the scale factor.

        Returns: Scaled image

        """
        # Gets the width and height once they are multiplied by the scale factor
        if self.original_image is not None:
            scaled_size = (
                int(self.original_image.get_width() * self.scale),
                int(self.original_image.get_height() * self.scale)
            )
            # Scales the image up with the new size of the image
            self.image = pygame.transform.scale(self.original_image, scaled_size)
            # Returns the new scaled image
            return self.image
        return self.original_image

    def draw(self, screen: Surface) -> None:
        """
        Draws the tile image on the screen.

        Args:
            screen: The pygame window to display the image on.
        """
        screen.blit(self.image, self.rect.topleft)


def process_layer(tmx_data, layer_name, group, scale, stretched):
    layer = tmx_data.get_layer_by_name(layer_name)
    if hasattr(layer, "tiles"):
        for x, y, surf in layer.tiles():
            pos = (x * 16 * scale, y * 16 * scale)  # Scale position
            Tile(pos=pos, surf=surf, groups=group, scale=scale, stretched=stretched)

from dataclasses import dataclass

@dataclass
class TileMapData:
    bg_layer_2: any
    bg_layer_1: any
    mechanical_door: any
    sword_position: any
    enemies_position: any
    ladders: any
    wall_jump: any
    tiles: any
    background_group: any

def load_scaled_tile_map(game_screen,
                         tile_map: str = "",
                         scale: int = 1.875,
                         size_scale_x:int = 1,
                         size_scale_y: int = 1) -> TileMapData:
    """
    Load a scaled tile map from a .tmx file and create sprite groups for tiles and ladders.

    This function loads a .tmx tile map file, scales the tile positions and surfaces,
    and organizes them into two separate sprite groups: one for regular tiles and one for ladders.

    Args:
        size_scale_y:
        size_scale_x:
        size_scale:
        tile_map (str): The file path to the .tmx tile map file.
        scale (int): The scaling factor for the tile positions and sizes. Defaults to 1 (no scaling).

    Returns:
        Tuple[pygame.sprite.Group, ...]:
            A tuple containing multiple sprite groups:
                - The first group contains all the first layer background tiles.
                - The second group contains all the second layer background tiles.
                - The third group contains all the regular tiles.
                - The second group contains all the ladder tiles.
    """
    # Ensure the aspect ratio scaling doesn't stretch the resolution, maintain bars
    screen_width, screen_height = game_screen.get_width(), game_screen.get_height()
    target_aspect_ratio = 16 / 9  # Your target aspect ratio
    current_aspect_ratio = screen_width / screen_height
    stretched = True if target_aspect_ratio != current_aspect_ratio else False


    size_scale = [size_scale_x, size_scale_y]

    # Determine the scale factors based on aspect ratios
    if current_aspect_ratio > target_aspect_ratio:  # Wider screen (16:10 or similar)
        # Calculate scale for x and adjust y
        size_scale[0] = (screen_height / (screen_width / target_aspect_ratio))  # Scale y based on x
    else:  # Taller screen (less than 16:9)
        # Calculate scale for y and adjust x
        size_scale[1] = (screen_width / (screen_height * target_aspect_ratio))  # Scale x based on y

    # Scale the tile map based on the calculated size_scale
    scaled_size = [scale * size_scale[0], scale * size_scale[1]]

    # Loads the tmx file
    tmx_data = load_pygame(tile_map)

    # Creates an empty sprite groups
    bg2_tile_group = pygame.sprite.Group()
    bg1_tile_group = pygame.sprite.Group()
    mechanical_door_group = pygame.sprite.Group()
    sword_group = pygame.sprite.Group()
    enemies_group = pygame.sprite.Group()
    ladder_group = pygame.sprite.Group()
    wall_jump_group = pygame.sprite.Group()
    tile_group = pygame.sprite.Group()
    background_group = pygame.sprite.Group()

    # Process each layer
    process_layer(tmx_data, "bg2", bg2_tile_group, scaled_size[0], stretched)
    process_layer(tmx_data, "bg1", bg1_tile_group, scaled_size[0], stretched)
    process_layer(tmx_data, "mechanical_door", mechanical_door_group, scaled_size[0], stretched)
    process_layer(tmx_data, "sword", sword_group, scaled_size[0], stretched)
    process_layer(tmx_data, "enemies", enemies_group, scaled_size[0], stretched)
    process_layer(tmx_data, "ladders", ladder_group, scaled_size[0],stretched)
    process_layer(tmx_data, "wall_jump", wall_jump_group, scaled_size[0], stretched)
    process_layer(tmx_data, "tiles", tile_group, scaled_size[0], stretched)
    process_layer(tmx_data, "background", background_group, scaled_size[0], stretched)

    layers = bg2_tile_group, bg1_tile_group, mechanical_door_group, sword_group, enemies_group, ladder_group, wall_jump_group, tile_group, background_group
    # Returns the group of tiles
    return TileMapData(*layers), stretched


def get_layer_positions(tmx_data, layer_name, width_x, width_y):
    if isinstance(tmx_data, str):
        tmx_data = pytmx.TiledMap(tmx_data)

    try:
        layer = tmx_data.get_layer_by_name(layer_name)
    except KeyError:
        raise ValueError(f"Layer '{layer_name}' not found in the .tmx file.")

    positions = []
    for x, y, tile in layer.tiles():
        positions.append((x * width_x, y * width_y))

    return positions

def load_tmx_to_array(file_path):
    """
    Load a TMX file and convert its first tile layer into a 2D array.

    Args:
        file_path (str): Path to the TMX file.

    Returns:
        list[list[int]]: A 2D array where `1` represents a tile and `0` represents empty space.

    Raises:
        TypeError: If the first layer is not a valid Tile Layer.
    """

    # Load the TMX map from the specified file
    tmx_data = pytmx.TiledMap(file_path)

    # Access the first layer in the TMX file
    layer = tmx_data.layers[1]

    # Ensure the layer is a tile layer
    if isinstance(layer, pytmx.TiledTileLayer):
        map_array = []  # Initialize the 2D array

        # Iterate through rows (y-coordinates)
        for y in range(layer.height):
            row = []  # Create a new row

            # Iterate through columns (x-coordinates)
            for x in range(layer.width):
                # Retrieve the tile's GID (Global ID)
                gid = layer.data[y][x]

                # Add 1 for tiles and 0 for empty spaces
                row.append(1 if gid != 0 else 0)

            # Add the completed row to the map array
            map_array.append(row)

        return map_array
    else:
        raise TypeError("The first layer is not a valid Tile Layer.")
