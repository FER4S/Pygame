import pygame
import random
import os
import sys


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


vector = pygame.math.Vector2

# initialize pygame
pygame.init()

# set display (tile size is 31X31, 1366/31 = 42... wide, 768/31 = 24 high
WINDOW_WIDTH, WINDOW_HEIGHT = 1240, 713
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

pygame.display.set_caption('Zombie Slayer')

# set FPS and Clock
FPS = 60
clock = pygame.time.Clock()


# define Classes
class Game:
    """A class to help manage the game"""

    def __init__(self, player, zombie_group, platform_group, portal_group, bullet_group, ruby_group):
        """Initialize the game"""
        self.STARTING_TIME = 30
        self.STARTING_ZOMBIE_CREATION_TIME = 4

        # set game values
        self.score = 0
        self.round_number = 1
        self.frame_count = 0
        self.round_time = self.STARTING_TIME
        self.zombie_creation_time = self.STARTING_ZOMBIE_CREATION_TIME

        # set fonts
        self.title_font = pygame.font.Font(resource_path('resources/fonts/Poultrygeist.ttf'), 48)
        self.HUD_font = pygame.font.Font(resource_path('resources/fonts/Pixel.ttf'), 24)

        # sounds
        self.lost_ruby_sound = pygame.mixer.Sound(resource_path('resources/sounds/lost_ruby.wav'))
        self.pickup_ruby_sound = pygame.mixer.Sound(resource_path('resources/sounds/ruby_pickup.wav'))
        pygame.mixer.music.load(resource_path('resources/sounds/level_music.wav'))

        # attach groups
        self.player = player
        self.zombie_group = zombie_group
        self.platform_group = platform_group
        self.portal_group = portal_group
        self.bullet_group = bullet_group
        self.ruby_group = ruby_group

    def update(self):
        """Update the game"""
        self.frame_count += 1
        if self.frame_count % FPS == 0:
            self.round_time -= 1
            self.frame_count = 0

        # check for gameplay collisions
        self.check_collisions()

        # add zombie when it's the time
        self.add_zombie()

        # check if won
        self.check_round_completion()

        # check if lost
        self.check_game_over()

    def draw(self):
        """Draw the game HUD"""
        # colours
        WHITE = (255, 255, 255)
        GREEN = (25, 200, 25)

        # text
        score_text = self.HUD_font.render(f'Score: {self.score}', True, WHITE)
        score_rect = score_text.get_rect()
        score_rect.topleft = (10, WINDOW_HEIGHT - 50)

        health_text = self.HUD_font.render(f'Health: {self.player.health}', True, WHITE)
        health_rect = health_text.get_rect()
        health_rect.topleft = (10, WINDOW_HEIGHT - 25)

        title_text = self.title_font.render('Zombie Slayer', True, GREEN)
        title_rect = title_text.get_rect()
        title_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 25)

        round_text = self.HUD_font.render(f'Night: {self.round_number}', True, WHITE)
        round_rect = round_text.get_rect()
        round_rect.topright = (WINDOW_WIDTH - 10, WINDOW_HEIGHT - 50)

        time_text = self.HUD_font.render(f'Sunrise in: {self.round_time}', True, WHITE)
        time_rect = time_text.get_rect()
        time_rect.topright = (WINDOW_WIDTH - 10, WINDOW_HEIGHT - 25)

        # draw the HUD
        window.blit(score_text, score_rect)
        window.blit(health_text, health_rect)
        window.blit(title_text, title_rect)
        window.blit(round_text, round_rect)
        window.blit(time_text, time_rect)

    def add_zombie(self):
        """Add a zombie to the game"""
        # check adding zombie every sec
        if not self.frame_count % FPS:
            # add if creation time is passed
            if not self.round_time % self.zombie_creation_time:
                zombie = Zombie(self.platform_group, self.portal_group, self.round_number, self.round_number + 5)
                self.zombie_group.add(zombie)

    def check_collisions(self):
        """Check collisions that affect gameplay"""
        # if bullet hit a zombie
        collision_dict = pygame.sprite.groupcollide(self.bullet_group, self.zombie_group, True, False)
        if collision_dict:
            for zombies in collision_dict.values():
                for zombie in zombies:
                    zombie.hit_sound.play()
                    zombie.is_dead = True
                    zombie.animate_death = True

        # player collided with a dead zombie or not
        collision_list = pygame.sprite.spritecollide(self.player, self.zombie_group, False, pygame.sprite.collide_mask)
        if collision_list:
            for zombie in collision_list:
                # is the zombie dead? remove it
                if zombie.is_dead:
                    zombie.kick_sound.play()
                    zombie.kill()
                    self.score += 25

                    ruby = Ruby(self.platform_group, self.portal_group)
                    self.ruby_group.add(ruby)
                # not dead? take dmg
                else:
                    self.player.health -= 20
                    self.player.hit_sound.play()
                    # move the player so he doesnt continually take dmg
                    self.player.pos.x += 150 * zombie.direction
                    self.player.rect.bottomleft = self.player.pos

        # player collide with ruby
        if pygame.sprite.spritecollide(self.player, self.ruby_group, True):
            self.pickup_ruby_sound.play()
            self.score += 100
            self.player.health += 10
            if self.player.health > self.player.STARTING_HEALTH:
                self.player.health = self.player.STARTING_HEALTH

        # living zombie collide with ruby
        for zombie in self.zombie_group:
            if not zombie.is_dead:
                if pygame.sprite.spritecollide(zombie, self.ruby_group, True):
                    self.lost_ruby_sound.play()
                    zombie = Zombie(self.platform_group, self.portal_group, self.round_number, self.round_number + 5)
                    self.zombie_group.add(zombie)

    def check_round_completion(self):
        """Check if the player survived a single night"""
        if self.round_time == 0:
            self.new_round()

    def check_game_over(self):
        """Check if the player lost the game"""
        if self.player.health <= 0:
            pygame.mixer.music.stop()
            self.pause_game(f'Game Over! Your Score: {self.score}', "Press 'Enter' to play again...")
            self.reset_game()

    def new_round(self):
        """Start a new night"""
        self.round_number += 1

        # make zombie spawn faster
        if self.round_number < self.STARTING_ZOMBIE_CREATION_TIME:
            self.zombie_creation_time -= 1

        # reset round values
        self.round_time = self.STARTING_TIME

        self.zombie_group.empty()
        self.ruby_group.empty()
        self.bullet_group.empty()

        self.player.reset()

        self.pause_game('You survived the night!', "Press 'Enter' to continue...")

    def pause_game(self, main_text, sub_text):
        """Pause the game"""

        pygame.mixer.music.pause()

        # colours
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        GREEN = (25, 255, 25)

        # create text
        main_text = self.title_font.render(main_text, True, GREEN)
        main_rect = main_text.get_rect()
        main_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

        sub_text = self.title_font.render(sub_text, True, WHITE)
        sub_rect = sub_text.get_rect()
        sub_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 64)

        # display text
        window.fill(BLACK)
        window.blit(sub_text, sub_rect)
        window.blit(main_text, main_rect)
        pygame.display.update()

        is_paused = True
        while is_paused:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        is_paused = False
                        pygame.mixer.music.unpause()
                if event.type == pygame.QUIT:
                    sys.exit()

    def reset_game(self):
        """Reset the game"""
        # reset game values
        self.score = 0
        self.round_number = 1
        self.round_time = self.STARTING_TIME
        self.zombie_creation_time = self.STARTING_ZOMBIE_CREATION_TIME

        # reset the player
        self.player.health = self.player.STARTING_HEALTH
        self.player.reset()

        # empty sprite groups
        self.zombie_group.empty()
        self.ruby_group.empty()
        self.bullet_group.empty()

        pygame.mixer.music.play(-1)


class Tile(pygame.sprite.Sprite):
    """A class to represent a 31X31 pixel area"""

    def __init__(self, x, y, img_int, main_group, sub_group=None):
        """Initialize the tile"""
        super().__init__()
        # dirt
        if img_int == 1:
            self.image = pygame.transform.scale(pygame.image.load(resource_path('resources/images/tiles/Tile (1).png')),
                                                (31, 31))
        # platform
        elif img_int == 2:
            self.image = pygame.transform.scale(pygame.image.load(resource_path('resources/images/tiles/Tile (2).png')),
                                                (31, 31))
            sub_group.add(self)
        elif img_int == 3:
            self.image = pygame.transform.scale(pygame.image.load(resource_path('resources/images/tiles/Tile (3).png')),
                                                (31, 31))
            sub_group.add(self)
        elif img_int == 4:
            self.image = pygame.transform.scale(pygame.image.load(resource_path('resources/images/tiles/Tile (4).png')),
                                                (31, 31))
            sub_group.add(self)
        elif img_int == 5:
            self.image = pygame.transform.scale(pygame.image.load(resource_path('resources/images/tiles/Tile (5).png')),
                                                (31, 31))
            sub_group.add(self)

        # add all to the main group
        main_group.add(self)

        # get the rect of the image and position within the grid
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        # create mask
        self.mask = pygame.mask.from_surface(self.image)


class Player(pygame.sprite.Sprite):
    """A class the user can control"""

    def __init__(self, x, y, platform_group, portal_group, bullet_group):
        """Initialize the player"""
        super().__init__()

        # set constant
        self.HORIZONTAL_ACCELERATION = 2
        self.HORIZONTAL_FRICTION = .15
        self.VERTICAL_ACCELERATION = .8  # GRAVITY
        self.JUMP_SPEED = 18  # HOW HIGH THE PLAYER CAN JUMP
        self.STARTING_HEALTH = 100

        # animation frames
        self.move_right_sprites = []
        self.move_left_sprites = []
        self.idle_right_sprites = []
        self.idle_left_sprites = []
        self.jump_right_sprites = []
        self.jump_left_sprites = []
        self.attack_right_sprites = []
        self.attack_left_sprites = []

        # moving
        self.move_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/run/Run (1).png')),
                                   (62, 62)))
        self.move_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/run/Run (2).png')),
                                   (62, 62)))
        self.move_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/run/Run (3).png')),
                                   (62, 62)))
        self.move_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/run/Run (4).png')),
                                   (62, 62)))
        self.move_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/run/Run (5).png')),
                                   (62, 62)))
        self.move_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/run/Run (6).png')),
                                   (62, 62)))
        self.move_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/run/Run (7).png')),
                                   (62, 62)))
        self.move_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/run/Run (8).png')),
                                   (62, 62)))
        self.move_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/run/Run (9).png')),
                                   (62, 62)))
        self.move_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/run/Run (10).png')),
                                   (62, 62)))
        for sprite in self.move_right_sprites:
            self.move_left_sprites.append(pygame.transform.flip(sprite, True, False))

        # idling
        self.idle_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/idle/Idle (1).png')),
                                   (62, 62)))
        self.idle_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/idle/Idle (2).png')),
                                   (62, 62)))
        self.idle_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/idle/Idle (3).png')),
                                   (62, 62)))
        self.idle_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/idle/Idle (4).png')),
                                   (62, 62)))
        self.idle_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/idle/Idle (5).png')),
                                   (62, 62)))
        self.idle_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/idle/Idle (6).png')),
                                   (62, 62)))
        self.idle_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/idle/Idle (7).png')),
                                   (62, 62)))
        self.idle_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/idle/Idle (8).png')),
                                   (62, 62)))
        self.idle_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/idle/Idle (9).png')),
                                   (62, 62)))
        self.idle_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/idle/Idle (10).png')),
                                   (62, 62)))
        for sprite in self.idle_right_sprites:
            self.idle_left_sprites.append(pygame.transform.flip(sprite, True, False))

        # jumping
        self.jump_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/jump/Jump (1).png')),
                                   (62, 62)))
        self.jump_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/jump/Jump (2).png')),
                                   (62, 62)))
        self.jump_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/jump/Jump (3).png')),
                                   (62, 62)))
        self.jump_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/jump/Jump (4).png')),
                                   (62, 62)))
        self.jump_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/jump/Jump (5).png')),
                                   (62, 62)))
        self.jump_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/jump/Jump (6).png')),
                                   (62, 62)))
        self.jump_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/jump/Jump (7).png')),
                                   (62, 62)))
        self.jump_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/jump/Jump (8).png')),
                                   (62, 62)))
        self.jump_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/jump/Jump (9).png')),
                                   (62, 62)))
        self.jump_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/jump/Jump (10).png')),
                                   (62, 62)))
        for sprite in self.jump_right_sprites:
            self.jump_left_sprites.append(pygame.transform.flip(sprite, True, False))

        # attacking
        self.attack_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/attack/Attack (1).png')),
                                   (62, 62)))
        self.attack_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/attack/Attack (2).png')),
                                   (62, 62)))
        self.attack_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/attack/Attack (3).png')),
                                   (62, 62)))
        self.attack_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/attack/Attack (4).png')),
                                   (62, 62)))
        self.attack_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/attack/Attack (5).png')),
                                   (62, 62)))
        self.attack_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/attack/Attack (6).png')),
                                   (62, 62)))
        self.attack_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/attack/Attack (7).png')),
                                   (62, 62)))
        self.attack_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/attack/Attack (8).png')),
                                   (62, 62)))
        self.attack_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/attack/Attack (9).png')),
                                   (62, 62)))
        self.attack_right_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/attack/Attack (10).png')),
                                   (62, 62)))
        for sprite in self.attack_right_sprites:
            self.attack_left_sprites.append(pygame.transform.flip(sprite, True, False))

        # load and get rect
        self.current_sprite = 0
        self.image = self.idle_right_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

        # attach sprite groups
        self.platform_group = platform_group
        self.portal_group = portal_group
        self.bullet_group = bullet_group

        # animation bool
        self.animation_jump = False
        self.animation_fire = False

        # load sounds
        self.jump_sound = pygame.mixer.Sound(resource_path('resources/sounds/jump_sound.wav'))
        self.slash_sound = pygame.mixer.Sound(resource_path('resources/sounds/slash_sound.wav'))
        self.portal_sound = pygame.mixer.Sound(resource_path('resources/sounds/portal_sound.wav'))
        self.hit_sound = pygame.mixer.Sound(resource_path('resources/sounds/player_hit.wav'))

        # kinematic vectors
        self.pos = vector(x, y)
        self.velocity = vector(0, 0)
        self.acceleration = vector(0, self.VERTICAL_ACCELERATION)

        # initial player values
        self.health = self.STARTING_HEALTH
        self.starting_x, self.starting_y = x, y

    def update(self):
        """Update the player"""
        self.move()
        self.check_collisions()
        self.check_animation()

        # update the player mask
        self.mask = pygame.mask.from_surface(self.image)

    def move(self):
        """Move the player"""
        # set the acceleration vector
        self.acceleration = vector(0, self.VERTICAL_ACCELERATION)

        # if the user is pressing a key ( change x of acceleration to non-zero
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.acceleration.x = -1 * self.HORIZONTAL_ACCELERATION
            self.animate(self.move_left_sprites, .5)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.acceleration.x = self.HORIZONTAL_ACCELERATION
            self.animate(self.move_right_sprites, .5)
        else:
            if self.velocity.x > 0:
                self.animate(self.idle_right_sprites, .5)
            else:
                self.animate(self.idle_left_sprites, .5)

        # calculate new kinematic values
        self.acceleration.x -= self.velocity.x * self.HORIZONTAL_FRICTION
        self.velocity += self.acceleration
        # + .5 * acceleration ( physic formula)
        self.pos += self.velocity + .5 * self.acceleration

        # update rect based on kinematic and add wrap around movement
        if self.pos.x < 0:
            self.pos.x = WINDOW_WIDTH
        elif self.pos.x > WINDOW_WIDTH:
            self.pos.x = 0

        self.rect.bottomleft = self.pos

    def check_collisions(self):
        """Check collisions with platforms and portals"""
        # collision check with platform when falling
        if self.velocity.y > 0:
            collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False,
                                                             pygame.sprite.collide_mask)
            if collided_platforms:
                self.pos.y = collided_platforms[0].rect.top + 5
                self.velocity.y = 0

        # when jumping up
        if self.velocity.y < 0:
            collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False,
                                                             pygame.sprite.collide_mask)
            if collided_platforms:
                self.velocity.y = 0
                while pygame.sprite.spritecollide(self, self.platform_group, False, pygame.sprite.collide_mask):
                    self.pos.y += 1
                    self.rect.bottomleft = self.pos

        # portals
        if pygame.sprite.spritecollide(self, self.portal_group, False):
            self.portal_sound.play()
            # which portal to teleport to
            # left and right
            if self.pos.x > WINDOW_WIDTH // 2:
                self.pos.x = 70
            else:
                self.pos.x = WINDOW_WIDTH - 130
            # top and bottom
            if self.pos.y > WINDOW_HEIGHT // 2:
                self.pos.y = 62
            else:
                self.pos.y = WINDOW_HEIGHT - 132

            self.rect.bottomleft = self.pos

    def check_animation(self):
        """Check which animation to run"""
        # animate the jump
        if self.animation_jump:
            if self.velocity.x > 0:
                self.animate(self.jump_right_sprites, .1)
            else:
                self.animate(self.jump_left_sprites, .1)

        # animate the fire
        if self.animation_fire:
            if self.velocity.x > 0:
                self.animate(self.attack_right_sprites, .2)
            else:
                self.animate(self.attack_left_sprites, .2)

    def jump(self):
        """Jump if on a platform"""
        # jump only if on a platform
        if pygame.sprite.spritecollide(self, self.platform_group, False):
            self.jump_sound.play()
            self.velocity.y = -1 * self.JUMP_SPEED
            self.animation_jump = True

    def fire(self):
        """Fire a bullet"""
        self.slash_sound.play()
        Bullet(self.rect.centerx, self.rect.centery, self.bullet_group, self)
        self.animation_fire = True

    def reset(self):
        """Reset the player position"""
        self.velocity = vector(0, 0)
        self.pos = vector(self.starting_x, self.starting_y)
        self.rect.bottomleft = self.pos

    def animate(self, sprite_list, speed):
        """Animate the player actions"""
        if self.current_sprite < len(sprite_list) - 1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0
            self.animation_jump = False
            self.animation_fire = False

        self.image = sprite_list[int(self.current_sprite)]


class Bullet(pygame.sprite.Sprite):
    """A projectile launched by the player"""

    def __init__(self, x, y, bullet_group, player):
        """Initialize the bullet"""
        super().__init__()

        # set constants
        self.VELOCITY = 20
        self.RANGE = 450

        # load img
        if player.velocity.x > 0:
            self.image = pygame.transform.scale(pygame.image.load(resource_path('resources/images/player/slash.png')),
                                                (31, 31))
        else:
            self.image = pygame.transform.scale(
                pygame.transform.flip(pygame.image.load(resource_path('resources/images/player/slash.png')), True,
                                      False), (31, 31))
            self.VELOCITY = -1 * self.VELOCITY

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.starting_x = x

        bullet_group.add(self)

    def update(self):
        """Update the bullet"""
        self.rect.x += self.VELOCITY

        # destroy bullet if passed its range
        if abs(self.rect.x - self.starting_x) > self.RANGE:
            self.kill()


class Zombie(pygame.sprite.Sprite):
    """An enemy class"""

    def __init__(self, platform_group, portal_group, min_speed, max_speed):
        """Initialize the zombie"""
        super().__init__()

        # set constants
        self.VERTICAL_ACCELERATION = 3  # gravity
        self.RISE_TIME = 2

        # animation frames
        self.walk_right_sprites = []
        self.walk_left_sprites = []
        self.die_right_sprites = []
        self.die_left_sprites = []
        self.rise_right_sprites = []
        self.rise_left_sprites = []

        gender = random.randint(0, 1)
        if gender:
            self.walk_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/girl/walk/Walk (1).png')), (62, 62)))
            self.walk_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/girl/walk/Walk (2).png')), (62, 62)))
            self.walk_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/girl/walk/Walk (3).png')), (62, 62)))
            self.walk_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/girl/walk/Walk (4).png')), (62, 62)))
            self.walk_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/girl/walk/Walk (5).png')), (62, 62)))
            self.walk_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/girl/walk/Walk (6).png')), (62, 62)))
            self.walk_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/girl/walk/Walk (7).png')), (62, 62)))
            self.walk_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/girl/walk/Walk (8).png')), (62, 62)))
            self.walk_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/girl/walk/Walk (9).png')), (62, 62)))
            self.walk_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/girl/walk/Walk (10).png')), (62, 62)))

            for sprite in self.walk_right_sprites:
                self.walk_left_sprites.append(pygame.transform.flip(sprite, True, False))

            self.die_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/girl/dead/Dead (1).png')), (62, 62)))
            self.die_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/girl/dead/Dead (2).png')), (62, 62)))
            self.die_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/girl/dead/Dead (3).png')), (62, 62)))
            self.die_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/girl/dead/Dead (4).png')), (62, 62)))
            self.die_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/girl/dead/Dead (5).png')), (62, 62)))
            self.die_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/girl/dead/Dead (6).png')), (62, 62)))
            self.die_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/girl/dead/Dead (7).png')), (62, 62)))
            self.die_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/girl/dead/Dead (8).png')), (62, 62)))
            self.die_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/girl/dead/Dead (9).png')), (62, 62)))
            self.die_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/girl/dead/Dead (10).png')), (62, 62)))

            for sprite in self.die_right_sprites:
                self.die_left_sprites.append(pygame.transform.flip(sprite, True, False))

            self.rise_right_sprites = list(reversed(self.die_right_sprites))
            self.rise_left_sprites = list(reversed(self.die_left_sprites))
        else:
            self.walk_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/boy/walk/Walk (1).png')), (62, 62)))
            self.walk_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/boy/walk/Walk (2).png')), (62, 62)))
            self.walk_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/boy/walk/Walk (3).png')), (62, 62)))
            self.walk_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/boy/walk/Walk (4).png')), (62, 62)))
            self.walk_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/boy/walk/Walk (5).png')), (62, 62)))
            self.walk_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/boy/walk/Walk (6).png')), (62, 62)))
            self.walk_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/boy/walk/Walk (7).png')), (62, 62)))
            self.walk_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/boy/walk/Walk (8).png')), (62, 62)))
            self.walk_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/boy/walk/Walk (9).png')), (62, 62)))
            self.walk_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/boy/walk/Walk (10).png')), (62, 62)))

            for sprite in self.walk_right_sprites:
                self.walk_left_sprites.append(pygame.transform.flip(sprite, True, False))

            self.die_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/boy/dead/Dead (1).png')), (62, 62)))
            self.die_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/boy/dead/Dead (2).png')), (62, 62)))
            self.die_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/boy/dead/Dead (3).png')), (62, 62)))
            self.die_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/boy/dead/Dead (4).png')), (62, 62)))
            self.die_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/boy/dead/Dead (5).png')), (62, 62)))
            self.die_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/boy/dead/Dead (6).png')), (62, 62)))
            self.die_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/boy/dead/Dead (7).png')), (62, 62)))
            self.die_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/boy/dead/Dead (8).png')), (62, 62)))
            self.die_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/boy/dead/Dead (9).png')), (62, 62)))
            self.die_right_sprites.append(pygame.transform.scale(
                pygame.image.load(resource_path('resources/images/zombie/boy/dead/Dead (10).png')), (62, 62)))

            for sprite in self.die_right_sprites:
                self.die_left_sprites.append(pygame.transform.flip(sprite, True, False))

            self.rise_right_sprites = list(reversed(self.die_right_sprites))
            self.rise_left_sprites = list(reversed(self.die_left_sprites))

        # load img
        self.direction = random.choice([-1, 1])

        self.current_sprite = 0
        if self.direction == -1:
            self.image = self.walk_left_sprites[self.current_sprite]
        else:
            self.image = self.walk_right_sprites[self.current_sprite]

        self.rect = self.image.get_rect()
        self.rect.bottomleft = (random.randint(100, WINDOW_WIDTH - 100), -100)

        # attach sprite group
        self.platform_group = platform_group
        self.portal_group = portal_group

        # animation booleans
        self.animate_death = False
        self.animate_rise = False

        # load sounds
        self.hit_sound = pygame.mixer.Sound(resource_path('resources/sounds/zombie_hit.wav'))
        self.kick_sound = pygame.mixer.Sound(resource_path('resources/sounds/zombie_kick.wav'))
        self.portal_sound = pygame.mixer.Sound(resource_path('resources/sounds/portal_sound.wav'))

        # kinematic vectors
        self.pos = vector(self.rect.x, self.rect.y)
        self.velocity = vector(self.direction * random.randint(min_speed, max_speed), 0)
        self.acceleration = vector(0, self.VERTICAL_ACCELERATION)

        # initial zombie values
        self.is_dead = False
        self.round_time = 0
        self.frame_count = 0

    def update(self):
        """Update the zombie"""
        self.move()
        self.check_collisions()
        self.check_animation()

        # when the zombie raise
        if self.is_dead:
            self.frame_count += 1
            if not self.frame_count % FPS:
                self.round_time += 1
                if self.round_time == self.RISE_TIME:
                    self.animate_rise = True
                    # when the zombie dies the image is the last image so we want to start at index 0
                    self.current_sprite = 0

        # update mask
        self.mask = pygame.mask.from_surface(self.image)

    def move(self):
        """Move the zombie"""

        if not self.is_dead:
            if self.direction == -1:
                self.animate(self.walk_left_sprites, .5)
            else:
                self.animate(self.walk_right_sprites, .5)

            # calculate new kinematic values
            self.velocity += self.acceleration
            # + .5 * acceleration ( physic formula)
            self.pos += self.velocity + .5 * self.acceleration

            # update rect based on kinematic and add wrap around movement
            if self.pos.x < 0:
                self.pos.x = WINDOW_WIDTH
            elif self.pos.x > WINDOW_WIDTH:
                self.pos.x = 0

            self.rect.bottomleft = self.pos

    def check_collisions(self):
        """Check collisions with platforms and portals"""
        # collision check with platform when falling

        collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False, pygame.sprite.collide_mask)
        if collided_platforms:
            self.pos.y = collided_platforms[0].rect.top + 1
            self.velocity.y = 0

        # portals
        if pygame.sprite.spritecollide(self, self.portal_group, False):
            self.portal_sound.play()
            # which portal to teleport to
            # left and right
            if self.pos.x > WINDOW_WIDTH // 2:
                self.pos.x = 70
            else:
                self.pos.x = WINDOW_WIDTH - 130
            # top and bottom
            if self.pos.y > WINDOW_HEIGHT // 2:
                self.pos.y = 62
            else:
                self.pos.y = WINDOW_HEIGHT - 132

            self.rect.bottomleft = self.pos

    def check_animation(self):
        """Check which animation to run"""
        if self.animate_death:
            if self.direction == 1:
                self.animate(self.die_right_sprites, .095)
            else:
                self.animate(self.die_left_sprites, .095)

        if self.animate_rise:
            if self.direction == 1:
                self.animate(self.rise_right_sprites, .095)
            else:
                self.animate(self.rise_left_sprites, .095)

    def animate(self, sprite_list, speed):
        """Animate the player actions"""
        if self.current_sprite < len(sprite_list) - 1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0
            if self.animate_death:
                self.current_sprite = len(sprite_list) - 1
                self.animate_death = False
            if self.animate_rise:
                self.animate_rise = False
                self.is_dead = False
                self.frame_count = 0
                self.round_time = 0

        self.image = sprite_list[int(self.current_sprite)]


class RubyMaker(pygame.sprite.Sprite):
    """A tile that is animated. A Ruby will be generated here"""

    def __init__(self, x, y, main_group):
        """Initialize the Ruby maker"""
        super().__init__()
        # animation frames
        self.ruby_sprites = []

        self.ruby_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/ruby/tile000.png')), (62, 62)))
        self.ruby_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/ruby/tile001.png')), (62, 62)))
        self.ruby_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/ruby/tile002.png')), (62, 62)))
        self.ruby_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/ruby/tile003.png')), (62, 62)))
        self.ruby_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/ruby/tile004.png')), (62, 62)))
        self.ruby_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/ruby/tile005.png')), (62, 62)))
        self.ruby_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/ruby/tile006.png')), (62, 62)))

        # load and get rect
        self.current_sprite = 0
        self.image = self.ruby_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

        # add to main group to draw
        main_group.add(self)

    def update(self):
        """Update the Ruby maker"""
        self.animate(self.ruby_sprites, .3)

    def animate(self, sprite_list, speed):
        """Animate the Ruby maker"""
        if self.current_sprite < len(sprite_list) - 1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0

        self.image = sprite_list[int(self.current_sprite)]


class Ruby(pygame.sprite.Sprite):
    """A Ruby Class"""

    def __init__(self, platform_group, portal_group):
        """Initialize the Ruby"""
        super().__init__()

        # constants
        self.VERTICAL_ACCELERATION = 3  # gravity
        self.HORIZONTAL_VELOCITY = 5

        # animation frames
        self.ruby_sprites = []

        self.ruby_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/ruby/tile000.png')), (62, 62)))
        self.ruby_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/ruby/tile001.png')), (62, 62)))
        self.ruby_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/ruby/tile002.png')), (62, 62)))
        self.ruby_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/ruby/tile003.png')), (62, 62)))
        self.ruby_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/ruby/tile004.png')), (62, 62)))
        self.ruby_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/ruby/tile005.png')), (62, 62)))
        self.ruby_sprites.append(
            pygame.transform.scale(pygame.image.load(resource_path('resources/images/ruby/tile006.png')), (62, 62)))

        # load img
        self.current_sprite = 0
        self.image = self.ruby_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (WINDOW_WIDTH // 2, 100)

        # attach groups
        self.platform_group = platform_group
        self.portal_group = portal_group

        # sounds
        self.portal_sound = pygame.mixer.Sound(resource_path('resources/sounds/portal_sound.wav'))

        # kinematic vectors
        self.pos = vector(self.rect.x, self.rect.y)
        self.velocity = vector(random.choice([-1, 1]) * self.HORIZONTAL_VELOCITY, 0)
        self.acceleration = vector(0, self.VERTICAL_ACCELERATION)

    def update(self):
        """Update the Ruby"""
        self.animate(self.ruby_sprites, .25)
        self.move()
        self.check_collisions()

    def move(self):
        """Move the Ruby"""
        # calculate new kinematic values
        self.velocity += self.acceleration
        # + .5 * acceleration ( physic formula)
        self.pos += self.velocity + .5 * self.acceleration

        # update rect based on kinematic and add wrap around movement
        if self.pos.x < 0:
            self.pos.x = WINDOW_WIDTH
        elif self.pos.x > WINDOW_WIDTH:
            self.pos.x = 0

        self.rect.bottomleft = self.pos

        # update mask
        self.mask = pygame.mask.from_surface(self.image)

    def check_collisions(self):
        """Check for collisions"""
        # collision check with platform when falling

        collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False, pygame.sprite.collide_mask)
        if collided_platforms:
            self.pos.y = collided_platforms[0].rect.top + 1
            self.velocity.y = 0

        # portals
        if pygame.sprite.spritecollide(self, self.portal_group, False, pygame.sprite.collide_mask):
            self.portal_sound.play()
            # which portal to teleport to
            # left and right
            if self.pos.x > WINDOW_WIDTH // 2:
                self.pos.x = 70
            else:
                self.pos.x = WINDOW_WIDTH - 130
            # top and bottom
            if self.pos.y > WINDOW_HEIGHT // 2:
                self.pos.y = 62
            else:
                self.pos.y = WINDOW_HEIGHT - 132

            self.rect.bottomleft = self.pos

    def animate(self, sprite_list, speed):
        """Animate the Ruby"""
        if self.current_sprite < len(sprite_list) - 1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0

        self.image = sprite_list[int(self.current_sprite)]


class Portal(pygame.sprite.Sprite):
    """A class the transport things"""

    def __init__(self, x, y, colour, portal_group):
        """Initialize the portal"""
        super().__init__()

        # animation framess
        self.portal_sprites = []

        # portal animation
        if colour == 'green':
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/green/tile000.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/green/tile001.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/green/tile002.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/green/tile003.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/green/tile004.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/green/tile005.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/green/tile006.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/green/tile007.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/green/tile008.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/green/tile009.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/green/tile010.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/green/tile011.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/green/tile012.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/green/tile013.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/green/tile014.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/green/tile015.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/green/tile016.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/green/tile017.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/green/tile018.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/green/tile019.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/green/tile020.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/green/tile021.png')),
                                       (70, 70)))
        else:
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/purple/tile000.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/purple/tile001.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/purple/tile002.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/purple/tile003.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/purple/tile004.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/purple/tile005.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/purple/tile006.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/purple/tile007.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/purple/tile008.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/purple/tile009.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/purple/tile010.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/purple/tile011.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/purple/tile012.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/purple/tile013.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/purple/tile014.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/purple/tile015.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/purple/tile016.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/purple/tile017.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/purple/tile018.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/purple/tile019.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/purple/tile020.png')),
                                       (70, 70)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load(resource_path('resources/images/portals/purple/tile021.png')),
                                       (70, 70)))

        # load and get rect
        self.current_sprite = random.randint(0, len(self.portal_sprites) - 1)
        self.image = self.portal_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

        # add to the protal group
        portal_group.add(self)

    def update(self):
        """Update the portal"""
        self.animate(self.portal_sprites, .2)

    def animate(self, sprite_list, speed):
        """Animate the portal"""
        if self.current_sprite < len(sprite_list) - 1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0

        self.image = sprite_list[int(self.current_sprite)]


# create sprite groups
main_tile_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()

player_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()

zombie_group = pygame.sprite.Group()

portal_group = pygame.sprite.Group()
ruby_group = pygame.sprite.Group()

# create the tile map
# 0 -> no tile, 1 -> dirt, 2-5 -> platforms, 6 -> ruby maker, 7-8 -> portal, 9 -> player
# 27 row ( some extra ) 45 columns (same)
tile_map = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0],
    [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     8, 0],
    [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
     4, 4],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0],
    [4, 4, 4, 4, 4, 4, 4, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 4, 4,
     4, 4],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0],
    [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
     4, 4],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     7, 0],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
     2, 2],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
     1, 1]
]

# generate tile objects from the tile map
for i in range(len(tile_map)):
    for j in range(len(tile_map[i])):
        # dirt
        if tile_map[i][j] == 1:
            Tile(j * 31, i * 31, 1, main_tile_group)
        # platform
        elif tile_map[i][j] == 2:
            Tile(j * 31, i * 31, 2, main_tile_group, platform_group)
        elif tile_map[i][j] == 3:
            Tile(j * 31, i * 31, 3, main_tile_group, platform_group)
        elif tile_map[i][j] == 4:
            Tile(j * 31, i * 31, 4, main_tile_group, platform_group)
        elif tile_map[i][j] == 5:
            Tile(j * 31, i * 31, 5, main_tile_group, platform_group)
        # ruby maker
        elif tile_map[i][j] == 6:
            RubyMaker(j * 31, i * 31, main_tile_group)
        # portals
        elif tile_map[i][j] == 7:
            Portal(j * 31, i * 31, 'green', portal_group)
        elif tile_map[i][j] == 8:
            Portal(j * 31, i * 31, 'purple', portal_group)
        # player
        elif tile_map[i][j] == 9:
            player = Player(j * 31 - 31, i * 31 + 31, platform_group, portal_group, bullet_group)
            player_group.add(player)

# load background image
bg_img = pygame.transform.scale(pygame.image.load(resource_path('resources/images/background.png')),
                                (WINDOW_WIDTH, WINDOW_HEIGHT))
bg_rect = bg_img.get_rect()
bg_rect.topleft = (0, 0)

# create a game
game = Game(player, zombie_group, platform_group, portal_group, bullet_group, ruby_group)
game.pause_game("Zombie Slayer", "Press 'Enter' to Begin")
pygame.mixer.music.play(-1)

# main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE:
                player.jump()
            if event.key in [pygame.K_UP, pygame.K_w]:
                player.fire()

    # blitting the background
    window.blit(bg_img, bg_rect)

    # draw tiles and update
    main_tile_group.update()
    main_tile_group.draw(window)

    portal_group.update()
    portal_group.draw(window)

    player_group.update()
    player_group.draw(window)

    bullet_group.update()
    bullet_group.draw(window)

    zombie_group.update()
    zombie_group.draw(window)

    ruby_group.update()
    ruby_group.draw(window)

    # update and draw the game
    game.update()
    game.draw()

    # update display and tick the clock
    pygame.display.update()
    clock.tick(FPS)

# quitting
pygame.quit()
