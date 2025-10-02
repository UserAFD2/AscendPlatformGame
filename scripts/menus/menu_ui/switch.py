from typing import Optional, Callable

import pygame

from scripts.utils.game_utils import RGB


class Switch:
    def __init__(self,
                 width: int = 60,
                 height: int = 30,
                 x: int = 400,
                 y: int = 300,
                 outside_rect_height=50,
                 font: pygame.font.SysFont = None,
                 font_size: int = 25,
                 variable_text: str = "Variable",
                 on_text: str = "",
                 off_text: str = "",
                 text_colour: RGB = (255, 255, 255),
                 description: str = "This is just a test description.",
                 knob_speed: int = 4,
                 get_bool: Optional[Callable[[], bool]] = False,  # Default getter
                 set_bool: Optional[Callable[[bool], None]] = None,  # Default setter
                 on_colour: RGB = (205, 205, 205),
                 off_colour: RGB = (155, 155, 155),
                 knob_on_colour: RGB = (255, 255, 255),
                 knob_off_colour: RGB = (100, 100, 100),
                 outline_colour: RGB = None,
                 hover_colour = None,
                 outside_rect_shadow_colour = None,
                 outside_rect_colour = None) -> None:

        """
        Initializes a Switch object.

        Args:

            font (pygame.font.Font): Font used to render text.
            variable_text (str): Text displayed on the switch.
            text_colour (tuple[int, int, int]): Colour of the text.

            get_bool (Callable[[], bool]): Function to get the state of the switch.
            set_bool (Callable[[bool], None]): Function to set the state of the switch.


        """

        # Colour properties
        self._initialise_colours(
            on_colour,
            off_colour,
            knob_on_colour,
            knob_off_colour,
            outline_colour,
            hover_colour,
            outside_rect_colour,
            outside_rect_shadow_colour
        )

        # Knob and Switch properties
        self._initialise_properties(
            x,
            y,
            width,
            height,
            knob_speed,
            outside_rect_height
        )

        # Toggle state
        self.get_bool = get_bool or (lambda: False)
        self.set_bool = set_bool or (lambda value: None)
        self.on_text = on_text
        self.off_text = off_text
        self.text = self.off_text
        self.text_colour = text_colour
        self.variable_text = variable_text
        self.locked = False
        self.hover = False
        self.description = description
        self.font = pygame.font.SysFont(font, font_size)
        self.font_type = font
        self.knob_font = pygame.font.SysFont(font, font_size)
        self.knob_font_size = font_size
        self.min_font_size = 1
        self.padding = 5
        while self.knob_font_size > self.min_font_size:
            text_width, text_height = self.knob_font.size(self.text)
            if text_width + self.padding * 2 <= self.switch_height and text_height + self.padding * 2 <= self.switch_height:
                break
            self.knob_font_size -= 1
            self.knob_font = pygame.font.SysFont(self.font_type, self.knob_font_size)


    def _initialise_colours(self,
                            on_colour: RGB,
                            off_colour: RGB,
                            knob_on_colour: RGB,
                            knob_off_colour: RGB,
                            outline_colour: RGB,
                            hover_colour: RGB,
                            outside_rect_colour: RGB,
                            outside_rect_shadow_colour: RGB) -> None:

        """
        Initialises the colour-related properties of the slider.

        Args:
            on_colour (tuple[int, int, int]): Colour of the switch when on.
            off_colour (tuple[int, int, int]): Colour of the switch when off.
            knob_on_colour (tuple[int, int, int]): Colour of the knob when on.
            knob_off_colour (tuple[int, int, int]): Colour of the knob when off.
            outline_colour (tuple[int, int, int]): Colour of the outline of the switch.
            hover_colour (tuple[int, int, int]): Colour change during hover.
            outside_rect_colour (tuple[int, int, int]): Colour of the outside area.
            outside_rect_shadow_colour (tuple[int, int, int]): Colour of the shadow of the outside area.
        """

        self.on_colour = on_colour
        self.off_colour = off_colour
        self.knob_on_colour = knob_on_colour
        self.knob_off_colour = knob_off_colour
        self.outline_colour = outline_colour
        self.hover_colour = hover_colour
        self.outside_rect_colour = outside_rect_colour
        self.outside_rect_shadow_colour = outside_rect_shadow_colour

    def _initialise_properties(self,
                               x: int,
                               y: int,
                               width: int,
                               height: int,
                               knob_speed: int,
                               outside_rect_height: int) -> None:

        """
        Initialises the properties of the switch and knob.

        Args:
            x (int): X-coordinate of the switch position.
            y (int): Y-coordinate of the switch position.
            width (int): Width of the switch.
            height (int): Height of the switch.
            knob_speed (int): Speed at which the knob moves.
            outside_rect_height (int): Height of the outside rectangle.

        Returns:

        """

        # Switch properties
        self.switch_width = width
        self.switch_height = height
        self.outside_rect_height = outside_rect_height
        self.rect = pygame.Rect(x, y, width, height)  # Pill-shaped switch
        self.outside_rect = pygame.Rect(x-width*5.25, y-5, width*7, self.outside_rect_height)
        self.outside_rect_shadow = pygame.Rect(x - width * 4.75 + 3, y - height * 0.25 + 3, width * 7 + 3, height * 1.5 + 3)
        self.circle_radius = self.switch_height // 2

        # Knob properties
        self.knob_rect = pygame.Rect(self.rect.x + 6, self.rect.y + 3, self.circle_radius * 2 - 6, self.circle_radius * 2 - 6)
        self.knob_speed = knob_speed  # Speed of knob movement

    def update(self):
        # Smoothly move the knob
        if self.get_bool():
            target_x = self.rect.x + self.switch_width - self.circle_radius * 2   # Rightmost position
            if self.knob_rect.x < target_x:
                self.knob_rect.x += self.knob_speed
        else:
            target_x = self.rect.x + 6  # Leftmost position
            if self.knob_rect.x > target_x:
                self.knob_rect.x -= self.knob_speed

    def handle_events(self, event, sound=None):
        mouse_pos = pygame.mouse.get_pos()
        if self.outside_rect.collidepoint(mouse_pos):
            self.hover = True
        else:
            self.hover = False
        if not self.locked:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    if sound is not None:
                        sound.play()
                    self.set_bool(not self.get_bool())
        else:
            self.set_bool(False)

    @staticmethod
    def draw_rect(surface, color, rect, width=0, border_radius=0):
        if color:
            if surface.get_flags() & pygame.SRCALPHA:  # Check if the surface supports per-pixel alpha
                # Use RGBA colors for true transparency
                pygame.draw.rect(surface, color, rect, width, border_radius)
            else:
                # Fallback for non-alpha surfaces (e.g., RGB-only surfaces)
                pygame.draw.rect(surface, color, rect, width, border_radius)

    @staticmethod
    def draw_text(surface, text, font, color, position):
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, position)

    def _draw_shadow_or_hover(self, screen):
        """Draw the shadow or hover effect."""
        if self.hover:

            if self.hover_colour:
                self.draw_rect(screen, self.hover_colour, self.outside_rect, border_radius=15)
        else:
            self.draw_rect(screen, self.outside_rect_shadow_colour, self.outside_rect_shadow, width=15,
                           border_radius=15)
            self.draw_rect(screen, self.outside_rect_colour, self.outside_rect, border_radius=15)

    def _draw_knob(self, screen):
        """Draw the knob with a high-resolution surface."""


        # Create a high-res surface
        high_res_surface = pygame.Surface(
            ((self.circle_radius * 2 - 6) * 4, (self.circle_radius * 2 - 6) * 4),
            pygame.SRCALPHA
        )

        # Draw on the high-res surface
        pygame.draw.ellipse(
            high_res_surface,
            (self.knob_on_colour[0], self.knob_on_colour[1], self.knob_on_colour[2], 255),
            (0, 0, (self.circle_radius * 2 - 6) * 4, (self.circle_radius * 2 - 6) * 4)
        )

        # Scale down and blit to the screen
        smooth_surface = pygame.transform.smoothscale(
            high_res_surface,
            (self.circle_radius * 2 - 6, self.circle_radius * 2 - 6)
        )
        screen.blit(smooth_surface, self.knob_rect)

    def _draw_text(self, screen):
        """Update and render text."""
        self.text = self.on_text if self.get_bool() else self.off_text
        if not self.locked:
            text_position = (
                (self.knob_rect.x + 5, self.knob_rect.y + 3) if self.text == self.on_text
                else (self.knob_rect.x + 2, self.knob_rect.y + 3)
            )
            self.draw_text(screen, self.text, self.knob_font, self.text_colour, text_position)
            self.draw_text(screen, self.variable_text, self.knob_font, self.text_colour,
                           (self.rect.x - self.switch_width * 4 - 55, self.rect.y + 10))
        else:
            self.draw_text(screen, self.variable_text, self.font, (150, 150, 150),
                           (self.rect.x - self.switch_width * 4 - 55, self.rect.y + 10))

    def draw(self, screen):
        if not self.locked:
            # Draw shadow or hover effect
            self._draw_shadow_or_hover(screen)

            # Draw the switch (active or inactive based on state)
            switch_colour = self.on_colour if self.get_bool() else self.off_colour
            self.draw_rect(screen, switch_colour, self.rect, border_radius=self.circle_radius)

            # Draw the outline
            self.draw_rect(screen, self.outline_colour, self.rect, width=3, border_radius=self.circle_radius)

            # Draw the knob
            self._draw_knob(screen)

            # Update and render text
            self._draw_text(screen)

