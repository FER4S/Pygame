import pygame
import os
import sys


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class Bullet(pygame.sprite.Sprite):
    """ A Bullet Class """
    def __init__(self, x, y, img, dy, bullet_group):
        """ Initialize the Bullet """
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.dy = dy
        self.w_w, self.w_h = pygame.display.get_surface().get_size()
        self.bullet_group = bullet_group

        self.velocity = 10

    def update(self):
        """ Move The Bullet """
        self.rect.y += self.velocity * self.dy
        self.delete_bullet()

    def delete_bullet(self):
        """ Delete the Bullet if it is out of the screen"""
        if self.rect.y > self.w_h or self.rect.y < 0:
            self.bullet_group.remove(self)
