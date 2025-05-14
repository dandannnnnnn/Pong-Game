import pygame, sys
import random

# Initialize pygame
pygame.init()
screen_width = 400
screen_height = 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pong Game")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BALL_COLOR= (60, 179, 113)
pastel_purple = (221, 160, 221) #color borders windows

fps = pygame.time.Clock()

#Global variables
recordScore = 0
lastScore = 0

#Border variables
rectBorder_x = 0 #position rectangle x
rectBorder_y_top = 0 #position rectangle y
rect_width = screen_width
borderThickness = 8

#Pallet variables
pallet_width = 4
pallet_height = 40
pallet_x = 380 #position
pallet_y = (screen_height / 2) - (pallet_height / 2) #position
pallet_speed = 5

#Ball variables
ballRADIUS = 8
speedBall = 2.0
speedBall_x = 0
speedBall_y = 0

def spawnRESET_Ball(): #nieuwe willekeurige positie van de bal
    global positionBall_x, positionBall_y, speedBall_x, speedBall_y
    positionBall_x = random.uniform(borderThickness + ballRADIUS, screen_width - borderThickness + ballRADIUS) #random position
    positionBall_y = random.uniform(borderThickness + ballRADIUS, screen_height - borderThickness + ballRADIUS) #random position

    speedBall_x = random.choice([-speedBall, speedBall])
    speedBall_y = random.choice([-speedBall, speedBall])

    if speedBall_x == 0 and speedBall_y == 0:
        speedBall_x == speedBall 

spawnRESET_Ball()
#=========================================================================================================================================
#=========================================================================================================================================

running = True
while running:
    screen.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    #Pallet movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        pallet_y -= pallet_speed
    if keys[pygame.K_DOWN]:
        pallet_y += pallet_speed
    
    #Pallet boundary: pallet cannot overlay with borders
    if pallet_y < borderThickness:
        pallet_y = borderThickness
    if pallet_y + pallet_height > screen_height - borderThickness:
        pallet_y = screen_height - borderThickness - pallet_height

    
    #Ball movement
    positionBall_x += speedBall_x
    positionBall_y += speedBall_y

    if positionBall_x - ballRADIUS <= borderThickness: #left border collision
        speedBall_x *= -1
        positionBall_x = borderThickness + ballRADIUS
    
    if positionBall_y - ballRADIUS <= borderThickness: #top border collision
        speedBall_y *= -1
        positionBall_y = borderThickness + ballRADIUS
    if positionBall_y + ballRADIUS >= screen_width - borderThickness: #bottom border collision
        speedBall_y *= -1
        positionBall_y = screen_height - borderThickness - ballRADIUS

    #Pallet + Ball collision
    ball_rect = pygame.Rect(positionBall_x - ballRADIUS, positionBall_y - ballRADIUS, ballRADIUS * 2, ballRADIUS * 2)
    pallet_rect = pygame.Rect(pallet_x, pallet_y, pallet_width, pallet_height)

    if ball_rect.colliderect(pallet_rect): #collision detection
        if speedBall_x > 0:
            speedBall_x *= -1
            positionBall_x = pallet_x - ballRADIUS
    
    #Ball out of game area
    if positionBall_x - ballRADIUS > screen_width: 
        spawnRESET_Ball()

    #Border drawing
    pygame.draw.rect(screen, pastel_purple, [rectBorder_x, rectBorder_y_top, rect_width, borderThickness]) #top border
    pygame.draw.rect(screen, pastel_purple, [0, screen_height - borderThickness, screen_width, borderThickness]) #bottom border
    pygame.draw.rect(screen, pastel_purple, [0, 0, borderThickness, screen_height]) #left border

    pygame.draw.rect(screen, WHITE, [pallet_x, pallet_y, pallet_width, pallet_height]) #pong pallet drawing
    pygame.draw.circle(screen, BALL_COLOR, (float(positionBall_x), float(positionBall_y)), ballRADIUS) #pong ball drawing


    pygame.display.flip()
    fps.tick(60)


pygame.quit()
sys.exit()