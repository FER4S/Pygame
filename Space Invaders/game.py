import pygame
import sys
import os
from alien import Alien


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class Game:
    """ A Class to Control Gameplay """

    def __init__(self, window, player, player_bullet_group, alien_group, alien_bullet_group):
        """ Initialize The Game Object """
        self.score = 0
        self.round = 0

        self.window = window
        self.player = player
        self.player_bullet_group = player_bullet_group
        self.alien_group = alien_group
        self.alien_bullet_group = alien_bullet_group
        self.w_w, self.w_h = window.get_size()

        self.new_round_sound = pygame.mixer.Sound(resource_path('resources/new_round.wav'))
        self.breach = pygame.mixer.Sound(resource_path('resources/breach.wav'))

        self.font = pygame.font.Font(resource_path('resources/Facon.ttf'), 50)

    def update(self):
        """ Update The Game Object"""
        self.check_collision()

    def draw(self):
        """ Draw The HUD to The Screen"""
        # colours
        white = (255, 255, 255)

        # text
        round_text = self.font.render(f'Round: {self.round}', True, white)
        round_rect = round_text.get_rect()
        round_rect.topleft = (10, 10)

        score_text = self.font.render(f'Score: {self.score}', True, white)
        score_rect = score_text.get_rect()
        score_rect.centerx = self.w_w // 2
        score_rect.top = 10

        lives_text = self.font.render(f'Lives: {self.player.lives}', True, white)
        lives_rect = lives_text.get_rect()
        lives_rect.topright = (self.w_w - 10, 10)

        # blit the HUD
        self.window.blit(round_text, round_rect)
        self.window.blit(score_text, score_rect)
        self.window.blit(lives_text, lives_rect)
        pygame.draw.line(self.window, white, (0, 70), (self.w_w, 70), 3)
        pygame.draw.line(self.window, white, (0, self.w_h - 100), (self.w_w, self.w_h - 100), 3)

    def check_collision(self):
        """ Check for Collision Between The Bullets And The Aliens """
        killed_alien = pygame.sprite.groupcollide(self.player_bullet_group, self.alien_group, True, True)
        if killed_alien:
            self.score += 100 * self.round
            if not self.alien_group:
                self.player.reset()
                self.new_round()

        killed_ship = pygame.sprite.spritecollideany(self.player, self.alien_bullet_group)
        if killed_ship:
            self.player.lives -= 1
            self.player.hit_sound.play()
            self.player.reset()
            # remove bullets
            for bullet in self.alien_bullet_group:
                self.alien_bullet_group.remove(bullet)
            for bullet in self.player_bullet_group:
                self.player_bullet_group.remove(bullet)
            if self.player.lives < 0:
                self.pause_game(f'Final Score: {self.score}', "Press 'Enter' to Play Again", "Press 'Esc' to Quit")
                self.reset_game()
            else:
                self.pause_game(f'You got hit!', "Press 'Enter' to Continue", "Press 'Esc' to Quit")

        for alien in self.alien_group.sprites():
            if alien.rect.bottom > self.w_h - 100:
                self.breach.play()
                self.pause_game(f'Final Score: {self.score}', "Press 'Enter' to Play Again", "Press 'Esc' to Quit")
                self.reset_game()

    def new_round(self):
        """ Generate New Aliens for The New Round """
        self.round += 1

        # remove any remaining aliens/bullets
        for alien in self.alien_group:
            self.alien_group.remove(alien)
        for bullet in self.alien_bullet_group:
            self.alien_bullet_group.remove(bullet)
        for bullet in self.player_bullet_group:
            self.player_bullet_group.remove(bullet)

        # add new aliens
        for i in range(10):
            for j in range(5):
                self.alien_group.add(
                    Alien(i * 80, 75 + j * 50, self.window, self.alien_bullet_group, self.alien_group, self.round))

        self.new_round_sound.play()

    def pause_game(self, main_text, sub_text, sub_text1):
        """ Pause The Game """
        # colours
        white = (255, 255, 255)
        black = (0, 0, 0)

        main_text = self.font.render(main_text, True, white)
        main_rect = main_text.get_rect()
        main_rect.center = (self.w_w // 2, self.w_h // 2)

        sub_text = self.font.render(sub_text, True, white)
        sub_rect = sub_text.get_rect()
        sub_rect.center = (self.w_w // 2, self.w_h // 2 + 64)

        sub_text1 = self.font.render(sub_text1, True, white)
        sub_rect1 = sub_text1.get_rect()
        sub_rect1.center = (self.w_w // 2, self.w_h // 2 + 128)

        self.window.fill(black)

        self.window.blit(main_text, main_rect)
        self.window.blit(sub_text, sub_rect)
        self.window.blit(sub_text1, sub_rect1)

        pygame.display.update()

        is_paused = True
        while is_paused:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        is_paused = False
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
                if event.type == pygame.QUIT:
                    sys.exit()

    def reset_game(self):
        """ Reset The Game """
        self.score = 0
        self.round = 0

        self.player.lives = 3
        self.player.reset()

        self.new_round()
