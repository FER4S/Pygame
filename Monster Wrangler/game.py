import random
import pygame
import sys
import os
from monster import Monster


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class Game:
    """ A Class to Control Gameplay"""

    def __init__(self, window, player, monster_group, FPS):
        """ Initialize The Game Object """
        self.score = 0
        self.round = 0

        self.timer = 0
        self.frame_count = 0
        self.FPS = FPS

        self.window = window
        self.player = player
        self.monster_group = monster_group

        self.W_W, self.W_H = self.window.get_size()

        self.next_level_sound = pygame.mixer.Sound(resource_path('resources/next_level.wav'))

        self.font = pygame.font.Font(resource_path('resources/Abrushow.ttf'), 24)

        blue_img = pygame.image.load(resource_path('resources/blue_monster.png'))
        green_img = pygame.image.load(resource_path('resources/green_monster.png'))
        purple_img = pygame.image.load(resource_path('resources/purple_monster.png'))
        yellow_img = pygame.image.load(resource_path('resources/yellow_monster.png'))
        # monster type
        self.target_imgs = [blue_img, green_img, purple_img, yellow_img]

        self.target_type = random.randint(0, 3)
        self.target_img = self.target_imgs[self.target_type]

        self.target_rect = self.target_img.get_rect()
        self.target_rect.centerx = 600
        self.target_rect.top = 30

    def update(self):
        """ Update The Game Object"""
        self.frame_count += 1
        if self.frame_count == self.FPS:
            self.timer += 1
            self.frame_count = 0

        # check for collision
        self.check_collisions()

    def draw(self):
        """ Draw The HUD to The Screen"""
        # colours
        white = (255, 255, 255)
        blue = (20, 176, 235)
        green = (87, 201, 47)
        purple = (226, 73, 243)
        yellow = (243, 157, 20)

        colours = [blue, green, purple, yellow]

        # text
        catch_text = self.font.render('Current Catch', True, white)
        catch_rect = catch_text.get_rect()
        catch_rect.centerx = self.W_W // 2
        catch_rect.top = 5

        score_text = self.font.render(f'Score: {self.score}', True, white)
        score_rect = score_text.get_rect()
        score_rect.topleft = (5, 5)

        lives_text = self.font.render(f'Lives: {self.player.lives}', True, white)
        lives_rect = lives_text.get_rect()
        lives_rect.topleft = (5, 35)

        round_text = self.font.render(f'Round: {self.round}', True, white)
        round_rect = round_text.get_rect()
        round_rect.topleft = (5, 65)

        time_text = self.font.render(f'Round Time: {self.timer}', True, white)
        time_rect = time_text.get_rect()
        time_rect.topright = (self.W_W - 10, 5)

        wrap_text = self.font.render(f'Wraps: {self.player.wraps}', True, white)
        wrap_rect = wrap_text.get_rect()
        wrap_rect.topright = (self.W_W - 10, 35)

        # blit the HUD
        self.window.blit(catch_text, catch_rect)
        self.window.blit(score_text, score_rect)
        self.window.blit(round_text, round_rect)
        self.window.blit(lives_text, lives_rect)
        self.window.blit(time_text, time_rect)
        self.window.blit(wrap_text, wrap_rect)
        self.window.blit(self.target_img, self.target_rect)

        pygame.draw.rect(self.window, colours[self.target_type], (self.W_W // 2 - 32, 30, 64, 64), 2)
        pygame.draw.rect(self.window, colours[self.target_type], (0, 100, self.W_W, self.W_H - 200), 4)

    def check_collisions(self):
        """ Check for Collision Between The Player And The Monsters """
        collided_monster = pygame.sprite.spritecollideany(self.player, self.monster_group)

        if collided_monster:
            if collided_monster.monster_type == self.target_type:
                self.score += 100 * self.round
                # remove monster
                collided_monster.remove(self.monster_group)

                if self.monster_group:
                    self.player.catch_sound.play()
                    self.set_target()
                else:
                    self.player.reset()
                    self.new_round()
            else:
                self.player.die_sound.play()
                self.player.lives -= 1
                self.player.reset()
                if self.player.lives <= 0:
                    self.pause_game(f'Final Score: {self.score}', "Press 'Enter' to Play Again")
                    self.reset_game()

    def new_round(self):
        """ Generate New Monsters for The New Round """
        # get score base on round timer
        self.score += int(10000 * self.round / (1 + self.timer))

        # reset round values
        self.timer = 0
        self.frame_count = 0
        self.round += 1
        self.player.wraps += 1

        # remove any remaining monster ( loss )
        for monster in self.monster_group:
            self.monster_group.remove(monster)

        # new monster
        for i in range(self.round):
            self.monster_group.add(
                Monster(random.randint(0, self.W_W - 64), random.randint(100, self.W_H - 264), self.target_imgs[0], 0))
            self.monster_group.add(
                Monster(random.randint(0, self.W_W - 64), random.randint(100, self.W_H - 264), self.target_imgs[1], 1))
            self.monster_group.add(
                Monster(random.randint(0, self.W_W - 64), random.randint(100, self.W_H - 264), self.target_imgs[2], 2))
            self.monster_group.add(
                Monster(random.randint(0, self.W_W - 64), random.randint(100, self.W_H - 264), self.target_imgs[3], 3))

        self.set_target()
        self.next_level_sound.play()

    def set_target(self):
        """ Choose a New Monster Target for The Player """
        target = random.choice(self.monster_group.sprites())
        self.target_type = target.monster_type
        self.target_img = target.image

    def pause_game(self, main_text, sub_text):
        """ Pause The Game """
        white = (255, 255, 255)
        black = (0, 0, 0)

        main_text = self.font.render(main_text, True, white)
        main_rect = main_text.get_rect()
        main_rect.center = (self.W_W // 2, self.W_H // 2)

        sub_text = self.font.render(sub_text, True, white)
        sub_rect = sub_text.get_rect()
        sub_rect.center = (self.W_W // 2, self.W_H // 2 + 64)

        self.window.fill(black)

        self.window.blit(main_text, main_rect)
        self.window.blit(sub_text, sub_rect)

        pygame.display.update()

        is_paused = True
        while is_paused:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        is_paused = False
                if event.type == pygame.QUIT:
                    sys.exit()

    def reset_game(self):
        """ Reset The Game """
        self.score = 0
        self.round = 0

        self.player.lives = 5
        self.player.wraps = 2
        self.player.reset()

        self.new_round()
