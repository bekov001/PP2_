import pygame
import math

# Initialize pygame
pygame.init()

# Screen settings
fps = 60  # Frames per second for smooth animation
timer = pygame.time.Clock()  # Clock to control game speed
WIDTH = 800  # Screen width
HEIGHT = 600  # Screen height
active_figure = 0  # Active drawing tool (0=circle by default)
active_color = (255, 255, 255)  # Default color is white (RGB)
color_selected = False  # Track if a color has been selected

# Set up the display window
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption("Paint")  # Set the window title
painting = []  # List to store all drawing actions

# Initialize font for messages
font = pygame.font.Font(None, 36)


def draw_menu(color):
    """Draws the top menu with color options, brush shapes, and buttons."""
    # Draw the menu background
    pygame.draw.rect(screen, 'gray', [0, 0, WIDTH, 70])
    pygame.draw.line(screen, 'black', (0, 70), (WIDTH, 70), 3)

    # Basic brush selection tools
    # Circle brush button
    circle_brush = [pygame.draw.rect(screen, 'black', [10, 10, 50, 50]), 0]
    pygame.draw.circle(screen, 'white', (35, 35), 20)
    pygame.draw.circle(screen, 'black', (35, 35), 18)

    # Rectangle brush button
    rect_brush = [pygame.draw.rect(screen, 'black', [70, 10, 50, 50]), 1]
    pygame.draw.rect(screen, 'white', [76.5, 26, 37, 20], 2)

    # Square brush button
    square_brush = [pygame.draw.rect(screen, 'black', [130, 10, 50, 50]), 2]
    pygame.draw.rect(screen, 'white', [140, 20, 30, 30], 2)

    # Right triangle brush button
    right_triangle = [pygame.draw.rect(screen, 'black', [190, 10, 50, 50]), 3]
    pygame.draw.polygon(screen, 'white', [(195, 45), (235, 45), (195, 15)], 2)

    # Equilateral triangle brush button
    eq_triangle = [pygame.draw.rect(screen, 'black', [250, 10, 50, 50]), 4]
    pygame.draw.polygon(screen, 'white', [(275, 15), (255, 45), (295, 45)], 2)

    # Rhombus brush button
    rhombus = [pygame.draw.rect(screen, 'black', [310, 10, 50, 50]), 5]
    pygame.draw.polygon(screen, 'white', [(335, 15), (350, 35), (335, 55), (320, 35)], 2)

    # Collect all brush options
    brush_list = [circle_brush, rect_brush, square_brush, right_triangle, eq_triangle, rhombus]

    # Current active color indicator
    pygame.draw.circle(screen, color, (400, 35), 30)
    pygame.draw.circle(screen, 'dark gray', (400, 35), 30, 3)

    # Eraser button (X icon)
    eraser_rect = pygame.draw.rect(screen, (200, 200, 200), [WIDTH - 150, 10, 40, 40])
    pygame.draw.line(screen, 'black', (WIDTH - 140, 15), (WIDTH - 120, 35), 5)
    pygame.draw.line(screen, 'black', (WIDTH - 120, 15), (WIDTH - 140, 35), 5)

    # Color palette with various color options
    blue = pygame.draw.rect(screen, (0, 0, 255), [WIDTH - 35, 10, 25, 25])
    red = pygame.draw.rect(screen, (255, 0, 0), [WIDTH - 35, 35, 25, 25])
    green = pygame.draw.rect(screen, (0, 255, 0), [WIDTH - 60, 10, 25, 25])
    yellow = pygame.draw.rect(screen, (255, 255, 0), [WIDTH - 60, 35, 25, 25])
    teal = pygame.draw.rect(screen, (0, 255, 255), [WIDTH - 85, 10, 25, 25])
    purple = pygame.draw.rect(screen, (255, 0, 255), [WIDTH - 85, 35, 25, 25])
    black = pygame.draw.rect(screen, (0, 0, 0), [WIDTH - 110, 10, 25, 25])

    # Group color options and their RGB values
    color_rect = [blue, red, green, yellow, teal, purple, black, eraser_rect]
    rgb_list = [(0, 0, 255), (255, 0, 0), (0, 255, 0), (255, 255, 0),
                (0, 255, 255), (255, 0, 255), (0, 0, 0), (255, 255, 255)]  # Eraser is white

    # Clear button
    clear_button = pygame.draw.rect(screen, (173, 216, 230), [450, 10, 80, 50])
    pygame.draw.rect(screen, 'black', [450, 10, 80, 50], 2)
    font = pygame.font.Font(None, 24)
    text = font.render("Clear", True, (0, 0, 0))
    text_rect = text.get_rect(center=(490, 35))
    screen.blit(text, text_rect)

    return brush_list, color_rect, rgb_list, clear_button


def draw_painting(paints):
    """Draws all shapes from the stored paint list."""
    for color, pos, figure in paints:
        if figure == -1:  # Eraser
            pygame.draw.rect(screen, (255, 255, 255), [pos[0] - 20, pos[1] - 20, 40, 40])
        elif figure == 0:  # Circle
            pygame.draw.circle(screen, color, pos, 20, 2)
        elif figure == 1:  # Rectangle
            pygame.draw.rect(screen, color, [pos[0] - 15, pos[1] - 15, 37, 20], 2)
        elif figure == 2:  # Square
            pygame.draw.rect(screen, color, [pos[0] - 15, pos[1] - 15, 30, 30], 2)
        elif figure == 3:  # Right triangle
            pygame.draw.polygon(screen, color, [(pos[0], pos[1]), (pos[0] + 40, pos[1]), (pos[0], pos[1] - 40)], 2)
        elif figure == 4:  # Equilateral triangle
            # Calculate vertices for equilateral triangle
            side = 40
            height = side * math.sqrt(3) / 2
            pygame.draw.polygon(screen, color, [
                (pos[0], pos[1] - 2 * height / 3),  # Top vertex
                (pos[0] - side / 2, pos[1] + height / 3),  # Bottom left
                (pos[0] + side / 2, pos[1] + height / 3)  # Bottom right
            ], 2)
        elif figure == 5:  # Rhombus
            # Draw rhombus (diamond shape)
            size = 20
            pygame.draw.polygon(screen, color, [
                (pos[0], pos[1] - size),  # Top
                (pos[0] + size, pos[1]),  # Right
                (pos[0], pos[1] + size),  # Bottom
                (pos[0] - size, pos[1])  # Left
            ], 2)


# Main game loop
run = True
while run:
    # Control game speed
    timer.tick(fps)
    screen.fill("white")  # Clear screen with white background

    # Display initial guidance message
    if not color_selected and len(painting) == 0:
        text = font.render("Choose a color first", True, (0, 0, 0))
        text_rect = text.get_rect(center=(400, 350))  # Center in the canvas area
        screen.blit(text, text_rect)

    # Get mouse position and click state
    mouse = pygame.mouse.get_pos()
    left_click = pygame.mouse.get_pressed()[0]

    # Create menu and get interactive elements
    brushes, colors, rgbs, clear_button = draw_menu(active_color)

    # Add shapes when clicking in the canvas area
    if left_click and mouse[1] > 85:  # Only draw below menu bar
        painting.append((active_color, mouse, active_figure))

    # Render all existing drawings
    draw_painting(painting)

    # Show cursor preview (what will be drawn on click)
    if mouse[1] > 85:  # Only show preview below menu bar
        if active_figure == -1:  # Eraser
            pygame.draw.rect(screen, (200, 200, 200), [mouse[0] - 20, mouse[1] - 20, 40, 40], 2)
        elif active_figure == 0:  # Circle
            pygame.draw.circle(screen, active_color, mouse, 20, 2)
        elif active_figure == 1:  # Rectangle
            pygame.draw.rect(screen, active_color, [mouse[0] - 15, mouse[1] - 15, 37, 20], 2)
        elif active_figure == 2:  # Square
            pygame.draw.rect(screen, active_color, [mouse[0] - 15, mouse[1] - 15, 30, 30], 2)
        elif active_figure == 3:  # Right triangle
            pygame.draw.polygon(screen, active_color,
                                [(mouse[0], mouse[1]), (mouse[0] + 40, mouse[1]), (mouse[0], mouse[1] - 40)], 2)
        elif active_figure == 4:  # Equilateral triangle
            side = 40
            height = side * math.sqrt(3) / 2
            pygame.draw.polygon(screen, active_color, [
                (mouse[0], mouse[1] - 2 * height / 3),
                (mouse[0] - side / 2, mouse[1] + height / 3),
                (mouse[0] + side / 2, mouse[1] + height / 3)
            ], 2)
        elif active_figure == 5:  # Rhombus
            size = 20
            pygame.draw.polygon(screen, active_color, [
                (mouse[0], mouse[1] - size),  # Top
                (mouse[0] + size, mouse[1]),  # Right
                (mouse[0], mouse[1] + size),  # Bottom
                (mouse[0] - size, mouse[1])  # Left
            ], 2)

    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Handle window close button
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Clear canvas when clear button is clicked
            if clear_button.collidepoint(event.pos):
                painting = []  # Empty the painting list

            # Handle color selection
            for i in range(len(colors)):
                if colors[i].collidepoint(event.pos):
                    active_color = rgbs[i]
                    if active_color != (255, 255, 255):  # If not eraser
                        color_selected = True  # Mark that a color has been selected
                    if active_color == (255, 255, 255):  # If eraser is selected
                        active_figure = -1  # Special eraser mode

            # Handle brush/shape selection
            for brush in brushes:
                if brush[0].collidepoint(event.pos):
                    active_figure = brush[1]  # Set active figure to the selected shape

    # Update the display
    pygame.display.flip()

# Clean up and exit
pygame.quit()
