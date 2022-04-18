from random import randint
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

# constants
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 400
PLAYER_VELOCITY = 5
FPS = 60
STARTING_SCORE = 0
STARTING_LIFES = 5
STARTING_FOOD_SPEED = 5

score = STARTING_SCORE
lifes = STARTING_LIFES
food_speed = STARTING_FOOD_SPEED


# set clock
clock = pygame.time.Clock()

# set display
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Feed The Dragon')

# load images
dragon_image = pygame.image.load(resource_path('resources/dragon.png'))
dragon_rect = dragon_image.get_rect()
dragon_rect.center = (80, WINDOW_HEIGHT//2)

food_image = pygame.image.load(resource_path('resources/food.png'))
food_rect = food_image.get_rect()
food_rect.center = (WINDOW_WIDTH, WINDOW_HEIGHT//2)

# Load fonts
title_font = pygame.font.Font(
    resource_path('resources/AttackGraffiti.ttf'), 32)
score_lifes_font = pygame.font.Font(
    resource_path('resources/DanceToday.otf'), 30)

# define text
title = title_font.render('Feed The Dragon', True, (37, 180, 44))
title_rect = title.get_rect()
title_rect.center = (WINDOW_WIDTH//2, 22)

score_text = score_lifes_font.render(f'Score {score}', True, (255, 255, 255))
score_rect = score_text.get_rect()
score_rect.topleft = (25, 10)

lifes_text = score_lifes_font.render(f'Lifes {lifes}', True, (255, 0, 0))
lifes_rect = lifes_text.get_rect()
lifes_rect.topright = (WINDOW_WIDTH-25, 10)

game_over = title_font.render('GAME OVER!', True, (255, 255, 255))
game_over_rect = game_over.get_rect()
game_over_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2)

continue_text = score_lifes_font.render(
    'Press anykey to play again', True, (37, 180, 44))
continue_rect = continue_text.get_rect()
continue_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 32)


# load sounds
food = pygame.mixer.Sound(resource_path(
    'resources/food_sound.wav'))
miss = pygame.mixer.Sound(resource_path(
    'resources/miss_sound.wav'))
bg = pygame.mixer.music.load(resource_path(
    'resources/bg_music.wav'))

miss.set_volume(.5)

# play background music
pygame.mixer.music.play(-1, 0.0)

running = True
result = False
while running:
    # loop over events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and result:
            score = STARTING_SCORE
            lifes = STARTING_LIFES
            food_speed = STARTING_FOOD_SPEED
            result = False
            pygame.mixer.music.play(-1, 0.0)

    # getting keys being hold
    keys = pygame.key.get_pressed()

    if (keys[pygame.K_w] or keys[pygame.K_UP]) and dragon_rect.top > 50:
        dragon_rect.y -= PLAYER_VELOCITY
    if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and dragon_rect.bottom < WINDOW_HEIGHT:
        dragon_rect.y += PLAYER_VELOCITY

    # check collision
    if dragon_rect.colliderect(food_rect):
        food.play()
        food_rect.topleft = (WINDOW_WIDTH,
                             randint(82, WINDOW_HEIGHT - 32))
        food_speed += 1
        score += 1

    if food_rect.x < 0:
        miss.play()
        food_rect.topleft = (WINDOW_WIDTH,
                             randint(82, WINDOW_HEIGHT - 32))
        lifes -= 1
        if lifes < 0:
            lifes = 0
            pygame.mixer.music.stop()
            result = True

    # wipe old screen
    window.fill((0, 0, 0))

    # changing score and life
    score_text = score_lifes_font.render(
        f'Score {score}', True, (255, 255, 255))
    lifes_text = score_lifes_font.render(
        f'Lifes {lifes}', True, (255, 0, 0))

    # blitting images and text
    window.blit(dragon_image, dragon_rect)
    window.blit(food_image, food_rect)

    window.blit(title, title_rect)
    window.blit(score_text, score_rect)
    window.blit(lifes_text, lifes_rect)

    # draw line
    pygame.draw.line(window, (255, 255, 255), (0, 50), (WINDOW_WIDTH, 50), 5)

    # move food
    if not result:
        food_rect.x -= food_speed

    # check if lost
    if result:
        window.blit(game_over, game_over_rect)
        window.blit(continue_text, continue_rect)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                score = STARTING_SCORE
                lifes = STARTING_LIFES
                food_speed = STARTING_FOOD_SPEED

    pygame.display.update()

    clock.tick(FPS)


pygame.quit()
