import pygame, sys
import random, time
import math
import paho.mqtt.client as mqtt

# Initialize game
pygame.init()
screen_width = 400
screen_height = 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pong Game")
fps = pygame.time.Clock()

# ====== MQTT config ======
MQTT_BROKER_IP = "192.168.0.157"
MQTT_PORT = 1883
MQTT_TOPIC = "GAME/Mikhaela"
mqtt_paddle_command = "hold"


# ====== MQTback Functies ======
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"Failed to connect to MQTT Broker, return code {rc}")


def on_message(client, userdata, msg):
    global mqtt_paddle_command
    payload = msg.payload.decode()
    # CORRECTED: Now accepts "0", "1", or "hold"
    if payload in ["0", "1", "hold"]:
        mqtt_paddle_command = payload
    else:
        print(f"Unknown command received via MQTT: {payload}")


# ====== MQTT Client Setup ======
mqtt_client = mqtt.Client(client_id="PongGamePlayer_Mikhaela")
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

try:
    mqtt_client.connect(MQTT_BROKER_IP, MQTT_PORT, 60)
    mqtt_client.loop_start()
except Exception as e:
    print(f"Could not connect to MQTT Broker: {e}")

# ====== Global Variables ======

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BALL_COLOR = (60, 179, 113)
pastel_purple = (221, 160, 221)
GREEN_LIGHT = (118, 227, 120)
ORANGE_LIGHT = (227, 151, 118)
RED_LIGHT = (227, 129, 118)

# Button: difficulty selection
BUTTON_COLOR_NORMAL = BLACK
BUTTON_COLOR_HOVER = (170, 170, 170)
BUTTON_TEXT_COLOR = WHITE

# Font
title_font = pygame.font.SysFont('Arial', 28, bold=True)
button_font = pygame.font.SysFont('Arial', 20, bold=True)

# Border
borderThickness = 8
rectBorder_x = 0
rectBorder_y_top = 0
rect_width = screen_width
right_border_x = screen_width - borderThickness

# Pallet
pallet_width = 4
pallet_height = 40 # Default, will be changed by difficulty
pallet_x = 380
pallet_y = (screen_height / 2) - (pallet_height / 2)
pallet_speed = 5

# Highscore variables
player_name = ""
highscores = []
current_level = ""


def load_highscores():
    global highscores
    highscores = []
    try:
        with open("highscores.txt", "r") as file:
            for line in file:
                try:
                    name, level, score_str = line.strip().split(",")
                    highscores.append({"name": name, "level": level, "score": float(score_str)})
                except ValueError:
                    print(f"Skipping malformed line in highscores.txt: {line.strip()}")
    except FileNotFoundError:
        pass


def save_highscores():
    with open("highscores.txt", "w") as file:
        for score_data in highscores:
            file.write(f"{score_data['name']},{score_data['level']},{score_data['score']}\n")


def get_player_name():
    global player_name
    player_name = ""
    input_active = True
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if player_name.strip():
                        input_active = False
                    else:
                        player_name = "Player"
                        input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    if len(player_name) < 20:
                        player_name += event.unicode

        screen.fill(WHITE)
        text_surface = button_font.render("Enter your name:", True, BLACK)
        text_rect = text_surface.get_rect(center=(screen_width // 2, 100))
        screen.blit(text_surface, text_rect)

        name_surface = button_font.render(player_name, True, BLACK)
        name_rect = name_surface.get_rect(center=(screen_width // 2, 150))
        screen.blit(name_surface, name_rect)

        pygame.display.flip()
        fps.tick(60)


def update_highscores(name, level, score_val):
    global highscores
    highscores.append({"name": name, "level": level, "score": score_val})
    highscores.sort(key=lambda x: x["score"], reverse=True)
    highscores = highscores[:10] # Keep top 10 scores
    save_highscores()


def display_highscores_screen():
    screen.fill(WHITE)
    title_text = title_font.render("Highscores", True, BLACK)
    title_rect = title_text.get_rect(center=(screen_width // 2, 30))
    screen.blit(title_text, title_rect)

    y_offset = 80
    if not highscores:
        no_scores_text = button_font.render("No highscores yet!", True, BLACK)
        no_scores_rect = no_scores_text.get_rect(center=(screen_width // 2, y_offset + 50))
        screen.blit(no_scores_text, no_scores_rect)

    for i, score_data in enumerate(highscores[:5]):  # Display top 5
        score_text_display = button_font.render(
            f"{i + 1}. {score_data['name']} - {score_data['level']} - {score_data['score']:.2f} s",
            True, BLACK)
        score_rect_display = score_text_display.get_rect(center=(screen_width // 2, y_offset))
        screen.blit(score_text_display, score_rect_display)
        y_offset += 30

    back_text = button_font.render("Click to go back", True, RED_LIGHT)
    back_rect = back_text.get_rect(center=(screen_width // 2, screen_height - 40))
    screen.blit(back_text, back_rect)

    pygame.display.flip()


load_highscores()

# Ball
ballRADIUS = 8
speedBall = 2.0
speedBall_x = 0
speedBall_y = 0
positionBall_x = 0
positionBall_y = 0

# ====== Game score + lives ======
lives = 3
score_start_time = None
current_game_score = 0.0
game_over = False
in_difficulty_menu = True
running = True
showing_highscores_page = False

# Difficulty selection buttons
button_width = 150
button_height = 50
padding = 20

buttons = []
easy = {"text": "Easy", "rect": pygame.Rect(0, 0, button_width, button_height), "base_text_color": GREEN_LIGHT,
        "action": "easy_selected"}
medium = {"text": "Medium", "rect": pygame.Rect(0, 0, button_width, button_height), "base_text_color": ORANGE_LIGHT,
          "action": "medium_selected"}
hard = {"text": "Hard", "rect": pygame.Rect(0, 0, button_width, button_height), "base_text_color": RED_LIGHT,
        "action": "hard_selected"}
buttons.extend([easy, medium, hard])

start_y_difficulty_buttons = 130
for i, button_info in enumerate(buttons):
    button_info["rect"].centerx = screen_width // 2
    button_info["rect"].top = start_y_difficulty_buttons + i * (button_height + padding)

# Game over screen buttons
restart_button = {"text": "Restart", "rect": pygame.Rect(0, 0, button_width, button_height),
                  "base_text_color": GREEN_LIGHT, "action": "restart"}
menu_button = {"text": "Menu", "rect": pygame.Rect(0, 0, button_width, button_height), "base_text_color": ORANGE_LIGHT,
               "action": "menu"}
show_highscores_button = {"text": "Highscores", "rect": pygame.Rect(0, 0, button_width, button_height),
                          "base_text_color": pastel_purple, "action": "show_highscores"}

game_over_buttons = [restart_button, menu_button, show_highscores_button]
start_y_game_over_buttons = 200
for i, button_info in enumerate(game_over_buttons):
    button_info["rect"].centerx = screen_width // 2
    button_info["rect"].top = start_y_game_over_buttons + i * (button_height + 15)


# Respawn ball + position
def spawnRESET_Ball():
    global positionBall_x, positionBall_y, speedBall_x, speedBall_y, speedBall, pallet_y, pallet_height
    positionBall_x = random.uniform(borderThickness + ballRADIUS, screen_width - borderThickness - ballRADIUS - 150)
    positionBall_y = random.uniform(borderThickness + ballRADIUS, screen_height - borderThickness - ballRADIUS)

    angle_range = math.pi / 3
    angle = random.uniform(-angle_range / 2, angle_range / 2)

    direction_x = random.choice([-1, 1])
    speedBall_x = direction_x * speedBall * math.cos(angle)
    speedBall_y = speedBall * math.sin(angle)

    if abs(speedBall_x) < 0.5 * speedBall:
        speedBall_x = direction_x * 0.5 * speedBall
    if abs(speedBall_y) < 0.2 * speedBall:
         speedBall_y = random.choice([-1,1]) * 0.2 * speedBall


def calc_angle(positionAngle):
    global pallet_height
    positionAngle = max(0, min(positionAngle, pallet_height))
    angle_range_degrees = 100
    angle_degrees = (positionAngle / pallet_height) * angle_range_degrees - (angle_range_degrees / 2)
    return angle_degrees


spawnRESET_Ball()

# ====== Pong Game ======
while running:
    mouse_pos = pygame.mouse.get_pos()

    if in_difficulty_menu or showing_highscores_page:
        screen.fill(WHITE)
    elif game_over:
        screen.fill(WHITE)
    else:
        screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

        if showing_highscores_page:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                showing_highscores_page = False
            continue

        if in_difficulty_menu:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button_info in buttons:
                    if button_info["rect"].collidepoint(mouse_pos):
                        if button_info["action"] == "easy_selected":
                            speedBall = 3.0
                            pallet_height = 50
                            current_level = "Easy"
                        elif button_info["action"] == "medium_selected":
                            speedBall = 4.0 # Adjusted
                            pallet_height = 40
                            current_level = "Medium"
                        elif button_info["action"] == "hard_selected":
                            speedBall = 6.0 # Adjusted
                            pallet_height = 30
                            current_level = "Hard"

                        pallet_y = (screen_height / 2) - (pallet_height / 2)

                        get_player_name()
                        spawnRESET_Ball()
                        lives = 3
                        score_start_time = time.time()
                        current_game_score = 0.0
                        game_over = False
                        in_difficulty_menu = False
                        mqtt_paddle_command = "hold"
        elif game_over:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button_info in game_over_buttons:
                    if button_info["rect"].collidepoint(mouse_pos):
                        if button_info["action"] == "restart":
                            lives = 3
                            score_start_time = time.time()
                            current_game_score = 0.0
                            game_over = False
                            spawnRESET_Ball()
                            pallet_y = (screen_height / 2) - (pallet_height / 2)
                            mqtt_paddle_command = "hold"
                        elif button_info["action"] == "menu":
                            in_difficulty_menu = True
                            game_over = False
                            mqtt_paddle_command = "hold"
                        elif button_info["action"] == "show_highscores":
                            showing_highscores_page = True

    if not running: break

    if not in_difficulty_menu and not game_over and not showing_highscores_page:
        if mqtt_paddle_command == "0":
            pallet_y -= pallet_speed
        elif mqtt_paddle_command == "1":
            pallet_y += pallet_speed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            pallet_y -= pallet_speed
        if keys[pygame.K_DOWN]:
            pallet_y += pallet_speed

        pallet_y = max(borderThickness, min(pallet_y, screen_height - borderThickness - pallet_height))

        positionBall_x += speedBall_x
        positionBall_y += speedBall_y

        if positionBall_y - ballRADIUS <= borderThickness:
            speedBall_y *= -1
            positionBall_y = borderThickness + ballRADIUS
        if positionBall_y + ballRADIUS >= screen_height - borderThickness:
            speedBall_y *= -1
            positionBall_y = screen_height - borderThickness - ballRADIUS

        if positionBall_x - ballRADIUS <= borderThickness:
            speedBall_x *= -1
            positionBall_x = borderThickness + ballRADIUS

        ball_rect = pygame.Rect(int(positionBall_x - ballRADIUS), int(positionBall_y - ballRADIUS), ballRADIUS * 2,
                                ballRADIUS * 2)
        pallet_rect = pygame.Rect(int(pallet_x), int(pallet_y), int(pallet_width), int(pallet_height))

        if ball_rect.colliderect(pallet_rect):
            if speedBall_x > 0 and positionBall_x + ballRADIUS > pallet_x and positionBall_x < pallet_x + pallet_width + ballRADIUS:
                hit_pos_on_paddle = (positionBall_y - pallet_y)
                angle_deg = calc_angle(hit_pos_on_paddle)
                angle_rad = math.radians(angle_deg)

                current_ball_speed_magnitude = math.sqrt(speedBall_x ** 2 + speedBall_y ** 2)
                if current_ball_speed_magnitude == 0: current_ball_speed_magnitude = speedBall

                speedBall_x = -current_ball_speed_magnitude * math.cos(angle_rad)
                speedBall_y = current_ball_speed_magnitude * math.sin(angle_rad)

                positionBall_x = pallet_x - ballRADIUS

        if positionBall_x + ballRADIUS >= right_border_x:
            lives -= 1
            if lives > 0:
                spawnRESET_Ball()
                pallet_y = (screen_height / 2) - (pallet_height / 2)
            else:
                if score_start_time is not None:
                    current_game_score = time.time() - score_start_time
                game_over = True
                if player_name.strip():
                    update_highscores(player_name, current_level, current_game_score)
                else:
                    update_highscores("Player", current_level, current_game_score)


        if score_start_time is not None and not game_over:
            current_game_score = time.time() - score_start_time

    if showing_highscores_page:
        display_highscores_screen()
    elif in_difficulty_menu:
        title_text_surface = title_font.render('Select Difficulty', True, BLACK)
        title_text_rect = title_text_surface.get_rect(center=(screen_width // 2, 70))
        screen.blit(title_text_surface, title_text_rect)
        for button_info in buttons:
            button_rect = button_info["rect"]
            current_button_bg_color = BUTTON_COLOR_HOVER if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR_NORMAL
            pygame.draw.rect(screen, current_button_bg_color, button_rect, border_radius=4)
            text_surface = button_font.render(button_info["text"], True, button_info["base_text_color"])
            text_rect = text_surface.get_rect(center=button_rect.center)
            screen.blit(text_surface, text_rect)
    elif game_over:
        game_over_text = title_font.render('Game Over', True, RED_LIGHT)
        game_over_rect = game_over_text.get_rect(center=(screen_width // 2, 80))
        screen.blit(game_over_text, game_over_rect)
        score_text_display = button_font.render(f"Score: {current_game_score:.2f} s", True, BLACK)
        score_rect_display = score_text_display.get_rect(center=(screen_width // 2, 140))
        screen.blit(score_text_display, score_rect_display)
        for button_info in game_over_buttons:
            button_rect = button_info["rect"]
            current_button_bg_color = BUTTON_COLOR_HOVER if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR_NORMAL
            pygame.draw.rect(screen, current_button_bg_color, button_rect, border_radius=4)
            text_surface = button_font.render(button_info["text"], True, button_info["base_text_color"])
            text_rect = text_surface.get_rect(center=button_rect.center)
            screen.blit(text_surface, text_rect)
    else:
        # ====== Border drawing ======
        pygame.draw.rect(screen, pastel_purple, [rectBorder_x, rectBorder_y_top, rect_width, borderThickness])
        pygame.draw.rect(screen, pastel_purple, [0, screen_height - borderThickness, screen_width, borderThickness])
        pygame.draw.rect(screen, pastel_purple, [0, 0, borderThickness, screen_height])
        pygame.draw.rect(screen, pastel_purple, [right_border_x, 0, borderThickness, screen_height])

        pygame.draw.rect(screen, WHITE, [pallet_x, pallet_y, pallet_width, pallet_height])
        pygame.draw.circle(screen, BALL_COLOR, (int(positionBall_x), int(positionBall_y)), ballRADIUS)

        lives_text = button_font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(lives_text, (20, 20))
        score_display_text = button_font.render(f"Score: {current_game_score:.2f}", True, WHITE)
        score_display_rect = score_display_text.get_rect(topright=(screen_width - 20, 20))
        screen.blit(score_display_text, score_display_rect)

    pygame.display.flip()
    fps.tick(60)

if mqtt_client.is_connected():
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    print("MQTT client disconnected.")

pygame.quit()
sys.exit()