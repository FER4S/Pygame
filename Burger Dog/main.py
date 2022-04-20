from random import randint
import pygame
import sys
import os


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# init pygame
pygame.init()

# set window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Burger Dog')

# set FPS and clock
FPS = 60
clock = pygame.time.Clock()

# constants
STARTING_LIFES = 3
NORMAL_SPEED = 5
BOOST_SPEED = 12
STARTING_BOOST_VALUE = 100
STARTING_BURGER_SPEED = 3
BURGER_ACCELRATION = .5
BUFFER = -100

score = 0
burger_points = 0
burgers_eaten = 0
player_lifes = STARTING_LIFES
player_speed = NORMAL_SPEED
boost_value = STARTING_BOOST_VALUE
burger_speed = STARTING_BURGER_SPEED


# colours
ORANGE = (246, 170, 54)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


# fonts
font = pygame.font.Font(resource_path('resources/WashYourHand.ttf'), 32)

# text
points_text = font.render(f'Burger Points: {burger_points}', True, ORANGE)
points_rect = points_text.get_rect()
points_rect.topleft = (10, 10)

score_text = font.render(f'Score: {score}', True, ORANGE)
score_rect = score_text.get_rect()
score_rect.topleft = (10, 50)

title_text = font.render('Burger Dog', True, ORANGE)
title_rect = title_text.get_rect()
title_rect.center = (WINDOW_WIDTH//2, 25)

eaten_text = font.render(f'Burgers Eaten: {burgers_eaten}', True, ORANGE)
eaten_rect = eaten_text.get_rect()
eaten_rect.center = (WINDOW_WIDTH//2, 65)

lifes_text = font.render(f'Lifes: {player_lifes}', True, ORANGE)
lifes_rect = lifes_text.get_rect()
lifes_rect.topright = (WINDOW_WIDTH-10, 10)

boost_text = font.render(f'Boost: {boost_value}', True, ORANGE)
boost_rect = boost_text.get_rect()
boost_rect.topright = (WINDOW_WIDTH-10, 50)

game_over_text = font.render('GAME OVER', True, ORANGE)
game_over_rect = game_over_text.get_rect()
game_over_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2)

continue_text = font.render('Press any key to play again', True, ORANGE)
continue_rect = continue_text.get_rect()
continue_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2+64)

# load sounds
bark_sound = pygame.mixer.Sound(resource_path('resources/bark_sound.wav'))
miss_sound = pygame.mixer.Sound(resource_path('resources/miss_sound.wav'))
pygame.mixer.music.load(resource_path('resources/bg_music.wav'))

# load images
dog_right = pygame.image.load(resource_path('resources/dog_right.png'))
dog_left = pygame.image.load(resource_path('resources/dog_left.png'))
dog_img = dog_right
dog_rect = dog_img.get_rect()
dog_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT-50)

burger_img = pygame.image.load(resource_path('resources/burger.png'))
burger_rect = burger_img.get_rect()
burger_rect.topleft = (randint(0, WINDOW_WIDTH-32), BUFFER)

# main game loop
pygame.mixer.music.play()
result = False
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and result:
            score = 0
            burger_points = 0
            burgers_eaten = 0
            player_lifes = STARTING_LIFES
            player_speed = NORMAL_SPEED
            boost_value = STARTING_BOOST_VALUE
            burger_speed = STARTING_BURGER_SPEED
            burger_rect.topleft = (randint(0, WINDOW_WIDTH-32), BUFFER)
            dog_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT-50)
            pygame.mixer.music.play()
            result = False

    # move the dog
    keys = pygame.key.get_pressed()

    if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and dog_rect.x > 0:
        dog_rect.x -= player_speed
        dog_img = dog_left
    if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and dog_rect.x < WINDOW_WIDTH-64:
        dog_rect.x += player_speed
        dog_img = dog_right
    if (keys[pygame.K_w] or keys[pygame.K_UP]) and dog_rect.y > 90:
        dog_rect.y -= player_speed
    if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and dog_rect.y < WINDOW_HEIGHT-64:
        dog_rect.y += player_speed

    # engage boost
    if keys[pygame.K_SPACE] and boost_value > 0:
        player_speed = BOOST_SPEED
        boost_value -= 1
    else:
        player_speed = NORMAL_SPEED

    # move the burger and reduce its points
    if not result:
        burger_rect.y += burger_speed
        burger_points = int(
            (WINDOW_HEIGHT - burger_rect.y + 100) * burger_speed)

    # if player misses
    if burger_rect.y > WINDOW_HEIGHT:
        burger_rect.topleft = (randint(0, WINDOW_WIDTH-32), BUFFER)
        player_lifes -= 1
        if player_lifes < 0:
            player_lifes = 0
            result = True
        miss_sound.play()

        burger_speed = STARTING_BURGER_SPEED
        boost_value = STARTING_BOOST_VALUE
        dog_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT-50)

    # check for collision
    if dog_rect.colliderect(burger_rect):
        bark_sound.play()
        burger_speed += BURGER_ACCELRATION
        burger_rect.topleft = (randint(0, WINDOW_WIDTH-32), BUFFER)
        score += burger_points
        burgers_eaten += 1
        boost_value += 25
        if boost_value > STARTING_BOOST_VALUE:
            boost_value = STARTING_BOOST_VALUE

    # update HUD
    boost_text = font.render(f'Boost: {boost_value}', True, ORANGE)
    points_text = font.render(f'Burger Points: {burger_points}', True, ORANGE)
    eaten_text = font.render(f'Burgers Eaten: {burgers_eaten}', True, ORANGE)
    score_text = font.render(f'Score: {score}', True, ORANGE)
    lifes_text = font.render(f'Lifes: {player_lifes}', True, ORANGE)

    # fill the background
    window.fill(BLACK)

    # blit the HUD
    window.blit(points_text, points_rect)
    window.blit(score_text, score_rect)
    window.blit(title_text, title_rect)
    window.blit(lifes_text, lifes_rect)
    window.blit(boost_text, boost_rect)
    window.blit(eaten_text, eaten_rect)
    pygame.draw.line(window, WHITE, (0, 90), (WINDOW_WIDTH, 90), 5)

    # blit images
    window.blit(dog_img, dog_rect)
    window.blit(burger_img, burger_rect)

    # when game is over
    if result:
        pygame.mixer.music.pause()
        window.blit(game_over_text, game_over_rect)
        window.blit(continue_text, continue_rect)

    # update the window and tick the clock
    pygame.display.update()
    clock.tick(FPS)


pygame.quit()
