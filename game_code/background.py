import pygame
from loading_image import load_image

class Sky:
    def __init__(self, screen):
        self.screen = screen
        self.group = pygame.sprite.Group()
        self.sprite = pygame.sprite.Sprite()
        self.image = load_image('../textures/background/sky.png')
        self.sprite.image = self.image
        self.sprite.rect = self.sprite.image.get_rect()
        self.sprite.rect.left, self.sprite.rect.top = 0,0
        self.group.add(self.sprite)
        self.group.draw(screen)

    def draw(self):
        self.group.draw(self.screen)


class Mountains:
    def __init__(self, pos,screen,image):
        self.screen = screen
        self.pos = [pos,120]
        self.layer = int(image.split('.')[-2][-1])
        self.group = pygame.sprite.Group()
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = load_image(image)
        self.sprite.rect = self.sprite.image.get_rect()
        self.sprite.rect.left, self.sprite.rect.top = pos,120

        self.group.add(self.sprite)
        # self.group.draw(screen)

    def draw(self):
        self.sprite.rect.left, self.sprite.rect.top = self.pos
        self.group.draw(self.screen)