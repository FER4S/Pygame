from random import choice
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

# set display
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 640
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# set FPS and Clock
FPS = 9
clock = pygame.time.Clock()


# colours
RED = (232, 48, 48)  # head
YELLOW = (232, 223, 48)  # body
GREEN = (65, 232, 48)
BLACK = (0, 0, 0)

# poisitions for food
food_pos = [x for x in range(0, 640, 32)]

# fonts
font = pygame.font.Font(resource_path('resources/GamePlayed.ttf'), 32)

# text
score_text = font.render(f'Your Score is: 0', True, BLACK, GREEN)
score_rect = score_text.get_rect()
score_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2)

game_over_text = font.render('GAME OVER', True, BLACK, GREEN)
game_over_rect = game_over_text.get_rect()
game_over_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2-36)

continue_text = font.render('Press anykey to play again', True, BLACK, GREEN)
continue_rect = continue_text.get_rect()
continue_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 36)

# load images
bg_img = pygame.image.load(resource_path('resources/bg_img.jpg'))
bg_rect = bg_img.get_rect()
bg_rect.topleft = (0, 0)

food_img = pygame.image.load(resource_path('resources/apple.png'))
food_rect = food_img.get_rect()
random_pos_x, random_pos_y = choice(food_pos), choice(food_pos)
food_rect.topleft = (random_pos_x, random_pos_y)


# CONSTANTS
STARTING_SCORE = 0
STARTING_HEAD_X = WINDOW_WIDTH//2
STARTING_HEAD_Y = WINDOW_HEIGHT//2
STARTING_POISTIONS_X = []
STARTING_POISTIONS_y = []

score = STARTING_SCORE
head_x = STARTING_HEAD_X
head_y = STARTING_HEAD_Y
move_x = 1
move_y = 0
poistions_x = STARTING_POISTIONS_X
poistions_y = STARTING_POISTIONS_y

# load sounds
eat_sound = pygame.mixer.Sound(resource_path('resources/eat_sound.wav'))
pygame.mixer.music.load(resource_path('resources/bg_music.wav'))
pygame.mixer.music.play(-1, 0.0)


# game main loop
result = False
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w and (move_x != 0 and move_y != 1):
                move_x = 0
                move_y = -1
            if event.key == pygame.K_s and (move_x != 0 and move_y != -1):
                move_x = 0
                move_y = 1
            if event.key == pygame.K_a and (move_x != 1 and move_y != 0):
                move_x = -1
                move_y = 0
            if event.key == pygame.K_d and (move_x != -1 and move_y != 0):
                move_x = 1
                move_y = 0
        if event.type == pygame.KEYDOWN and result:
            score = STARTING_SCORE
            head_x = STARTING_HEAD_X
            head_y = STARTING_HEAD_Y
            move_x = 1
            move_y = 0
            poistions_x = STARTING_POISTIONS_X
            poistions_y = STARTING_POISTIONS_y
            random_pos_x, random_pos_y = choice(food_pos), choice(food_pos)
            food_rect.topleft = (random_pos_x, random_pos_y)
            pygame.mixer.music.play(-1, 0.0)
            result = False

    # filling background
    window.blit(bg_img, bg_rect)

    # blitting food
    window.blit(food_img, food_rect)

    # if game is over
    if result:
        score_text = font.render(f'Your Score is: {score}', True, BLACK, GREEN)
        window.blit(score_text, score_rect)
        window.blit(game_over_text, game_over_rect)
        window.blit(continue_text, continue_rect)

    # check if ate food
    if food_rect.collidepoint(head_x, head_y):
        eat_sound.play()
        score += 1
        random_pos_x, random_pos_y = choice(food_pos), choice(food_pos)
        food_rect.topleft = (random_pos_x, random_pos_y)
        while(random_pos_x in r_x[:score+1]):
            random_pos_x, random_pos_y = choice(food_pos), choice(food_pos)
            food_rect.topleft = (random_pos_x, random_pos_y)

    # check if hit the edges
    if head_x < 0 or head_x > WINDOW_WIDTH or head_y < 0 or head_y > WINDOW_HEIGHT:
        result = True
        pygame.mixer.music.stop()

    if not result:
        # saving positions
        poistions_x.append(head_x)
        poistions_y.append(head_y)
        # get reversed lists
        r_x = list(reversed(poistions_x))
        r_y = list(reversed(poistions_y))

        # moving the snake
        head_x += 32 * move_x
        head_y += 32 * move_y
        for i in range(score+1):
            pygame.draw.rect(window, RED if i == 0 else YELLOW,
                             (r_x[i], r_y[i], 32, 32))
            # check if head hits body
            if i:
                if r_x[0] == r_x[i] and r_y[0] == r_y[i]:
                    pygame.mixer.music.stop()
                    result = True

    # update window and tick the clock
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
