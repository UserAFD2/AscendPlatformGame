import pygame
import os

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


class Door:
    def __init__(self, pos, scale):
        self.width, self.height = 128*scale[0], 140*scale[1]
        self.curr_frame = 0
        self.curr_animation = "DoorClosed"
        self.surface = pygame.Surface((self.width, self.height))
        self.pos = pygame.Vector2(pos[0]*30*scale[0]-self.width/2.5, pos[1]*30*scale[1]-self.height/1.65)
        self.rect = pygame.Rect(self.pos.x+self.width/2.3, self.pos.y, self.width/7, self.height)
        self.animation_dict = load_animations("assets/sprites/mechanical_door", (self.width, self.height))
        self.open = False
        self.open_door = False

    def animations(self, screen):
        if self.curr_frame < len(self.animation_dict[self.curr_animation]) -1:
            self.curr_frame += 0.3
        else:
            if self.curr_animation == "DoorOpen":
                self.open = True
                self.curr_animation = "DoorOpened"
                self.curr_frame = 0
            else:
                self.curr_frame = 0

        frame = self.animation_dict[self.curr_animation][int(self.curr_frame)]
        screen.blit(frame, (self.pos.x, self.pos.y))

    def update(self, lever):
        if lever.on and not self.open:
            self.open_door = True
        if self.open_door and not self.open:
            self.curr_animation = "DoorOpen"
            self.open_door = False

class Lever:
    def __init__(self, pos, scale):
        self.width, self.height = 90*scale[0], 90*scale[1]
        self.curr_frame = 0
        self.curr_animation = "LeverOff"
        self.surface = pygame.Surface((self.width, self.height))
        self.pos = pygame.Vector2(pos[3][0]*30*scale[0]-self.width/2.5, pos[3][1]*30*scale[1]-self.height/2.5)
        self.rect = pygame.Rect(self.pos.x-self.width/2.5, self.pos.y, self.width*2, self.height)
        self.animation_dict = load_animations("assets/sprites/lever", (self.width, self.height))
        self.on = False
        self.turn_on = False
        self.turn_off = False


    def animations(self, screen):
        if self.curr_frame < len(self.animation_dict[self.curr_animation]) -1:
            self.curr_frame += 0.5
        else:
            if self.curr_animation == "TurnOn":
                self.on = True
                self.curr_animation = "LeverOn"
                self.curr_frame = 0

            elif self.curr_animation == "TurnOff":
                self.on = False
                self.curr_animation = "LeverOff"
                self.curr_frame = 0
            else:
                self.curr_frame = 0

        frame = self.animation_dict[self.curr_animation][int(self.curr_frame)]
        screen.blit(frame, (self.pos.x, self.pos.y))

    def update(self):
        if self.turn_on and not self.on:
            self.curr_frame = 0
            self.curr_animation = "TurnOn"
            self.turn_on = False

        elif self.turn_off and self.on:
            self.curr_frame = 0
            self.curr_animation = "TurnOff"
            self.turn_off = False

class LaserDoor:
    def __init__(self, pos, scale):
        self.width, self.height = 128*scale[0], 140*scale[1]
        self.curr_frame = 0
        self.curr_animation = "LaserActivate"
        self.surface = pygame.Surface((self.width, self.height))
        self.pos = pygame.Vector2(pos[0]*30*scale[0]-self.width/2.5, pos[1]*30*scale[1]-self.height/1.65)
        self.rect = pygame.Rect(self.pos.x+self.width/2.3, self.pos.y, self.width/6, self.height)
        self.animation_dict = load_animations("assets/sprites/laser_door", (self.width, self.height))
        self.open = False
        self.switch_state = False

    def animations(self, screen):
        if self.curr_frame < len(self.animation_dict[self.curr_animation]) -1:
            self.curr_frame += 0.3
        else:
            if self.curr_animation == "LaserDeactivate":
                self.open = False
                self.curr_animation = "LaserDeactivated"
                self.curr_frame = 0
            elif self.curr_animation == "LaserActivate":
                self.open = True
                self.curr_animation = "LaserActivated"
                self.curr_frame = 0
            else:
                self.curr_frame = 0

        frame = self.animation_dict[self.curr_animation][int(self.curr_frame)]
        screen.blit(frame, (self.pos.x, self.pos.y))
        if self.open or self.curr_animation == "LaserActivate":
            pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)
        else:
            pygame.draw.rect(screen, (0,255,0), self.rect, 2)

    def update(self, lever):
        #if lever.on and not self.open:
        #    self.open_door = True
        if self.switch_state and self.open:
            self.curr_animation = "LaserDeactivate"
            self.switch_state = False
        elif self.switch_state and not self.open:
            self.curr_animation = "LaserActivate"
            self.switch_state = False
