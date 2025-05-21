import pygame, sys
import random, time
import math

#Initialize game
pygame.init()
screen_width = 400
screen_height = 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pong Game")

#Global variables

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BALL_COLOR= (60, 179, 113)
pastel_purple = (221, 160, 221)
GREEN_LIGHT = (118, 227, 120)
ORANGE_LIGHT = (227, 151, 118)
RED_LIGHT = (227, 129, 118)

BUTTON_COLOR_NORMAL = BLACK
BUTTON_COLOR_HOVER = (170, 170, 170)
BUTTON_TEXT_COLOR = WHITE

title_font = pygame.font.SysFont('Arial', 28, bold=True)
button_font = pygame.font.SysFont('Arial', 20, bold=True)

fps = pygame.time.Clock()
button_width = 150
button_height = 50
padding = 20

buttons = []
easy = {"text": "Easy", "rect": pygame.Rect(0, 0, button_width, button_height), "base_text_color": GREEN_LIGHT, "action": "easy_selected"}
medium = {"text": "Medium", "rect": pygame.Rect(0, 0, button_width, button_height), "base_text_color": ORANGE_LIGHT, "action": "medium_selected"}
hard = {"text": "Hard", "rect": pygame.Rect(0, 0, button_width, button_height), "base_text_color": RED_LIGHT, "action": "hard_selected"}
buttons.append(easy)
buttons.append(medium)
buttons.append(hard)

#Game over + lives + score
lives = 3
score_start_time = None
score = 0.0
game_over = False

# Game Over buttons
restart_button = {"text": "Restart", "rect": pygame.Rect(0, 0, button_width, button_height), "base_text_color": GREEN_LIGHT, "action": "restart"}
menu_button = {"text": "Menu", "rect": pygame.Rect(0, 0, button_width, button_height), "base_text_color": ORANGE_LIGHT, "action": "menu"}
game_over_buttons = [restart_button, menu_button]
for i, button_info in enumerate(game_over_buttons):
    button_info["rect"].centerx = screen_width // 2
    button_info["rect"].top = 220 + i * (button_height + 20)

rectBorder_x = 0
rectBorder_y_top = 0
rect_width = screen_width
borderThickness = 8
right_border_x = screen_width - borderThickness

pallet_width = 4
pallet_height = 40
pallet_x = 380
pallet_y = (screen_height / 2) - (pallet_height / 2)
pallet_speed = 5

ballRADIUS = 8
speedBall = 2.0
speedBall_x = 0
speedBall_y = 0
positionBall_x = 0
positionBall_y = 0


def spawnRESET_Ball():
    global positionBall_x, positionBall_y, speedBall_x, speedBall_y
    positionBall_x = random.uniform(borderThickness + ballRADIUS, screen_width - borderThickness - ballRADIUS)
    positionBall_y = random.uniform(borderThickness + ballRADIUS, screen_height - borderThickness - ballRADIUS)
    # Keep direction, but use current speedBall
    direction_x = random.choice([-1, 1])
    direction_y = random.choice([-1, 1])
    speedBall_x = direction_x * speedBall
    speedBall_y = direction_y * speedBall

def calc_angle(positionAngle):
    # Example: calculate angle based on position along the paddle
    # Clamp positionAngle between 0 and pallet_height
    positionAngle = max(0, min(positionAngle, pallet_height))
    # Map positionAngle to an angle between -45 and 45 degrees
    angle_range = 90  # total angle range
    angle = (positionAngle / pallet_height) * angle_range - (angle_range / 2)
    return angle

startPosition = random.randint(0, pallet_height)
startAngle = math.radians(calc_angle(startPosition))
spawnRESET_Ball()

start_y = 130
for i, button_info in enumerate(buttons):
    button_info["rect"].centerx = screen_width // 2
    button_info["rect"].top = start_y + i * (button_height + padding)

in_difficulty_menu = True
running = True

while running:
    if in_difficulty_menu:
        screen.fill(WHITE)
    elif game_over:
        screen.fill(WHITE)
    else:
        screen.fill(BLACK)

    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if in_difficulty_menu:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button_info in buttons:
                    if button_info["rect"].collidepoint(mouse_pos):
                        if button_info["action"] == "easy_selected":
                            speedBall = 2.0
                            pallet_height = 40
                        elif button_info["action"] == "medium_selected":
                            speedBall = 3.0
                            pallet_height = 30
                        elif button_info["action"] == "hard_selected":
                            speedBall = 4.0
                            pallet_height = 20
                        spawnRESET_Ball()

                        lives = 3
                        score_start_time = time.time()
                        score = 0.0
                        game_over = False
                        pallet_y = (screen_height / 2) - (pallet_height / 2)
                        in_difficulty_menu = False
        elif game_over:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button_info in game_over_buttons:
                    if button_info["rect"].collidepoint(mouse_pos):
                        if button_info["action"] == "restart":
                            # Restart game
                            lives = 3
                            score_start_time = time.time()
                            score = 0.0
                            game_over = False
                            spawnRESET_Ball()
                            pallet_y = (screen_height / 2) - (pallet_height / 2)
                        elif button_info["action"] == "menu":
                            in_difficulty_menu = True
                            game_over = False
        else:
            pass

    if in_difficulty_menu:
        title_text_surface = title_font.render('Select Difficulty', True, BLACK)
        title_text_rect = title_text_surface.get_rect(center=(screen_width // 2, 70))
        screen.blit(title_text_surface, title_text_rect)

        for button_info in buttons:
            button_rect = button_info["rect"]
            button_text_content = button_info["text"]
            button_base_text_color = button_info["base_text_color"]

            current_button_bg_color = BUTTON_COLOR_NORMAL
            if button_rect.collidepoint(mouse_pos):
                current_button_bg_color = BUTTON_COLOR_HOVER

            pygame.draw.rect(screen, current_button_bg_color, button_rect, border_radius=4)
            text_surface = button_font.render(button_text_content, True, button_base_text_color)
            text_rect = text_surface.get_rect(center=button_rect.center)
            screen.blit(text_surface, text_rect)
    elif game_over:
        #Game over screen
        game_over_text = title_font.render('Game Over', True, RED_LIGHT)
        game_over_rect = game_over_text.get_rect(center=(screen_width // 2, 100))
        screen.blit(game_over_text, game_over_rect)

        score_text = button_font.render(f"Score: {score:.2f} s", True, BLACK)
        score_rect = score_text.get_rect(center=(screen_width // 2, 160))
        screen.blit(score_text, score_rect)

        for button_info in game_over_buttons:
            button_rect = button_info["rect"]
            button_text_content = button_info["text"]
            button_base_text_color = button_info["base_text_color"]

            current_button_bg_color = BUTTON_COLOR_NORMAL
            if button_rect.collidepoint(mouse_pos):
                current_button_bg_color = BUTTON_COLOR_HOVER

            pygame.draw.rect(screen, current_button_bg_color, button_rect, border_radius=4)
            text_surface = button_font.render(button_text_content, True, button_base_text_color)
            text_rect = text_surface.get_rect(center=button_rect.center)
            screen.blit(text_surface, text_rect)
    else:
        # Pong game logic
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            pallet_y -= pallet_speed
        if keys[pygame.K_DOWN]:
            pallet_y += pallet_speed

        if pallet_y < borderThickness:
            pallet_y = borderThickness
        if pallet_y + pallet_height > screen_height - borderThickness:
            pallet_y = screen_height - borderThickness - pallet_height

        #Ball movement
        positionBall_x += speedBall_x
        positionBall_y += speedBall_y

        #Ball + border collision
        if positionBall_x - ballRADIUS <= borderThickness:
            speedBall_x *= -1
            positionBall_x = borderThickness + ballRADIUS

        # Create rects for collision detection (always define before use)
        ball_rect = pygame.Rect(int(positionBall_x - ballRADIUS), int(positionBall_y - ballRADIUS), ballRADIUS * 2, ballRADIUS * 2)
        pallet_rect = pygame.Rect(int(pallet_x), int(pallet_y), int(pallet_width), int(pallet_height))

        if positionBall_y - ballRADIUS <= borderThickness:
            speedBall_y *= -1
            positionBall_y = borderThickness + ballRADIUS

        # Ball + bottom border collision
        if positionBall_y + ballRADIUS >= screen_height - borderThickness:
            speedBall_y *= -1
            positionBall_y = screen_height - borderThickness - ballRADIUS

        #Ball angles
        if ball_rect.colliderect(pallet_rect):
            # Calculate where the ball hit the paddle
            hit_pos = (positionBall_y - pallet_y) / pallet_height
            angle = calc_angle(hit_pos * pallet_height)
            speed = math.hypot(speedBall_x, speedBall_y)
            speedBall_x = -abs(speedBall) * math.cos(math.radians(angle))
            speedBall_y = speedBall * math.sin(math.radians(angle))
            positionBall_x = pallet_x - ballRADIUS

        #Ball + pallet collision
        if ball_rect.colliderect(pallet_rect):
            if speedBall_x > 0:
                speedBall_x *= -1
                positionBall_x = pallet_x - ballRADIUS

        
        if positionBall_x + ballRADIUS >= right_border_x:
            lives -= 1
            if lives > 0:
                spawnRESET_Ball()
                pallet_y = (screen_height / 2) - (pallet_height / 2)
            else:
                # Game over, calculate score
                score = time.time() - score_start_time
                game_over = True
        # Draw game border, paddle, and ball only in game mode
        pygame.draw.rect(screen, pastel_purple, [rectBorder_x, rectBorder_y_top, rect_width, borderThickness])  # Top border
        pygame.draw.rect(screen, pastel_purple, [0, screen_height - borderThickness, screen_width, borderThickness])  # Bottom border
        pygame.draw.rect(screen, pastel_purple, [0, 0, borderThickness, screen_height])  # Left border
        pygame.draw.rect(screen, pastel_purple, [right_border_x, 0, borderThickness, screen_height])  # Right border (behind paddle)

        pygame.draw.rect(screen, WHITE, [pallet_x, pallet_y, pallet_width, pallet_height])
        pygame.draw.circle(screen, BALL_COLOR, (int(positionBall_x), int(positionBall_y)), ballRADIUS)
        pygame.draw.rect(screen, WHITE, [pallet_x, pallet_y, pallet_width, pallet_height])
        pygame.draw.circle(screen, BALL_COLOR, (int(positionBall_x), int(positionBall_y)), ballRADIUS)

        lives_text = button_font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(lives_text, (10, 10))

    pygame.display.flip()
    fps.tick(60)

pygame.quit()
sys.exit()
