from typing import Optional, Callable
import pygame
from scripts.utils.game_utils import RGB


class Slider:
    def __init__(self,
                 width: int = 200,
                 height: int = 30,
                 x_position: int = 400,
                 y_position: int = 300,
                 font_name: str = None,
                 font_size: int = 25,
                 variable_text: str = "Variable",
                 min_value: int = 0,
                 max_value: int = 100,
                 initial_value: int = 50,
                 text_colour: RGB = (255, 255, 255),
                 description: str = "This is just a test description.",
                 knob_speed: int = 4,
                 get_value: Optional[Callable[[], int]] = None,
                 set_value: Optional[Callable[[int], None]] = None,
                 slider_colour: RGB = (100, 100, 100),
                 knob_colour: RGB = (255, 255, 255),
                 outline_colour: RGB = None,
                 hover_colour: Optional[RGB] = None,
                 hover_slider_colour: Optional[RGB] = None,
                 hover_area_colour: Optional[RGB] = None) -> None:

        """
        Initializes a Slider object.
        """

        # Colour properties
        self._initialise_colours(
            slider_colour,
            knob_colour,
            outline_colour,
            hover_colour,
            hover_slider_colour,
            hover_area_colour
        )

        # Slider properties (dimensions and positioning)
        self._initialise_dimensions(
            width,
            height,
            x_position,
            y_position,
            min_value,
            max_value,
            initial_value,
            knob_speed
        )

        # Text properties
        self._initialise_text(
            variable_text,
            text_colour,
            description,
            font_name,
            font_size
        )

        # Value handlers
        self._initialise_value_handlers(
            get_value,
            set_value
        )

        # Hover states
        self._initialise_hover_state()

    def _initialise_colours(self,
                            slider_colour: RGB,
                            knob_colour: RGB,
                            outline_colour: RGB,
                            hover_colour: RGB,
                            hover_slider_colour: RGB,
                            hover_area_colour: RGB) -> None:
        """
        Initialises the colour-related properties of the slider.

        Args:

            slider_colour (tuple[int, int, int]): Colour of the slider bar.
            knob_colour (tuple[int, int, int]): Colour of the knob.
            outline_colour (tuple[int, int, int]): Colour of the slider's outline.
            hover_colour (tuple[int, int, int]): Colour when hovering over the slider.
            hover_slider_colour (tuple[int, int, int]): Colour of the slider when hovered.
            hover_area_colour (tuple[int, int, int]): Colour of the hover area.
        """

        self.slider_colour = slider_colour
        self.knob_colour = knob_colour
        self.outline_colour = outline_colour
        self.hover_colour = hover_colour
        self.hover_slider_colour = hover_slider_colour
        self.hover_area_colour = hover_area_colour

    def _initialise_dimensions(self,
                               width: int,
                               height: int,
                               x_position: int,
                               y_position: int,
                               min_value: int,
                               max_value: int,
                               initial_value: int,
                               knob_speed: int) -> None:
        """
        Initialise slider dimensions and positioning.

        Args:
            width (int): Width of the slider.
            height (int): Height of the slider.
            x_position (int): X-coordinate of the slider's position.
            y_position (int): Y-coordinate of the slider's position.
            min_value (int): Minimum value of the slider.
            max_value (int): Maximum value of the slider.
            initial_value (int): Starting value of the slider.
            knob_speed (int): Speed of the knob's movement.
        """

        self.slider_width = width
        self.slider_height = height
        self.knob_speed = knob_speed
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value

        # Slider Rectangles
        self.rect = pygame.Rect(x_position, y_position - height // 2, width, height)
        self.select_area_rect = pygame.Rect(x_position, y_position - height * 3 // 2, width + 3, height * 3)
        self.knob_rect = pygame.Rect(
            x_position + (initial_value - min_value) / (max_value - min_value) * width,
            y_position - (height * 3) // 2,
            height * 3,
            height * 3
        )
        self.outside_rect = pygame.Rect(x_position - width * 1.5, y_position - height * 5 // 2, width * 3, height * 5)

    def _initialise_text(self,
                        variable_text: str,
                        text_colour: RGB,
                        description: str,
                        font_name: str,
                        font_size: int) -> None:

        """
        Initialise text-related properties.

        Args:
            variable_text (str): Label text for the slider.
            text_colour (tuple[int, int, int]): Colour of the label text.
            description (str): Description of the slider's purpose.
            font_name (str): Name of the font to use.
            font_size (int): Font size for text.
        """

        self.variable_text = variable_text
        self.text_colour = text_colour
        self.description = description
        self.font = pygame.font.SysFont(font_name, font_size)

    def _initialise_value_handlers(self, get_value, set_value) -> None:
        """
        Initialise getter and setter for the slider's value.

        Args:
            get_value (Callable[[], int]): Function to get the slider's value.
            set_value (Callable[[int], None]): Function to set the slider's value.
        """
        self.get_value = get_value or (lambda: self.value)
        self.set_value = set_value or (lambda value: setattr(self, "value", value))

    def _initialise_hover_state(self):
        """
        Initialise hover state tracking.
        """
        self.is_hovering_slider = False
        self.is_hovering_area = False

    def handle_events(self):
        """Handle events like mouse interactions."""
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()

        # Update hover states
        self.is_hovering_slider = self.select_area_rect.collidepoint(mouse_pos)
        self.is_hovering_area = self.outside_rect.collidepoint(mouse_pos)

        # Handle left mouse button interaction
        if mouse_buttons[0] and self.is_hovering_slider:
            # Calculate the relative mouse position within the slider
            relative_x = mouse_pos[0] - self.rect.x

            # Clamp the knob position to stay within slider bounds
            knob_width = self.knob_rect.width
            knob_x = max(self.rect.x, min(mouse_pos[0] - knob_width // 2, self.rect.x + self.slider_width - knob_width))
            self.knob_rect.x = knob_x

            # Calculate the new value based on relative position
            new_value = self.min_value + (relative_x / self.slider_width) * (self.max_value - self.min_value)

            # Update the value only if it has changed
            current_value = self.get_value()
            if int(new_value) != current_value:
                self.set_value(int(new_value))

    def _draw_hover_effect(self, screen):
        """Draw hover effect."""
        if self.is_hovering_slider and self.hover_colour:
            pygame.draw.rect(screen, self.hover_colour, self.rect, border_radius=15)

    def _draw_knob(self, screen):
        """Draw the knob."""
        knob_colour = self.hover_colour if self.is_hovering_slider else self.knob_colour
        pygame.draw.ellipse(screen, knob_colour, self.knob_rect)

    def _draw_text(self, screen):
        """Render and draw the text."""
        # Define the texts and their respective positions
        texts = [
            (f"{self.get_value()}", self.rect.x + self.slider_width + 20),
            (self.variable_text, self.rect.x - self.slider_width - 55),
        ]

        # Render and draw each text
        for text, x_position in texts:
            text_surface = self.font.render(text, True, self.text_colour)
            y_position = self.rect.y + (self.slider_height - text_surface.get_height()) // 2
            screen.blit(text_surface, (x_position, y_position))

    def draw(self, screen):
        """Draw the slider and its components."""

        # Determine the slider color based on hover state
        slider_colour = self.hover_slider_colour if self.is_hovering_slider else self.slider_colour

        # Draw hover effect if there is one
        self._draw_hover_effect(screen)

        # Draw the hover area background (if hovering)
        if self.is_hovering_area:
            pygame.draw.rect(screen, self.hover_area_colour, self.outside_rect, border_radius=15)

        # Draw the slider background
        pygame.draw.rect(screen, slider_colour, self.rect, border_radius=15)

        # Draw the slider outline (if an outline color is set)
        if self.outline_colour:
            pygame.draw.rect(screen, self.outline_colour, self.rect, width=3, border_radius=15)

        # Draw the knob
        self._draw_knob(screen)

        # Draw the value number and variable text
        self._draw_text(screen)

