import pygame, sys
from pygame.locals import *
import random, time

# Initializing pygame
pygame.init()

# Setting up FPS (Frames Per Second)
FPS = 60
FramePerSec = pygame.time.Clock()

# Creating colors using RGB values
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)  # Gold color for special coins
SILVER = (192, 192, 192)  # Silver color for regular coins

# Game settings
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 5
SCORE = 0
COINS_COLLECTED = 0  # Counter to track collected coins

# Speed increase threshold - increase enemy speed every N coins
SPEED_BOOST_THRESHOLD = 5  # Increase speed every 5 coins collected
SPEED_BOOST_AMOUNT = 1  # How much to increase speed by

# Setting up Fonts
font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over = font.render("Game Over", True, BLACK)

# Load background image
background = pygame.image.load("images/AnimatedStreet.png")

# Create and configure game display window
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Coin Collector")


# Enemy class - obstacles the player must avoid
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        """Initialize enemy with image and random position at top of screen"""
        super().__init__()
        self.image = pygame.image.load("images/Enemy.png")
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)
        self.speed = SPEED  # Initialize with the default speed

    def move(self):
        """Moves the enemy downwards and respawns at a random position when out of screen."""
        global SCORE
        # Move enemy down based on current speed
        self.rect.move_ip(0, self.speed)

        # Reset enemy when it moves off screen
        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1  # Increase score when an enemy passes
            self.rect.top = 0
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def increase_speed(self, amount):
        """Increase the enemy's movement speed"""
        self.speed += amount


# Player class - controlled by the user
class Player(pygame.sprite.Sprite):
    def __init__(self):
        """Initialize player with image and starting position"""
        super().__init__()
        self.image = pygame.image.load("images/Player.png")
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)  # Position near bottom

    def move(self):
        """Handles player movement with keyboard and enforces screen boundaries"""
        pressed_keys = pygame.key.get_pressed()

        # Move left if left arrow pressed and not at screen edge
        if self.rect.left > 0 and pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)

        # Move right if right arrow pressed and not at screen edge
        if self.rect.right < SCREEN_WIDTH and pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)


# Coin class - collectible items with different values
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        """Initialize coin with random weight/value and position"""
        super().__init__()

        # Randomly determine if this is a special (gold) coin or regular (silver) coin
        # Gold coins are less common (25% chance) but worth more points
        self.is_special = random.random() < 0.25

        # Set coin value based on type
        self.value = 3 if self.is_special else 1

        # Load base coin image
        self.base_image = pygame.image.load("images/coin.png")

        # Create colored coin based on type (gold or silver)
        self.image = self.base_image.copy()

        # Color the coin surface based on type
        if self.is_special:
            # Gold coin (worth more)
            pygame.Surface.fill(self.image, GOLD, special_flags=pygame.BLEND_MULT)
        else:
            # Silver coin (regular value)
            pygame.Surface.fill(self.image, SILVER, special_flags=pygame.BLEND_MULT)

        # Set the coin's size based on value (bigger = worth more)
        if self.is_special:
            # Make special coins slightly larger
            new_size = (int(self.base_image.get_width() * 1.2),
                        int(self.base_image.get_height() * 1.2))
            self.image = pygame.transform.scale(self.image, new_size)

        # Set up position
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

        # Randomize movement speed (some coins fall faster than others)
        self.speed = (SPEED // 2) + random.randint(-1, 2)
        if self.speed < 1:  # Ensure minimum speed
            self.speed = 1

    def move(self):
        """Moves the coin downwards and respawns randomly when out of screen"""
        self.rect.move_ip(0, self.speed)

        # Reset coin when it moves off screen
        if self.rect.top > SCREEN_HEIGHT:
            self.reset_position()

    def reset_position(self):
        """Reset coin to a new random position at the top of the screen"""
        self.rect.top = 0
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

        # Randomize coin type and value on respawn
        self.is_special = random.random() < 0.25
        self.value = 3 if self.is_special else 1

        # Refresh coin appearance
        if self.is_special:
            pygame.Surface.fill(self.image, GOLD, special_flags=pygame.BLEND_MULT)
            new_size = (int(self.base_image.get_width() * 1.2),
                        int(self.base_image.get_height() * 1.2))
            self.image = pygame.transform.scale(self.image, new_size)
        else:
            pygame.Surface.fill(self.image, SILVER, special_flags=pygame.BLEND_MULT)
            self.image = pygame.transform.scale(self.base_image.copy(),
                                                (self.base_image.get_width(),
                                                 self.base_image.get_height()))


# Setting up initial game sprites
P1 = Player()
E1 = Enemy()

# Create multiple coins with different weights
coins = pygame.sprite.Group()
for _ in range(3):  # Create 3 coins with different properties
    new_coin = Coin()
    coins.add(new_coin)

# Creating Sprite Groups for collision detection and rendering
enemies = pygame.sprite.Group()
enemies.add(E1)

all_sprites = pygame.sprite.Group()
all_sprites.add(P1, E1)
for coin in coins:
    all_sprites.add(coin)

# Adding a new User event for general timing
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)  # Trigger every 1 second

# Track when the last enemy speed boost occurred
last_speed_boost = 0

# Game Loop
while True:
    # Process game events
    for event in pygame.event.get():
        if event.type == INC_SPEED:
            SPEED += 0.1  # Gradually increase base game speed over time
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Draw background on the display surface
    DISPLAYSURF.blit(background, (0, 0))

    # Display Score and Coins Collected as HUD elements
    score_display = font_small.render(f"Score: {SCORE}", True, BLACK)
    coin_display = font_small.render(f"Coins: {COINS_COLLECTED}", True, BLACK)
    DISPLAYSURF.blit(score_display, (10, 10))  # Top left corner
    DISPLAYSURF.blit(coin_display, (SCREEN_WIDTH - 100, 10))  # Top right corner

    # Move all game sprites according to their movement patterns
    P1.move()
    E1.move()
    for coin in coins:
        coin.move()

    # Draw all sprites on the screen
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)

    # Collision detection for coins
    # Check if player has collided with any coin
    coin_collisions = pygame.sprite.spritecollide(P1, coins, False)
    for coin in coin_collisions:
        # Add coin's value to total collected
        COINS_COLLECTED += coin.value

        # Check if player has reached a speed boost threshold
        if (COINS_COLLECTED // SPEED_BOOST_THRESHOLD) > last_speed_boost:
            # Increase enemy speed when player reaches coin threshold
            E1.increase_speed(SPEED_BOOST_AMOUNT)
            last_speed_boost = COINS_COLLECTED // SPEED_BOOST_THRESHOLD

            # Display speed boost notification
            boost_message = font_small.render("Speed Boost!", True, RED)
            DISPLAYSURF.blit(boost_message, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2))
            pygame.display.update()  # Force an immediate update to show message

        # Reset coin to new position after collection
        coin.reset_position()

    # Collision detection for enemy - game over if player hits enemy
    if pygame.sprite.spritecollideany(P1, enemies):
        # Play crash sound
        pygame.mixer.Sound('images/crash.wav').play()
        time.sleep(0.5)  # Brief pause after collision

        # Show game over screen
        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over, (30, 250))
        final_score = font_small.render(f"Final Score: {SCORE}", True, WHITE)
        final_coins = font_small.render(f"Coins Collected: {COINS_COLLECTED}", True, WHITE)
        DISPLAYSURF.blit(final_score, (SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2))
        DISPLAYSURF.blit(final_coins, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 30))

        # Update display, wait, then exit
        pygame.display.update()
        time.sleep(2)
        pygame.quit()
        sys.exit()

    # Update the display and maintain frame rate
    pygame.display.update()
    FramePerSec.tick(FPS)
