import pygame
import os
import sys
from bullet import Bullet


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class Player(pygame.sprite.Sprite):
    """ A Player Class """

    def __init__(self, size, bullet_group):
        """ Initialize the Player"""
        super().__init__()
        self.bullet_group = bullet_group
        self.w_w, self.w_h = size
        self.image = pygame.image.load(resource_path('resources/player_ship.png'))
        self.fire_img = pygame.image.load(resource_path('resources/green_laser.png'))
        self.rect = self.image.get_rect()
        self.rect.centerx = self.w_w // 2
        self.rect.bottom = self.w_h - 20

        self.lives = 3
        self.velocity = 5

        self.fire_sound = pygame.mixer.Sound(resource_path('resources/player_fire.wav'))
        self.hit_sound = pygame.mixer.Sound(resource_path('resources/player_hit.wav'))

    def update(self):
        """ Update the Player """
        keys = pygame.key.get_pressed()

        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and self.rect.x > 0:
            self.rect.x -= self.velocity
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and self.rect.x < self.w_w - 64:
            self.rect.x += self.velocity

    def fire(self):
        """ Fire a Bullet """
        if len(self.bullet_group) <= 2:
            self.fire_sound.play()
            self.bullet_group.add(Bullet(self.rect.centerx, self.rect.top - 10, self.fire_img, -1, self.bullet_group))

    def reset(self):
        """ Resets the Player Position """
        self.rect.centerx = self.w_w // 2
