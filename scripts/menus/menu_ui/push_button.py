import pygame

class PushButton:
    def __init__(self,
                 width=100,
                 height=30,
                 x=250,
                 y=300,
                 max_font_size=50,
                 min_font_size=10,
                 text="PRESS ME",
                 font="Arial",
                 callback=None,
                 border_radius=None,
                 text_colour=(255, 255, 255),
                 button_colour=(205, 205, 205),
                 hover_colour=(155, 155, 155),
                 pressed_colour=(75, 75, 75),
                 outline_colour=(50, 50, 50),
                 shadow_colour=(50,50,50)) -> None:

        # Colours
        self.button_colour = button_colour
        self.hover_colour = hover_colour
        self.pressed_colour = pressed_colour
        self.outline_colour = outline_colour
        self.shadow_colour = shadow_colour
        # Button properties
        self.button_width = width
        self.button_height = height
        self.rect = pygame.Rect(x, y, width, height)  # Pill-shaped switch
        if border_radius is None:
            self.circle_radius = self.button_height // 2
        else:
            self.circle_radius = border_radius

        # Toggle state
        self.pressed = False
        self.hover = False
        self.text = text
        self.callback = callback

        # Font and padding
        padding = 5
        font_size = max_font_size
        self.font = pygame.font.SysFont(font, font_size)  # Use the default font



        while font_size > min_font_size:
            text_width, text_height = self.font.size(self.text)
            if text_width + padding * 2 <= self.button_width and text_height + padding * 2 <= self.button_height:
                break
            font_size -= 1
            self.font = pygame.font.SysFont(font, font_size)

        self.text_colour = text_colour

    def handle_events(self, event, sound=None):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if sound is not None:
                    sound.play()
                if self.callback:
                    self.callback()
        elif self.rect.collidepoint(pygame.mouse.get_pos()):
            self.hover = True
        else:
            self.hover = False

    def draw(self, screen):
        if self.shadow_colour is not None:
            # Draw the pill-shaped switch
            pygame.draw.rect(screen, self.shadow_colour, (self.rect.x, self.rect.y, self.button_width + 5, self.button_height + 5), 7, border_radius=self.circle_radius+5)
        if self.pressed:
            # Draw the pill-shaped switch
            pygame.draw.rect(screen, self.pressed_colour, self.rect, border_radius=self.circle_radius)

            if self.outline_colour is not None:
                # Draw the outline
                pygame.draw.rect(screen, self.outline_colour, self.rect, width=2, border_radius=self.circle_radius)

            text_surface = self.font.render(self.text, True, self.text_colour)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, (text_rect.x, text_rect.y))
        elif self.hover:
            # Draw the pill-shaped switch
            pygame.draw.rect(screen, self.hover_colour, self.rect, border_radius=self.circle_radius)

            if self.outline_colour is not None:
                # Draw the outline
                pygame.draw.rect(screen, self.outline_colour, self.rect, width=2, border_radius=self.circle_radius)

            text_surface = self.font.render(self.text, True, self.text_colour)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, (text_rect.x, text_rect.y))

        else:
            # Draw the pill-shaped switch
            pygame.draw.rect(screen, self.button_colour, self.rect, border_radius=self.circle_radius)

            if self.shadow_colour is not None:
                # Draw the outline
                pygame.draw.rect(screen, self.outline_colour, self.rect, width=2, border_radius=self.circle_radius)

            text_surface = self.font.render(self.text, True, self.text_colour)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, (text_rect.x, text_rect.y))