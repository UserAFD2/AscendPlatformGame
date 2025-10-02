import sys
from typing import Tuple

import pygame

# (Red, Green, Blue) Type annotation
RGB = Tuple[int, int, int]

# Colours in RGB format
WHITE: RGB = (255, 255, 255)
BLUE: RGB = (30, 144, 255)
BLACK: RGB = (0, 0, 0)


def draw_menu_background(surface, rect_scale):
    draw_styled_rect(surface, (30, 30, 30, 255), rect_scale(0, 0, 2000, 1100))
    draw_styled_rect(surface, (45, 45, 45, 255), rect_scale(0, 0, 250, 1100))
    draw_styled_rect(surface, (100, 100, 100, 255), rect_scale(0, -10, 250, 1200), width=1)
    draw_styled_rect(surface, (45, 45, 45, 255), rect_scale(1200, 0, 800, 1100))
    draw_styled_rect(surface, (100, 100, 100, 255), rect_scale(1200, -10, 800, 1200), width=1)



def draw_styled_rect(surface, color, rect, width=0, border_radius=0):
    pygame.draw.rect(surface, color, rect, width, border_radius=border_radius)

def create_text(text_str, colour, size):
    font_name = pygame.font.get_default_font()
    font_size = size
    font = pygame.font.SysFont(font_name, font_size)
    text = font.render(text_str, True, colour)
    rect = text.get_rect()
    return text, rect

def quit_game():
    # Quitting Pygame
    pygame.quit()
    # Closing the program
    sys.exit()


def update_color_value(color_value, color_value_spd):
    if 255 > color_value > 100:
        color_value += color_value_spd
    else:
        color_value_spd *= -1
        color_value += color_value_spd
    return color_value, color_value_spd