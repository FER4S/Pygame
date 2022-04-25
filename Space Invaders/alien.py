import random
import pygame
import sys
import os
from bullet import Bullet


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class Alien(pygame.sprite.Sprite):
    """ A Class to Create an Enemy Alien """
    def __init__(self, x, y, window, bullet_group, alien_group, round):
        """ Initialize the Alien """
        super().__init__()
        self.w_w, self.w_h = window.get_size()
        self.bullet_group = bullet_group
        self.alien_group = alien_group
        self.image = pygame.image.load(resource_path('resources/alien.png'))
        self.img = pygame.image.load(resource_path('resources/red_laser.png'))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.round = round

        self.dx = 1
        self.velocity = 3

        self.fire_sound = pygame.mixer.Sound(resource_path('resources/alien_fire.wav'))

    def update(self):
        """ Update the Alien """
        self.rect.x += self.dx * self.velocity

        # check go down
        if self.rect.x > self.w_w-64 or self.rect.x < 0:
            for alien in self.alien_group.sprites():
                alien.dx *= -1
                alien.rect.y += 20 * self.round

        if random.randint(0, 1000) == 0 and len(self.bullet_group) < 4:
            self.fire()

    def fire(self):
        """ Alien Fires """
        self.fire_sound.play()
        self.bullet_group.add(Bullet(self.rect.centerx, self.rect.bottom, self.img, 1, self.bullet_group))
