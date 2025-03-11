import pygame
import datetime

pygame.init()

screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption('Clock')
clock = pygame.time.Clock()
FPS = 50
done = False
myClock = pygame.image.load('img/mainclock.png')
myClock = pygame.transform.scale(myClock, (600, 600))



minute_arrow = pygame.image.load('img/rightarm.png') # 30:257
minute_arrow = pygame.transform.scale(minute_arrow, (800, 700))
second_arrow = pygame.image.load('img/leftarm.png')
second_arrow = pygame.transform.scale(second_arrow, (40, 500))


while not done:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        done = True
        my_time = datetime.datetime.now()
        hourINT = int(my_time.strftime("%I"))
        minuteINT = int(my_time.strftime("%M"))
        secondINT = int(my_time.strftime("%S"))

        angleHOUR = (hourINT % 12 + minuteINT/60) * 30 * -1 
        angleMINUTE = minuteINT * 7 * -1 - 10
        angleSECOND = secondINT * 6 * -1 - 5

        minute = pygame.transform.rotate(minute_arrow, angleMINUTE)
        second = pygame.transform.rotate(second_arrow, angleSECOND)
        

        screen.fill((255, 255, 255))
        screen.blit(myClock, (100, 100))
        screen.blit(second, (399 - int(second.get_width() / 2), 400 - int(second.get_height() / 2))) # centering the image
        # screen.blit(hour, ((399 - int(hour.get_width() / 2), 400 - int(hour.get_height() / 2))))
        screen.blit(minute, ((399 - int(minute.get_width() / 2), 400 - int(minute.get_height() / 2))))
        pygame.draw.circle(screen, (0, 0, 0), (400, 400), 22)
        pygame.display.flip()
        clock.tick(FPS)
        # time.sleep(1)
pygame.quit()