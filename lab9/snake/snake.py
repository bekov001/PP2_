import pygame
import random

# Initialize pygame
pygame.init()

# Constants for the game
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
FPS = 5

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Create screen and set title
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Initial snake setup
snake = [(100, 100), (90, 100), (80, 100)]
direction = "RIGHT"


# Generate food with a timer and weight
def generate_food():
    """
    Randomly generate food at a position not occupied by the snake.
    Each food will have a random timer value (1-10 seconds)
    and a random weight (1, 2, or 3 points).
    Returns a tuple (food_x, food_y, timer, weight).
    """
    while True:
        x = random.randint(0, (WIDTH // CELL_SIZE) - 1) * CELL_SIZE
        y = random.randint(0, (HEIGHT // CELL_SIZE) - 1) * CELL_SIZE
        if (x, y) not in snake:
            timer = random.randint(5, 10) * FPS  # Timer in frames
            weight = random.choice([1, 2, 3])  # Food points
            return [x, y, timer, weight]


# Initial food generation
food = generate_food()

# Score and level tracking
score = 0
level = 1

# Game variables
running = True
clock = pygame.time.Clock()

# Main game loop
while running:
    # Fill screen with background color
    screen.fill(BLACK)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != "DOWN":
                direction = "UP"
            elif event.key == pygame.K_DOWN and direction != "UP":
                direction = "DOWN"
            elif event.key == pygame.K_LEFT and direction != "RIGHT":
                direction = "LEFT"
            elif event.key == pygame.K_RIGHT and direction != "LEFT":
                direction = "RIGHT"

    # Move snake's head based on direction
    head_x, head_y = snake[0]
    if direction == "UP":
        head_y -= CELL_SIZE
    elif direction == "DOWN":
        head_y += CELL_SIZE
    elif direction == "LEFT":
        head_x -= CELL_SIZE
    elif direction == "RIGHT":
        head_x += CELL_SIZE

    # Check for wall collision
    if head_x < 0 or head_x >= WIDTH or head_y < 0 or head_y >= HEIGHT:
        print("Game Over! Snake hit the wall.")
        running = False

    # Check for self-collision
    if (head_x, head_y) in snake:
        print("Game Over! Snake hit itself.")
        running = False

    # Insert new head position at the front of the snake
    snake.insert(0, (head_x, head_y))

    # Check if snake eats the food
    if (head_x, head_y) == (food[0], food[1]):
        score += food[3]  # Add food weight to score
        food = generate_food()  # Generate a new food
        if score % 3 == 0:
            level += 1
            FPS += 2  # Increase speed after every 3 points
    else:
        # Remove last segment of snake (if no food was eaten)
        snake.pop()

    # Decrease the food timer
    food[2] -= 1
    if food[2] <= 0:
        # Generate new food if timer expires
        food = generate_food()

    # Draw the snake
    for segment in snake:
        pygame.draw.rect(screen, GREEN,
                         (segment[0], segment[1], CELL_SIZE, CELL_SIZE))

    # Draw the food
    pygame.draw.rect(screen, RED if food[3] == 1 else BLUE,
                     (food[0], food[1], CELL_SIZE, CELL_SIZE))

    # Render score and level
    font = pygame.font.Font(None, 30)
    score_text = font.render(f"Score: {score}  Level: {level}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Update the display
    pygame.display.update()

    # Control the game speed
    clock.tick(FPS)

# Quit pygame
pygame.quit()
