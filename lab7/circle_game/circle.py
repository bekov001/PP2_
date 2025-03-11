import pygame

pygame.init()

screen_width = 600
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Moving Ball")

ball_color = (255, 0, 0)  
ball_x = screen_width // 2  #init pos x
ball_y = screen_height // 2 # init y
ball_radius = 25
move_distance = 20

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                ball_x = max(ball_radius, ball_x - move_distance)  
            elif event.key == pygame.K_RIGHT:
                ball_x = min(screen_width - ball_radius, ball_x + move_distance)  
            elif event.key == pygame.K_UP:
                ball_y = max(ball_radius, ball_y - move_distance)  
            elif event.key == pygame.K_DOWN:
                ball_y = min(screen_height - ball_radius, ball_y + move_distance)  

    screen.fill((255, 255, 255))

    pygame.draw.circle(screen, ball_color, (ball_x, ball_y), ball_radius)

    pygame.display.flip()

pygame.quit()
