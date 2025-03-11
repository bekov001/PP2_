from time import sleep

import pygame
import os

pygame.init()

screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Music Player")

music_directory = "music"
chill_guy = pygame.image.load("Chill_Guy.webp")
os.chdir(music_directory)

music_files = [file for file in os.listdir() if file.endswith(".mp3") or file.endswith(".weba") ]
print(music_files)
current_track = 0
paused = False

pygame.mixer.music.load(music_files[current_track])

pygame.mixer.music.play()
font = pygame.font.Font(None, 24)
large_font = pygame.font.Font(None, 40)


chill_guy = pygame.transform.scale(chill_guy, (400, 400))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if paused:
                    pygame.mixer.music.unpause()
                    paused = False
                else:
                    pygame.mixer.music.pause()
                    paused = True
            elif event.key == pygame.K_RIGHT:
                current_track = (current_track + 1) % len(music_files)
                pygame.mixer.music.load(music_files[current_track])
                sleep(1)
                pygame.mixer.music.play()
            elif event.key == pygame.K_LEFT:
                current_track = (current_track - 1) % len(music_files)
                pygame.mixer.music.load(music_files[current_track])
                sleep(1)
                pygame.mixer.music.play()

    screen.fill((255, 255, 255))

    # Instructions in column
    instructions_text = "Spacebar: Play/Pause\nLeft Arrow: Previous\nRight Arrow: Next"
    instruction_lines = instructions_text.split('\n')
    y_offset = 10
    for line in instruction_lines:
        instructions = font.render(line, True, (0, 0, 0))
        screen.blit(instructions, (10, y_offset))
        y_offset += font.get_linesize()


    enjoy_music_text = large_font.render("Enjoy Music", True, (0, 0, 0))
    screen.blit(enjoy_music_text, (50, 250))

    # Display current track name
    current_track_name = os.path.splitext(music_files[current_track])[0]
    track_text = font.render(f"Current Track: {current_track_name}", True, (0, 0, 0))
    screen.blit(track_text, (50, 300))


    screen.blit(chill_guy, (150, 100))

    pygame.display.flip()

pygame.quit()