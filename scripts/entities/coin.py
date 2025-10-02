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

class Coin:
    def __init__(self, pos, scale):
        self.width, self.height = 90, 90
        self.curr_frame = 0
        self.curr_animation = "CoinSpin"
        self.surface = pygame.Surface((self.width, self.height))
        self.pos = pygame.Vector2(pos[0]*30*scale[0]-self.width/2.5, pos[1]*30*scale[1]-self.height/2.5)
        self.rect = pygame.Rect(self.pos.x+self.width/2.5, self.pos.y+self.height/2.5, self.width/4, self.height/4)
        self.animation_dict = load_animations("assets/sprites/coin", (self.width, self.height))
        self.can_pickup = True
        self.pickup = False

    def animations(self, screen, game):
        if self.curr_frame < len(self.animation_dict[self.curr_animation]) -1:
            if self.curr_animation == "CoinCollect":
                self.curr_frame += 0.5
            else:
                self.curr_frame += 0.2
        else:
            if self.curr_animation == "CoinCollect":
                game.coins_list.remove(self)
                game.points += 15
            else:
                self.curr_frame = 0


        frame = self.animation_dict[self.curr_animation][int(self.curr_frame)]
        screen.blit(frame, (self.pos.x, self.pos.y))

    def update(self):
        if self.pickup and self.can_pickup:
            self.curr_frame = 0
            self.curr_animation = "CoinCollect"
            self.can_pickup = False



