import pygame


class Dropdown:
    def __init__(self,
                 x,
                 y,
                 width,
                 height,
                 options,
                 name,
                 description,
                 value,
                 font_size=25,
                 font=None,
                 text_colour=(255, 255, 255),
                 button_colour=(205, 205, 205),
                 hover_colour=(155, 155, 155),
                 outline_colour=(50, 50, 50),
                 border_radius=15):

        self.name = name
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options

        self.is_open = False
        self.text_colour = text_colour
        self.button_colour = button_colour
        self.hover_colour = hover_colour
        self.outline_colour = outline_colour
        self.border_radius = border_radius

        self.font = pygame.font.SysFont(font, font_size)
        self.option_height = height
        self.hovered_index = -1
        self.hover = False
        self.width = width
        self.height = height
        self.description = description
        self.value = value
        self.selected_index = self.options.index(self.value)

    def handle_events(self, event):
        """Handles events for the dropdown."""

        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self.hover = True
        else:
            self.hover = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_open = not self.is_open

            elif self.is_open:
                for i, option_rect in enumerate(self.get_option_rects()):
                    if option_rect.collidepoint(event.pos):
                        self.selected_index = i
                        self.value = self.options[i]
                        self.is_open = False
                        break

                self.is_open = False


    def update(self):
        pass

    def get_option_rects(self):
        """Gets the rects for each dropdown option, and also the bounding rect around all options."""
        rects = []
        selected_index = self.selected_index  # Assuming this is the index of the selected option

        # Variables to track the min and max x and y coordinates for the bounding rect
        min_x = self.rect.x
        max_x = self.rect.x + self.rect.width
        min_y = self.rect.y
        max_y = self.rect.y

        for i, _ in enumerate(self.options):
            # Calculate the position for each option based on the selected index
            if i < selected_index:
                option_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.y - (self.option_height * (selected_index - i)),
                    self.rect.width,
                    self.option_height
                )
            elif i == selected_index:
                option_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.y,
                    self.rect.width,
                    self.option_height
                )
            else:
                option_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.y + self.option_height * (i - selected_index),
                    self.rect.width,
                    self.option_height
                )

            rects.append(option_rect)

            # Update the min and max x and y values to form the bounding rect
            min_x = min(min_x, option_rect.x)
            max_x = max(max_x, option_rect.x + option_rect.width)
            min_y = min(min_y, option_rect.y)
            max_y = max(max_y, option_rect.y + option_rect.height)

        # Create the bounding rect that encompasses all options
        self.bounding_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)


        return rects

    def draw(self, screen):
        """Draws the dropdown menu."""
        # Draw the main button
        pygame.draw.rect(screen, self.button_colour, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(screen, self.outline_colour, self.rect, width=2, border_radius=self.border_radius)

        text_surface = self.font.render(self.options[self.selected_index], True, self.text_colour)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

        text_surface = self.font.render(self.name, True, self.text_colour)
        text_rect = text_surface.get_rect(center=(self.rect.x-self.width//2-200, self.rect.y+self.height//2))
        screen.blit(text_surface, text_rect)

        if self.is_open:
            option_rects = self.get_option_rects()
            # Draw the bounding rect
            pygame.draw.rect(screen, self.button_colour, self.bounding_rect, border_radius=self.border_radius)

            for i, option_rect in enumerate(option_rects):

                if option_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(screen, self.hover_colour, option_rect, border_radius=self.border_radius)
                else:
                    pygame.draw.rect(screen, self.button_colour, option_rect, border_radius=self.border_radius)


                option_text = self.font.render(self.options[i], True, self.text_colour)
                option_text_rect = option_text.get_rect(center=option_rect.center)
                screen.blit(option_text, option_text_rect)
            # Bounding rect outline
            pygame.draw.rect(screen, self.outline_colour, self.bounding_rect, border_radius=self.border_radius, width=2)


