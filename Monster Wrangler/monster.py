import random
import pygame


class Monster(pygame.sprite.Sprite):
    """ A Class to Create an Enemy Monster """
    def __init__(self, x, y, img, monster_type):
        """ Initialize the Monster """
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        # monster type is an int , 0=blue, 1=green, 2=purple, 3=yellow
        self.monster_type = monster_type

        self.dx = random.choice([-1, 1])
        self.dy = random.choice([-1, 1])
        self.velocity = random.randint(1, 5)

    def update(self):
        """ Update the Monster """
        self.rect.x += self.dx * self.velocity
        self.rect.y += self.dy * self.velocity

        # bounce
        if self.rect.y > 536 or self.rect.y < 100:
            self.dy *= -1
        if self.rect.x > 1136 or self.rect.x < 0:
            self.dx *= -1

