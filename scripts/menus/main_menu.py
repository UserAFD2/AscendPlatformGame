import pygame
from scripts.menus.menu_ui.push_button import PushButton
from scripts.utils.game_utils import quit_game, create_text
pygame.mixer.init()


class MainMenu:
    def __init__(self, game_screen: pygame.Surface, handler) -> None:
        self.game_screen = game_screen
        self.handler = handler


        self.x, self.y = game_screen.get_width(), game_screen.get_height()
        self.org_x, self.org_y = 1920, 1080
        self.scale_x, self.scale_y = self.x / self.org_x, self.y / self.org_y

        self.surf = pygame.Surface((self.x, self.y))
        self.surf.fill((50,50,50))
        # Button configurations and callbacks
        self.create_buttons()
        self.running = False
        self.colour = (220, 240, 255)

        self.click_sound = pygame.mixer.Sound(r"assets\audio\button_click.mp3")

        self.highscore = 0

    def rect_scale(self, x, y, w, h):
        return x * self.scale_x, y * self.scale_y, w * self.scale_x, h * self.scale_y

    def create_buttons(self) -> None:
        # Button configurations and callbacks
        self.button_config = {
            "width": int(180 * self.scale_x),
            "height": int(60 * self.scale_y),
            "button_colour": (180, 180, 180),
            "hover_colour": (130, 130, 130),
            "pressed_colour": (100, 100, 100),
            "outline_colour": (50, 50, 50),
            "text_colour": (255, 255, 255)
        }

        self.buttons_data = [
            {"x": self.x // 2 - self.button_config["width"] // 2,
             "y": self.y // 2 - self.button_config["height"] // 2 - int(70 * self.scale_y), "text": "Start",
             "callback": self.start_game},
            {"x": self.x // 2 - self.button_config["width"] // 2, "y": self.y // 2 - self.button_config["height"] // 2,
             "text": "Options", "callback": self.go_to_settings},
            {"x": self.x // 2 - self.button_config["width"] // 2,
             "y": self.y // 2 - self.button_config["height"] // 2 + int(70 * self.scale_y), "text": "Quit",
             "callback": quit_game},
        ]

        self.menu_buttons = [
            PushButton(x=data["x"], y=data["y"], text=data["text"], callback=data["callback"], **self.button_config)
            for data in self.buttons_data
        ]

    def go_to_settings(self) -> None:
        self.handler.next_menu = "settings"
        self.running = False  # Exit the current loop for transition
        return  # Exit the main function
    
    def start_game(self) -> None:
        self.handler.next_menu = "game"
        self.running = False  # Exit the current loop for transition
        return  # Exit the main function
    
    def handle_events(self, event) -> None:
        for button in self.menu_buttons:
            button.handle_events(event, self.click_sound)

    def render_glow_text(self, screen, text, font, colour, glow_colour, pos, glow_radius=10):
        # Render the glow effect
        glow_surface = pygame.Surface((font.size(text)[0] + 2*glow_radius, font.size(text)[1] + 2*glow_radius), pygame.SRCALPHA)
        for radius in range(glow_radius, 0, -2):
            alpha = int(255 * (radius / glow_radius))  # Gradually fade the glow
            glow_colour_with_alpha = (*glow_colour[:3], alpha)
            glow_font = font.render(text, True, glow_colour_with_alpha)
            glow_surface.blit(glow_font, (glow_radius - radius, glow_radius - radius))
    
        screen.blit(glow_surface, (pos[0] - glow_radius, pos[1] - glow_radius))
    
        # Render the main text
        text_surface = font.render(text, True, colour)
        screen.blit(text_surface, pos)

    def render(self) -> None:
        font = pygame.font.Font(r"assets\fonts\Agbalumo\Agbalumo-Regular.ttf", 72)
        self.render_glow_text(self.surf, "ASCEND", font, (255, 255, 255), (0, 20, 85), (500, 100))
        highscore_surf, _ = create_text(f"HIGHSCORE: {self.handler.highscore}", (255, 255, 255), 40)
        for button in self.menu_buttons:
            button.draw(self.surf)
        self.game_screen.blit(self.surf, (0, 0))
        self.game_screen.blit(highscore_surf, (self.x - 340, 40))

    def update(self) -> None:
        self.click_sound.set_volume(self.handler.volume)  # Sets the volume
        # Updates the sizes of menu elements on the screen
        if self.x != self.game_screen.get_width() or self.y != self.game_screen.get_height():
            self.x, self.y = self.game_screen.get_width(), self.game_screen.get_height()
            self.scale_x, self.scale_y = self.x / self.org_x, self.y / self.org_y
            self.create_buttons()
            self.surf = pygame.Surface((self.x, self.y))


        self.handler.game_settings.set_config("player_settings", "highscore", self.handler.highscore)
        self.handler.game_settings.set_config("player_settings", "last_5_games", self.handler.last_5_games)
        self.handler.game_settings.save_all("config\settings_saved.json")


        # Last 5 games table
        # outline_colour = (30, 50, 100)
        # pygame.draw.rect(self.surf, (30,30,30), (self.x - 350, self.y // 2 - 50, 250, 250), border_radius=10)
        # pygame.draw.rect(self.surf, (100, 150, 255), (self.x - 350 ,self.y // 2 - 50, 250, 250), border_radius=15)
        # pygame.draw.rect(self.surf, outline_colour, (self.x - 350 ,self.y // 2 - 50, 250, 250), width=4, border_radius=15)
        # # Title
        # last_5_games_surf, _ = create_text(f"LAST 5 GAMES", (255, 255, 255), 30)
        # self.surf.blit(last_5_games_surf, (self.x - 340, 100))
        # 
        # # Headers for the table
        # headers = ["Game", "Level", "Points"]
        # header_text = f"{headers[0]}   {headers[1]}   {headers[2]}"
        # header_surf, _ = create_text(header_text, (255, 255, 255), 30)
        # self.surf.blit(header_surf, (self.x - 340, self.y // 2 - 40))
        # 
        # # Draw a line under the header
        # pygame.draw.line(self.surf, outline_colour, (self.x - 350, self.y // 2 - 10), (self.x - 100, self.y // 2 - 10), 4)
        # 
        # # Get the last 5 games (reversed order)
        # last_5_games = self.handler.last_5_games[::-1]
        # 
        # # Draw the table rows and columns
        # for i in range(0, 5):
        #     
        #     y_pos = self.y // 2 + 40 * i
        # 
        # 
        #     # Format and draw each game's data in columns
        #     game_text = f"{i+1}.             {last_5_games[i][0]}        {last_5_games[i][1]}"
        #     game_surf, _ = create_text(game_text, (255, 255, 255), 30)
        #     
        #     self.surf.blit(game_surf, (self.x - 340, y_pos)) 
        #     
        #     if i != 4:
        #         pygame.draw.line(self.surf, outline_colour, (self.x - 350, y_pos + 30), (self.x - 100, y_pos + 30), 4)
        # 
        # pygame.draw.line(self.surf, outline_colour, (self.x - 275, self.y // 2 - 50), (self.x - 275, self.y // 2 + 200), 4)
        # pygame.draw.line(self.surf, outline_colour, (self.x - 200, self.y // 2 - 50), (self.x - 200, self.y // 2 + 200), 4)


