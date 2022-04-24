import pygame
import random
import os
import sys

from game import Game
from player import Player
from monster import Monster


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# init pygame
pygame.init()

# set window
WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 700
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Monster Wrangler')

# set FPS and clock
FPS = 60
clock = pygame.time.Clock()

# create a player group and object
player_group = pygame.sprite.Group()
player = Player()
player_group.add(player)

# create a monster group
monster_group = pygame.sprite.Group()

# create a game object
game = Game(window, player, monster_group, FPS)
game.pause_game("Monster Wrangler", "Press 'Enter' to Start")
game.new_round()

# main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # player wraps
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.wrap()

    # fill the display
    window.fill((0, 0, 0))

    # update and draw sprite groups
    player_group.update()
    player_group.draw(window)

    monster_group.update()
    monster_group.draw(window)

    # update and draw the game
    game.update()
    game.draw()

    # update display and tick the clock
    pygame.display.update()
    clock.tick(FPS)

# quit pygame
pygame.quit()
