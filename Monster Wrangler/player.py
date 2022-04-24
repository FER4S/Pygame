import pygame
import os
import sys


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class Player(pygame.sprite.Sprite):
    """ A Player Class """
    def __init__(self):
        """ Initialize the Player"""
        super().__init__()
        self.image = pygame.image.load(resource_path('resources/knight.png'))
        self.rect = self.image.get_rect()
        self.rect.centerx = 600
        self.rect.bottom = 700

        self.lives = 5
        self.wraps = 2
        self.velocity = 8

        self.catch_sound = pygame.mixer.Sound(resource_path('resources/catch.wav'))
        self.die_sound = pygame.mixer.Sound(resource_path('resources/die.wav'))
        self.wrap_sound = pygame.mixer.Sound(resource_path('resources/warp.wav'))

    def update(self):
        """ Update the Player """
        keys = pygame.key.get_pressed()

        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and self.rect.x > 0:
            self.rect.x -= self.velocity
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and self.rect.x < 1136:
            self.rect.x += self.velocity
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and self.rect.y > 100:
            self.rect.y -= self.velocity
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and self.rect.y < 536:
            self.rect.y += self.velocity

    def wrap(self):
        """ Wrap the Player to the Bottom (safe zone) """
        if self.wraps > 0:
            self.wraps -= 1
            self.wrap_sound.play()
            self.rect.bottom = 700

    def reset(self):
        """ Resets the Player Position """
        self.rect.centerx = 600
        self.rect.bottom = 700
