import pygame
import random

pygame.init()

WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
FPS = 5

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

snake = [(100, 100), (90, 100), (80, 100)]
direction = "RIGHT"

def generate_food():
    while True:
        x = random.randint(0, (WIDTH // CELL_SIZE) - 1) * CELL_SIZE
        y = random.randint(0, (HEIGHT // CELL_SIZE) - 1) * CELL_SIZE
        if (x, y) not in snake:
            return x, y

food = generate_food()

score = 0
level = 1

running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BLACK)

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

    head_x, head_y = snake[0]
    if direction == "UP":
        head_y -= CELL_SIZE
    elif direction == "DOWN":
        head_y += CELL_SIZE
    elif direction == "LEFT":
        head_x -= CELL_SIZE
    elif direction == "RIGHT":
        head_x += CELL_SIZE

    if head_x < 0 or head_x >= WIDTH or head_y < 0 or head_y >= HEIGHT:
        print("Game Over! Snake hit the wall.")
        running = False

    if (head_x, head_y) in snake:
        print("Game Over! Snake hit itself.")
        running = False

    snake.insert(0, (head_x, head_y))

    if (head_x, head_y) == food:
        score += 1
        food = generate_food()
        if score % 3 == 0:
            level += 1
            FPS += 2
    else:
        snake.pop()

    for segment in snake:
        pygame.draw.rect(screen, GREEN,
                         (segment[0], segment[1], CELL_SIZE, CELL_SIZE))

    pygame.draw.rect(screen, RED, (food[0], food[1], CELL_SIZE, CELL_SIZE))

    font = pygame.font.Font(None, 30)
    score_text = font.render(f"Score: {score}  Level: {level}", True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()