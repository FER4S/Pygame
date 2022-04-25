import os
import sys
import pygame
from game import Game
from player import Player
from alien import Alien
from bullet import Bullet


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# init pygame
pygame.init()

# set window
window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
window_width, window_height = window.get_size()
pygame.display.set_caption('Space Invaders')

# set FPS and clock
FPS = 60
clock = pygame.time.Clock()

# create a bullet group
player_bullet_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()

# create an Alien group
alien_group = pygame.sprite.Group()

# create player group and objet
player_group = pygame.sprite.Group()
player = Player((window_width, window_height), player_bullet_group)
player_group.add(player)

# create a game objet
game = Game(window, player, player_bullet_group, alien_group, alien_bullet_group)
game.pause_game('Space Invaders', "Press 'Enter' to Play", "Press 'Esc' to Quit")
game.new_round()

# main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            # player fire
            if event.key == pygame.K_SPACE:
                player.fire()

    # fill the display
    window.fill((0, 0, 0))

    # update and draw sprite groups
    player_group.update()
    player_group.draw(window)

    player_bullet_group.update()
    player_bullet_group.draw(window)

    alien_group.update()
    alien_group.draw(window)

    alien_bullet_group.update()
    alien_bullet_group.draw(window)

    # update and draw the game
    game.update()
    game.draw()

    # update window and tick the clock
    pygame.display.update()
    clock.tick(FPS)

# quit pygame
pygame.quit()
