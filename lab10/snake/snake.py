import pygame
import random
import psycopg2
import sys
import os
import configparser # Import the configparser module
import time # Import the time module (though we'll use pygame's timer)

# --- Configuration Loading ---

def load_db_config(filename='database.ini', section='postgresql'):
    """Reads database configuration from an INI file."""
    parser = configparser.ConfigParser()
    if not os.path.exists(filename):
        print(f"FATAL: Configuration file '{filename}' not found.")
        print("Please create it in the same directory as the script with a [postgresql] section.")
        sys.exit(1)

    try:
        parser.read(filename)
        db_config = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db_config[param[0]] = param[1]
            # Basic check for essential keys
            required_keys = ['host', 'port', 'database', 'user', 'password']
            if not all(key in db_config for key in required_keys):
                missing = [key for key in required_keys if key not in db_config]
                print(f"FATAL: Missing required keys in '{filename}' section '[{section}]': {missing}")
                sys.exit(1)
            return db_config
        else:
            print(f"FATAL: Section '[{section}]' not found in the '{filename}' file.")
            sys.exit(1)
    except configparser.Error as e:
        print(f"FATAL: Error reading configuration file '{filename}': {e}")
        sys.exit(1)
    except Exception as e:
         print(f"FATAL: An unexpected error occurred while loading config: {e}")
         sys.exit(1)


# --- Constants (Removed DB_CONFIG dictionary) ---
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
BASE_FPS = 5
INITIAL_DELAY_MS = 2000 # 2 seconds in milliseconds

# --- Colors ---
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)

# --- Database Functions (Using psycopg2 and loaded config) ---

def get_db_connection():
    """Establishes a connection to the PostgreSQL database using config from file."""
    config = load_db_config() # Load config when needed
    try:
        conn = psycopg2.connect(**config) # Use unpacked dictionary from config
        return conn
    except psycopg2.OperationalError as e:
        # Provide more context in error message
        # Use .get() for safer access in case keys are missing despite checks
        db_name = config.get('database', 'N/A')
        host = config.get('host', 'N/A')
        port = config.get('port', 'N/A')
        print(f"FATAL: Could not connect to PostgreSQL database '{db_name}' on {host}:{port}.")
        print(f"Error details: {e}")
        print(f"\nPlease check the connection details in 'database.ini' and ensure the PostgreSQL server is running.")
        sys.exit(1)
    except Exception as e: # Catch other potential errors during connect
         print(f"FATAL: An unexpected error occurred during DB connection: {e}")
         sys.exit(1)


def init_db():
    """Initializes the PostgreSQL database table if it doesn't exist."""
    sql = """
        CREATE TABLE IF NOT EXISTS user_data (
            username TEXT PRIMARY KEY,
            high_score INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1
        );
    """
    try:
        # Connection is established *inside* the 'with' block now
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
        print("Database table 'user_data' checked/created successfully.")
    except (psycopg2.Error, Exception) as e:
        print(f"Database error during table initialization: {e}")
        # If connection fails, get_db_connection exits. If table creation fails,
        # subsequent DB calls will likely fail too, but we let it continue for now.


def get_user_data(username):
    """Fetches high score and level for a given username from PostgreSQL."""
    sql = "SELECT high_score, level FROM user_data WHERE username = %s;"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (username,))
                data = cursor.fetchone()
                if data:
                    print(f"Welcome back, {username}! Starting at Level {data[1]}. High Score: {data[0]}")
                    return {"high_score": data[0], "level": data[1]}
                else:
                    print(f"Welcome, new player: {username}!")
                    # Ensure new players start at level 1, regardless of DB default
                    return {"high_score": 0, "level": 1}
    except (psycopg2.Error, Exception) as e:
        print(f"Database error fetching user data for '{username}': {e}")
        print("Starting as a new player (Level 1, Score 0) due to fetch error.")
        # Return default values if fetch fails after connection is made
        return {"high_score": 0, "level": 1}

def save_user_data(username, current_score, current_level):
    """Saves or updates the user's high score and level in PostgreSQL."""
    select_sql = "SELECT high_score, level FROM user_data WHERE username = %s;"
    update_sql = "UPDATE user_data SET high_score = %s, level = %s WHERE username = %s;"
    insert_sql = "INSERT INTO user_data (username, high_score, level) VALUES (%s, %s, %s);"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(select_sql, (username,))
                data = cursor.fetchone()
                if data:
                    saved_high_score, saved_level = data[0], data[1]
                    new_high_score = max(current_score, saved_high_score)
                    # Ensure level doesn't exceed MAX_LEVEL when saving
                    new_level = min(max(current_level, saved_level), MAX_LEVEL)
                    if new_high_score > saved_high_score or new_level > saved_level:
                         cursor.execute(update_sql, (new_high_score, new_level, username))
                         print(f"Data updated for {username}: Score={new_high_score}, Level={new_level}")
                    else:
                         print(f"No update needed for {username} (Current: Score={current_score}, Level={current_level} | Saved: Score={saved_high_score}, Level={saved_level})")
                else:
                    # Ensure level doesn't exceed MAX_LEVEL on first save
                    safe_level = min(current_level, MAX_LEVEL)
                    cursor.execute(insert_sql, (username, current_score, safe_level))
                    print(f"New user data saved for {username}: Score={current_score}, Level={safe_level}")
    except (psycopg2.Error, Exception) as e:
        print(f"Database error saving user data for '{username}': {e}")


# --- Level Definitions ---
LEVELS = {
    1: {"fps": 5, "walls": []},
    2: {"fps": 6, "walls": []},
    3: {"fps": 7, "walls": [(13, 9, 4, 2)]}, # Example wall: (startX, startY, width, height) in cells
    4: {"fps": 8, "walls": [(2, 2, 26, 1), (2, 17, 26, 1), (2, 3, 1, 14), (27, 3, 1, 14)]}, # Box outline
    5: {"fps": 10, "walls": [(5, 5, 1, 10), (24, 5, 1, 10), (10, 2, 10, 1), (10, 17, 10, 1)]}, # Inner cross
}
MAX_LEVEL = max(LEVELS.keys())

# --- Game Setup ---
pygame.init()
pygame.font.init() # Explicitly initialize font module

while True:
    current_username = input("Enter your username: ").strip()
    if current_username: break
    else: print("Username cannot be empty.")

init_db() # Check connection and table existence using config file

user_data = get_user_data(current_username)
# Ensure user_data is never None after get_user_data (it returns defaults on error/new)
score = 0
level = user_data["level"] # Already capped at MAX_LEVEL in get/save if needed
level = min(level, MAX_LEVEL) # Still good practice to cap here too

# --- Game Variables ---
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(f"Snake Game (PG/INI) - {current_username}")
clock = pygame.time.Clock()

initial_snake_pos = [(WIDTH // 2, HEIGHT // 2),
                     (WIDTH // 2 - CELL_SIZE, HEIGHT // 2),
                     (WIDTH // 2 - 2 * CELL_SIZE, HEIGHT // 2)]
snake = list(initial_snake_pos)
direction = "RIGHT" # Initial direction

current_walls_pixels = []
current_wall_coords = set() # Store wall coordinates for collision checks
FPS = BASE_FPS # Base FPS, will be updated by load_level

# --- Functions load_level, generate_food ---
def load_level(level_num):
    global FPS, current_walls_pixels, current_wall_coords, snake, direction, food
    level_num = min(level_num, MAX_LEVEL) # Ensure we don't exceed defined levels
    config = LEVELS[level_num]
    FPS = config["fps"]
    print(f"--- Loading Level {level_num} (FPS: {FPS}) ---")

    # Reset snake to center, clear walls
    snake = list(initial_snake_pos)
    direction = "RIGHT"
    current_walls_pixels = []
    current_wall_coords = set()

    for wall in config["walls"]:
        wx, wy, ww, wh = wall # Wall definition: startX, startY, width, height (in cells)
        # Create a Rect for drawing
        pixel_rect = pygame.Rect(wx * CELL_SIZE, wy * CELL_SIZE, ww * CELL_SIZE, wh * CELL_SIZE)
        current_walls_pixels.append(pixel_rect)
        # Add individual cell coordinates for collision detection
        for r in range(wy, wy + wh):
            for c in range(wx, wx + ww):
                current_wall_coords.add((c * CELL_SIZE, r * CELL_SIZE))

    # Regenerate food ensuring it's not inside new walls or snake
    food = generate_food()

def generate_food():
    while True:
        x = random.randint(0, (WIDTH // CELL_SIZE) - 1) * CELL_SIZE
        y = random.randint(0, (HEIGHT // CELL_SIZE) - 1) * CELL_SIZE
        # Check collision with snake body AND wall coordinates
        if (x, y) not in snake and (x, y) not in current_wall_coords:
            # Food properties: position x, y, timer, weight (score value)
            timer = random.randint(5, 10) * FPS # Timer based on current FPS
            weight = random.choice([1, 2, 3]) # Score value
            return [x, y, timer, weight]

# Load initial level setup
load_level(level)
# Food is generated by load_level

running = True
paused = False
initial_delay_active = True # <<< ADDED: Flag for initial delay
start_time = pygame.time.get_ticks() # <<< ADDED: Record start time

# --- Font Setup (Define fonts once) ---
try:
    score_font = pygame.font.Font(None, 30)
    help_font = pygame.font.Font(None, 24)
    message_font = pygame.font.Font(None, 50) # For Pause/Ready messages
except pygame.error as e:
    print(f"FATAL: Could not load default font: {e}")
    pygame.quit()
    sys.exit(1)


# --- Main Game Loop ---
while running:
    # --- Event Handling (Always run) ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not initial_delay_active: # Can only pause after initial delay
                    paused = not paused
                    print("Game Paused." if paused else "Game Resumed.")
            elif event.key == pygame.K_s:
                 print("Saving game state to PostgreSQL (using config from database.ini)...")
                 save_user_data(current_username, score, level)
                 print("Game saved. Exiting.")
                 running = False
            # Direction changes are allowed even during pause/delay,
            # but only acted upon when game is active
            elif not paused: # Direction change only if not paused
                # Check initial_delay_active here if you DON'T want directions queued during delay
                # if not initial_delay_active:
                if event.key == pygame.K_UP and direction != "DOWN": direction = "UP"
                elif event.key == pygame.K_DOWN and direction != "UP": direction = "DOWN"
                elif event.key == pygame.K_LEFT and direction != "RIGHT": direction = "LEFT"
                elif event.key == pygame.K_RIGHT and direction != "LEFT": direction = "RIGHT"

    if not running: break # Exit loop immediately if quit/save event processed

    # --- Initial Delay Logic ---
    if initial_delay_active:
        current_time = pygame.time.get_ticks()
        if current_time - start_time >= INITIAL_DELAY_MS:
            initial_delay_active = False # Delay over
            print("Get Ready... Go!")
        else:
            # --- Draw Game State During Delay ---
            screen.fill(BLACK)
            # Draw snake in starting position
            for segment in snake: pygame.draw.rect(screen, GREEN, (segment[0], segment[1], CELL_SIZE, CELL_SIZE))
            # Draw initial food
            food_color = {1: RED, 2: BLUE, 3: YELLOW}.get(food[3], RED)
            pygame.draw.rect(screen, food_color, (food[0], food[1], CELL_SIZE, CELL_SIZE))
            # Draw walls
            for wall_rect in current_walls_pixels: pygame.draw.rect(screen, GRAY, wall_rect)
            # Draw Score/Level Info
            score_text = score_font.render(f"User: {current_username} | Score: {score} | Level: {level} | Speed: {FPS}fps", True, WHITE)
            screen.blit(score_text, (10, 10))
            # Draw Help Text
            help_text = help_font.render("SPACE: Pause | S: Save & Quit", True, WHITE)
            help_rect = help_text.get_rect(bottomright=(WIDTH - 10, HEIGHT - 10))
            screen.blit(help_text, help_rect)
            # Draw "Get Ready" message
            ready_text = message_font.render("Get Ready!", True, YELLOW)
            ready_rect = ready_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(ready_text, ready_rect)

            pygame.display.update()
            clock.tick(FPS) # Keep ticking at game FPS for smooth display
            continue # Skip the rest of the loop (movement, game logic)

    # --- Pause Logic ---
    if paused:
        # Draw Paused Message overlaying the current game state
        pause_text = message_font.render("PAUSED", True, WHITE)
        pause_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        # Create a semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128)) # Black with 50% alpha
        screen.blit(overlay, (0, 0))
        screen.blit(pause_text, pause_rect)

        pygame.display.update()
        clock.tick(10) # Tick slower during pause
        continue # Skip movement and game logic

    # --- Game Logic (Movement, Collision, Food, Level Up) ---
    # This section only runs if not paused AND initial delay is over

    # Move Snake
    head_x, head_y = snake[0]
    if direction == "UP": head_y -= CELL_SIZE
    elif direction == "DOWN": head_y += CELL_SIZE
    elif direction == "LEFT": head_x -= CELL_SIZE
    elif direction == "RIGHT": head_x += CELL_SIZE
    new_head = (head_x, head_y)

    # Check Collisions
    game_over = False
    reason = ""
    if head_x < 0 or head_x >= WIDTH or head_y < 0 or head_y >= HEIGHT:
        game_over = True
        reason = "Hit screen boundary."
    elif new_head in current_wall_coords:
        game_over = True
        reason = "Hit wall."
    elif new_head in snake: # Check collision with self *after* moving
        game_over = True
        reason = "Hit self."

    if game_over:
        print("Game Over!")
        print(f"Reason: {reason}")
        running = False # Set running to False to exit loop
        # No 'break' here, let the drawing happen one last time if needed, then loop condition checks running=False
    else:
        # Insert new head
        snake.insert(0, new_head)

        # Check Food Collision
        if new_head == (food[0], food[1]):
            score += food[3]
            print(f"Ate food! Score: {score}")
            food = generate_food() # Generate new food

            # Check Level Up / Speed Increase
            # Level up every 5 points *earned on this level* might be better,
            # but original logic is based on total score % 5 == 0. Let's keep that.
            if score > 0 and score % 5 == 0:
                 previous_level = level
                 if level < MAX_LEVEL:
                     level += 1
                     load_level(level) # This resets snake, generates food, sets FPS
                     # Start the initial delay again for the new level? (Optional - not doing this now)
                     # initial_delay_active = True
                     # start_time = pygame.time.get_ticks()
                 elif previous_level == MAX_LEVEL: # Only increase speed if already at max level
                     FPS += 1
                     print(f"Max level reached, increasing speed! New FPS: {FPS}")
                 # No 'else' needed, food is generated by load_level or eating

        else:
            # Didn't eat food, remove tail segment
            snake.pop()

        # Update Food Timer
        food[2] -= 1
        if food[2] <= 0:
            print("Food expired!")
            food = generate_food()

    # --- Drawing (Main Game) ---
    # This section runs if the game is active (not paused, not in initial delay)
    # OR if it's the very last frame after game_over is set true
    screen.fill(BLACK)

    # Draw Walls
    for wall_rect in current_walls_pixels: pygame.draw.rect(screen, GRAY, wall_rect)

    # Draw Snake
    for segment in snake: pygame.draw.rect(screen, GREEN, (segment[0], segment[1], CELL_SIZE, CELL_SIZE))

    # Draw Food
    food_color = {1: RED, 2: BLUE, 3: YELLOW}.get(food[3], RED)
    pygame.draw.rect(screen, food_color, (food[0], food[1], CELL_SIZE, CELL_SIZE))

    # Draw Score/Level Info
    score_text = score_font.render(f"User: {current_username} | Score: {score} | Level: {level} | Speed: {FPS}fps", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Draw Help Text
    help_text = help_font.render("SPACE: Pause | S: Save & Quit", True, WHITE)
    help_rect = help_text.get_rect(bottomright=(WIDTH - 10, HEIGHT - 10))
    screen.blit(help_text, help_rect)

    # Update Display
    pygame.display.update()

    # Tick Clock
    clock.tick(FPS)

# --- Game Over or Quit ---
print("-" * 20)
# Ensure final state is saved only if the game didn't exit due to a fatal error before loop
if 'current_username' in locals() and current_username: # Check if username was set
    print(f"Final Score for {current_username}: {score}, Final Level: {level}")
    # Save final state using config from INI
    save_user_data(current_username, score, level)
else:
    print("Game ended before username was fully initialized or due to an early error.")

pygame.quit()
print("Game closed.")
sys.exit()