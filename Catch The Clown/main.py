from random import choice
import pygame
import os
import sys


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# init pygame
pygame.init()

# colours
YELLOW = (248, 231, 28)
CYAN = (1, 175, 209)


# constants
WINDOW_WIDTH = 967
WINDOW_HEIGHT = 655
STARTING_SCORE = 0
STARTING_LIFES = 5
STARTING_SPEED = 4
DIRECTION = 1

score = STARTING_SCORE
lifes = STARTING_LIFES
speed = STARTING_SPEED
direction_x = DIRECTION
direction_y = DIRECTION


# set FPS and clock
FPS = 60
clock = pygame.time.Clock()


# display surface
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Catch The Clown')

# loading images
bg_img = pygame.image.load(resource_path('resources/background.png'))
bg_rect = bg_img.get_rect()
bg_rect.topleft = (0, 0)

clown_img = pygame.image.load(resource_path('resources/clown.png'))
clown_rect = clown_img.get_rect()
clown_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2)

# loading sounds
click_sound = pygame.mixer.Sound(resource_path('resources/click_sound.wav'))
miss_sound = pygame.mixer.Sound(resource_path('resources/miss_sound.wav'))
bg_music = pygame.mixer.music.load(resource_path('resources/bg_music.wav'))

# loading fonts
font = pygame.font.Font(resource_path('resources/Franxurter.ttf'), 32)

# defining text
title_text = font.render('Catch The Clown', True, CYAN)
title_rect = title_text.get_rect()
title_rect.topleft = (20, 10)

score_text = font.render(f'Score: {score}', True, YELLOW)
score_rect = score_text.get_rect()
score_rect.topright = (WINDOW_WIDTH-20, 10)

lifes_text = font.render(f'Lifes: {lifes}', True, YELLOW)
lifes_rect = lifes_text.get_rect()
lifes_rect.topright = (WINDOW_WIDTH-20, 42)

game_over_text = font.render('GAME OVER', True, CYAN, YELLOW)
game_over_rect = game_over_text.get_rect()
game_over_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2)

continue_text = font.render('Press anykey to play again', True, YELLOW, CYAN)
continue_rect = continue_text.get_rect()
continue_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 32)

# play background music
pygame.mixer.music.play(-1, 0.0)

# game main loop
result = False
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and not result:
            if clown_rect.collidepoint(event.pos):
                click_sound.play()
                score += 1
                speed += .5
                cur_x, cur_y = direction_x, direction_y
                while(cur_x == direction_x and cur_y == direction_y):
                    direction_x, direction_y = choice([-1, 1]), choice([-1, 1])

            else:
                miss_sound.play()
                lifes -= 1
                if lifes < 0:
                    lifes = 0
                    pygame.mixer.music.stop()
                    result = True

        if result and (event.type == pygame.KEYDOWN):
            score = STARTING_SCORE
            lifes = STARTING_LIFES
            speed = STARTING_SPEED
            direction_x = DIRECTION
            direction_y = DIRECTION
            pygame.mixer.music.play(-1, 0.0)
            result = False

    # blitting images
    window.blit(bg_img, bg_rect)
    window.blit(clown_img, clown_rect)

    # blitting text
    window.blit(title_text, title_rect)
    window.blit(score_text, score_rect)
    window.blit(lifes_text, lifes_rect)

    # updaing score and lifes
    lifes_text = font.render(f'Lifes: {lifes}', True, YELLOW)
    score_text = font.render(f'Score: {score}', True, YELLOW)

    # move the clown xD
    if not result:
        clown_rect.x += speed * direction_x
        clown_rect.y += speed * direction_y

    # check bounce
    if clown_rect.y > WINDOW_HEIGHT-64 or clown_rect.y < 0:
        direction_y *= -1
    if clown_rect.x > WINDOW_WIDTH-64 or clown_rect.x < 0:
        direction_x *= -1

    if result:
        window.blit(game_over_text, game_over_rect)
        window.blit(continue_text, continue_rect)

    # update screen and tick the clock
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
