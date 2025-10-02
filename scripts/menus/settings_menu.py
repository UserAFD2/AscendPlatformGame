import pygame
from scripts.menus.menu_ui.drop_down import Dropdown
from scripts.menus.menu_ui.push_button import PushButton
from scripts.menus.menu_ui.switch import Switch
from scripts.menus.menu_ui.slider import Slider
from scripts.utils.game_utils import create_text, draw_menu_background


class SettingsMenu:
    def __init__(self, game_screen: pygame.Surface, handler) -> None:
        self.game_screen = game_screen
        self.handler = handler

        self.x, self.y = game_screen.get_width(), game_screen.get_height()

        self.org_x, self.org_y = 1920, 1080
        self.scale_x, self.scale_y = self.x / self.org_x, self.y / self.org_y

        self.button_config = {
            "on_colour": (100, 150, 120),
            "off_colour": (100, 100, 100),
            "knob_on_colour": (255, 255, 255),
            "knob_off_colour": (255, 255, 255),
            "hover_colour": (60, 60, 60),
            "text_colour": (255, 255, 255),
            "outside_rect_height": 55*self.scale_y,
            "width": int(85 * self.scale_x),
            "height": int(45 * self.scale_y),
        }

        self.slider_config = {
            "slider_colour": (70, 70, 70),
            "knob_colour": (150, 150, 150),
            "hover_colour": (255, 255, 255),
            "hover_area_colour": (60, 60, 60),
            "hover_slider_colour": (100, 100, 100),
            "text_colour": (255, 255, 255),
            "width": int(200 * self.scale_x),
            "height": int(10 * self.scale_y),
        }

        self.settings_menu_switches = []

        # Shared states
        self._get_values()

        self._create_background_surface()
        self._create_menu_surface()

        self._create_debug_mode_switches(self.button_config)
        self._create_gameplay_switches(self.button_config)
        self._create_sound_switches(self.slider_config)
        self._create_display_settings()
        self._create_settings_tabs()
        self._create_back_button()

        self.DEBUG_MODE = "Debug Settings"
        self.GAMEPLAY = "Gameplay Settings"
        self.SOUND = "Sound Settings"
        self.DISPLAY = "Display Settings"
        self.settings_state = self.DEBUG_MODE
        self.settings_menu_switches = self.debug_mode_switches
        self.running = False
        self.click_sound = pygame.mixer.Sound(r"assets\audio\button_click.mp3")
        # Draws the menu background
        draw_menu_background(self.surf, self.rect_scale)

        self.description = ""
        self.title = ""

    def _create_background_surface(self):
        self.surf = pygame.Surface((self.x, self.y))


    def _create_menu_surface(self):
        self.menu_surf = pygame.Surface(self.scale(1120, 800), pygame.SRCALPHA)
        self.menu_surf.fill((100, 100, 200, 0))


    def _create_debug_mode_switches(self, button_config):
        self.debug_mode_switches = [
            Switch(
                x=self.x // 2 - int(150 * self.scale_x),
                y=int(200 * self.scale_y) + int(i * 55 * self.scale_y) if i <= 7 else int(150 * self.scale_y) + int(
                    (i - 8) * 50 * self.scale_y),
                font="arial",
                variable_text=text,
                get_bool=getter,
                set_bool=setter,
                description=description,
                **button_config,
            )
            for i, (text, getter, setter, description) in enumerate([  # Adjusting for scaling
                ("Debug Mode", lambda: self.debug_mode, lambda value: setattr(self, "debug_mode", value),
                 "Toggles debugging mode."),
                ("Draw Enemy Line Path", lambda: self.draw_enemy_line_path,
                 lambda value: setattr(self, "draw_enemy_line_path", value),
                 "Draws calculated path lines that the enemy is following."),
                ("Draw Enemy Block Path", lambda: self.draw_enemy_block_path,
                 lambda value: setattr(self, "draw_enemy_block_path", value),
                 "Draws calculated path tiles that the enemy is following."),
                ("Show Player Stats", lambda: self.display_player_stats,
                 lambda value: setattr(self, "display_player_stats", value), "Displays players position values."),
                ("Show Player Hitbox", lambda: self.display_player_hitbox,
                 lambda value: setattr(self, "display_player_hitbox", value),
                 "Displays the players hitbox to show what space represents the player."),
                ("Show FPS", lambda: self.display_fps, lambda value: setattr(self, "display_fps", value),
                 "Displays the frames per second."),
            ])
        ]

    def _create_gameplay_switches(self, button_config):
        self.gameplay_switches = [
            Switch(
                x=self.x // 2 - int(150 * self.scale_x),
                y=int(200 * self.scale_y) + int(i * 55 * self.scale_y) if i <= 7 else int(150 * self.scale_y) + int(
                    (i - 8) * 50 * self.scale_y),
                font="arial",
                variable_text=text,
                get_bool=getter,
                set_bool=setter,
                description=description,
                **button_config,
            )
            for i, (text, getter, setter, description) in enumerate([
                ("Display Player Sprite", lambda: self.display_player_sprite,
                 lambda value: setattr(self, "display_player_sprite", value),
                 "Displays the player's sprite onto the screen."),

                ("Show HUD (Heads Up Display)", lambda: self.display_hud,
                 lambda value: setattr(self, "display_hud", value),
                 "Displays the HUD (Heads Up Display) onto the screen."),
                
                ("Name Tags", lambda: self.display_name_tags, lambda value: setattr(self, "display_name_tags", value),
                 f"Displays the player and enemies name tags. "),
            ])
        ]

    def _create_sound_switches(self, slider_config):
        self.sound_switches = [
            Slider(
                x_position=self.x // 2 - int(250 * self.scale_x),
                y_position=int(225 * self.scale_y) + int(i * 55 * self.scale_y) if i <= 7 else int(150 * self.scale_y) + int(
                    (i - 8) * 50 * self.scale_y),
                font_name="arial",
                variable_text=text,
                initial_value=initial,
                get_value=getter,
                set_value=setter,
                description=description,
                **slider_config,
            )
            for i, (text, initial, getter, setter, description) in enumerate([
                ("Sound Volume", int(self.sound_volume), lambda: self.sound_volume, lambda value: setattr(self, 'sound_volume', value),
                 "This setting is still working in progress at the moment but it will control the volume of the game."),

            ])
        ]


    def _create_display_settings(self):
        info = pygame.display.Info()
        self.display_settings = [
            Dropdown(
                x=self.x // 2 - int(150 * self.scale_x),
                y=int(200 * self.scale_y) + int(i * 50 * self.scale_y) if i <= 7 else int(150 * self.scale_y) + int((i - 8) * 50 * self.scale_y),
                width=200,
                height=40,
                options=options,
                name=text,
                description=description,
                value=value,
                font="arial",
                button_colour=(70, 70, 70),
                outline_colour=(150, 150, 150),
            )
            for i, (text, options, description, value) in enumerate([
                ("Resolution", ["2560x1440", "2880x1800", "1920x1080", "1440x900", "1280x720", "800x600"] if self.mode == "windowed" else [f"{info.current_w}x{info.current_h}"],
                 "Changes the resolution of the game.", self.resolution),
                ("Fullscreen", ["fullscreen", "windowed"],
                 "Toggles fullscreen mode.", self.mode),
            ])
        ]
        self.display_settings = []

    def _create_settings_tabs(self):
        different_config = {
            "x": 250//2*self.scale_x - 110*self.scale_x,
            "max_font_size": 40,
            "border_radius": 10,
            "width": 220 * self.scale_x,
            "height": 40 * self.scale_y,
            "button_colour": (45, 45, 45),
            "hover_colour": (60, 60, 60),
            "pressed_colour": (80, 80, 80),
            "outline_colour": None,
            "shadow_colour": None,
            "text_colour": (255, 255, 255)
        }

        # The buttons for the settings tabs
        self.settings_tabs = [PushButton(
            y=self.y // 2 - int(340*self.scale_x), text="Debug", callback=self.select_debug_mode, **different_config
        ), PushButton(
            y=self.y // 2 - int(300*self.scale_x), text="Gameplay", callback=self.select_gameplay, **different_config
        ), PushButton(
            y=self.y // 2 - int(260*self.scale_x), text="Sound", callback=self.select_sound, **different_config,
        )]

    def _create_back_button(self):
        back_button_config = {
            "x": 250 // 2 * self.scale_x - 110 * self.scale_x,
            "max_font_size": 40,
            "border_radius": 10,
            "width": 220 * self.scale_x,
            "height": 40 * self.scale_y,
            "button_colour": (45, 45, 45),
            "hover_colour": (60, 60, 60),
            "pressed_colour": (80, 80, 80),
            "outline_colour": None,
            "shadow_colour": None,
            "text_colour": (255, 255, 255)
        }

        # The buttons for the settings tabs
        self.back_button = PushButton(
            y=self.y // 2 - int(500 * self.scale_x), text="Back", callback=self.go_to_main_menu, **back_button_config
        )

    def rect_scale(self, x, y, w, h):
        return int(x * self.scale_x), int(y * self.scale_y), int(w * self.scale_x), int(h * self.scale_y)

    def scale(self, x, y):
        return int(x * self.scale_x), int(y * self.scale_y)

    def _get_values(self):
        self.debug_mode = self.handler.game_settings.settings["debug_settings"]["debug_mode"]
        self.draw_enemy_line_path = self.handler.game_settings.settings["debug_settings"]["draw_enemy_line_path"]
        self.draw_enemy_block_path = self.handler.game_settings.settings["debug_settings"]["draw_enemy_block_path"]
        self.display_player_stats = self.handler.game_settings.settings["debug_settings"]["display_player_stats"]
        self.display_player_hitbox = self.handler.game_settings.settings["debug_settings"]["display_player_hitbox"]
        self.display_fps = self.handler.game_settings.settings["debug_settings"]["display_fps"]
        self.display_player_sprite = self.handler.game_settings.settings["gameplay_settings"]["display_player_sprite"]
        self.display_hud = self.handler.game_settings.settings["gameplay_settings"]["display_hud"]
        self.display_name_tags = self.handler.game_settings.settings["gameplay_settings"]["display_name_tags"]
        self.resolution = f"{self.handler.game_settings.settings["video_settings"]["resolution"][0]}x{self.handler.game_settings.settings["video_settings"]["resolution"][1]}"
        self.mode = self.handler.game_settings.settings["video_settings"]["mode"]
        self.sound_volume = int(float(self.handler.game_settings.settings["audio_settings"]["sound_volume"]) * 100)

    def update_shared_vars(self):
        for item in self.display_settings:
            if item.name == "Resolution":
                self.resolution = item.value
            elif item.name == "Fullscreen":
                self.mode = item.value
        resolution = [int(x) for x in self.resolution.split("x")]
        self.handler.volume = self.sound_volume / 100
        # Map settings to their categories and keys
        settings_to_update = {
                "debug_settings": {
                    "debug_mode": self.debug_mode,
                    "draw_enemy_line_path": self.draw_enemy_line_path,
                    "draw_enemy_block_path": self.draw_enemy_block_path,
                    "display_player_stats": self.display_player_stats,
                    "display_player_hitbox": self.display_player_hitbox,
                    "display_fps": self.display_fps,
                },
                "gameplay_settings": {
                    "display_player_sprite": self.display_player_sprite,
                    "display_hud": self.display_hud,
                    "display_name_tags": self.display_name_tags
                },
                "video_settings": {
                    "mode": self.mode,
                },
                "audio_settings": {
                    "sound_volume": self.sound_volume / 100,
                }
            }

        # Update settings using the set method
        for category, keys in settings_to_update.items():
            for key, value in keys.items():
                self.handler.game_settings.set_settings(category, key, value)
               


    # Locks the switches
    def lock_switches(self):
        if not self.debug_mode and self.settings_state == self.DEBUG_MODE:
            for i in range(1, len(self.settings_menu_switches)):
                self.settings_menu_switches[i].locked = True
        else:
            for i in range(1, len(self.settings_menu_switches)):
                self.settings_menu_switches[i].locked = False

    def update(self) -> None:
        
        self.click_sound.set_volume(self.handler.volume)  # Sets the volume

        if self.x != self.game_screen.get_width() or self.y != self.game_screen.get_height():
            self.x, self.y = self.game_screen.get_width(), self.game_screen.get_height()
            self.scale_x, self.scale_y = self.x / self.org_x, self.y / self.org_y

            self._create_background_surface()
            self._create_menu_surface()
            self._create_debug_mode_switches(self.button_config)
            self._create_gameplay_switches(self.button_config)
            self._create_sound_switches(self.slider_config)
            self._create_display_settings()
            self._create_settings_tabs()
            self._create_back_button()
            self.settings_menu_switches = self.debug_mode_switches
            
        # Locks unusable switches
        self.lock_switches()


    def go_to_main_menu(self) -> None:
        # Updates the shared variables
        self.update_shared_vars()
        # Overwrite the file with the updated data
        self.handler.game_settings.save_all("config/settings_saved.json")
        self.handler.game_settings.apply_settings()
        self.handler.next_menu = "main"
        self.running = False  # Exit the current loop for transition
        return  # Exit the main function

    # Selects the gameplay settings tab
    def select_gameplay(self) -> None:
        self.settings_state = self.GAMEPLAY
        self.settings_menu_switches = self.gameplay_switches

    # Selects the sound settings tab
    def select_sound(self) -> None:
        self.settings_state = self.SOUND
        self.settings_menu_switches = self.sound_switches

    # Selects the debug mode settings tab
    def select_debug_mode(self) -> None:
        self.settings_state = self.DEBUG_MODE
        self.settings_menu_switches = self.debug_mode_switches

    def select_display_settings(self) -> None:
        self.settings_state = self.DISPLAY
        self.settings_menu_switches = self.display_settings

    def handle_events(self, event) -> None:
        for button in self.settings_menu_switches:
            if isinstance(button, (Switch, PushButton)):
                button.handle_events(event, self.click_sound)
            elif isinstance(button, Slider):
                button.handle_events()
            else:
                button.handle_events(event)
        self.back_button.handle_events(event, self.click_sound)
        for item in self.settings_tabs:
            item.handle_events(event, self.click_sound)

        # Define a list where each index corresponds to the button press state
        pressed_states = [self.DEBUG_MODE, self.GAMEPLAY, self.SOUND]

        # Loop through the buttons and set their pressed state
        for i, state in enumerate(pressed_states):
            self.settings_tabs[i].pressed = (self.settings_state == state)

    @staticmethod
    def create_background_surface(size, alpha_colour):
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill(alpha_colour)
        return surf

    def update_menu_text(self):
        # Draw the menu surface and description
        if any(
                (switch.hover if isinstance(switch, Switch) else switch.is_hovering_area)
                for switch in self.settings_menu_switches
                if isinstance(switch, (Switch, Slider)) and not getattr(switch, 'locked', False)  # Check if not locked
        ):
            # Find the first switch or slider that is hovered and not locked
            hovered_switch = next(
                switch for switch in self.settings_menu_switches
                if (
                        isinstance(switch, Switch) and switch.hover and not switch.locked
                # Check if switch is hovered and not locked
                ) or (
                        isinstance(switch, Slider) and switch.is_hovering_area
                )
            )
            try:
                self.description = hovered_switch.description
                self.title = hovered_switch.variable_text
            except Exception as e:
                print(e)

    def update_menu_surface(self):
        self.menu_surf = pygame.Surface(self.scale(2000, 1100), pygame.SRCALPHA)
        self.menu_surf.fill((100, 100, 200, 0))

        tab_title, _ = create_text(self.settings_state, (255, 255, 255), int(40 * self.scale_x))
        self.menu_surf.blit(tab_title, self.scale(600, 150))

        self.update_menu_text()

        self.menu_surf.blit(create_text(self.description, (255, 255, 255), int(20 * self.scale_x))[0],self.scale(1400, 150))
        self.menu_surf.blit(create_text(self.title, (255, 255, 255), int(50 * self.scale_x))[0], self.scale(1400, 75))

        self.disabled_tab()

    def update_settings_elements(self):
        is_open_i = 0
        for i, element in enumerate(self.settings_menu_switches):
            if isinstance(element, Slider):
                self.handler.volume = self.sound_volume / 100
                element.draw(self.game_screen)

            elif isinstance(element, Switch):
                element.update()
                element.draw(self.game_screen)

        self.settings_menu_switches[is_open_i].draw(self.game_screen)

    def disabled_tab(self):
        if self.settings_state == self.DISPLAY:
            self.menu_surf.blit(
                create_text("This tab is disabled at the moment.", (255, 255, 255), int(50 * self.scale_x))[0],
                self.scale(600, 75))

    def render(self) -> None:
        self.surf = pygame.Surface((self.x, self.y))
        # Draws the menu background
        draw_menu_background(self.surf, self.rect_scale)
        # Draw background onto screen
        self.game_screen.blit(self.surf, (0, 0))

        self.update_menu_surface()

        self.update_settings_elements()

        for tab in self.settings_tabs:
            tab.draw(self.game_screen)

        self.game_screen.blit(self.menu_surf, (self.x // 2 - int(1000 * self.scale_x), int(0 * self.scale_y)))
        self.back_button.draw(self.game_screen)

