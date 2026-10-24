import pygame
import sys
import random

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)
PURPLE = (147, 112, 219)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Naruto vs Madara - Undertale")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Courier", 18, bold=True)

try:
    boss_img = pygame.image.load("assets/madara_boss.png").convert_alpha()
    boss_img = pygame.transform.scale(boss_img, (180, 180))
except FileNotFoundError:
    boss_img = None

try:
    gunbai_img = pygame.image.load("assets/gunbai_bullet.png").convert_alpha()
    gunbai_img = pygame.transform.scale(gunbai_img, (20, 35))
except FileNotFoundError:
    gunbai_img = None

try:
    player_img = pygame.image.load("assets/naruto_soul.png").convert_alpha()
    player_img = pygame.transform.scale(player_img, (16, 16))
except FileNotFoundError:
    player_img = None

BOX_RECT = pygame.Rect(250, 250, 300, 200)

player_pos = [BOX_RECT.centerx, BOX_RECT.centery]
player_speed = 4
player_hp = 20
player_max_hp = 20

boss_hp = 200
boss_max_hp = 200
boss_dialogue = "Would you like these clones to use Susanoo or not?"

game_state = 'MENU'
selected_option = 0
options = ["FIGHT", "ACT", "ITEM", "MERCY"]

button_rects = []
for i in range(len(options)):
    btn_x = 150 + (i * 140)
    btn_y = 520
    button_rects.append(pygame.Rect(btn_x, btn_y, 110, 40))

bullets = []
bullet_timer = 0
attack_duration = 0

def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    surface.blit(text_obj, (x, y))

def draw_wrapped_text(text, font, color, surface, rect):
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] < (rect.width - 20):
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    y_offset = rect.top + 15
    for line in lines:
        draw_text(line.strip(), font, color, surface, rect.left + 15, y_offset)
        y_offset += font.get_linesize() + 4

def draw_code_button(surface, text, rect, is_selected):
    border_color = YELLOW if is_selected else ORANGE
    pygame.draw.rect(surface, BLACK, rect)
    pygame.draw.rect(surface, border_color, rect, 3)

    if is_selected:
        if player_img:
            surface.blit(player_img, (rect.x + 8, rect.y + (rect.height // 2 - 8)))
        else:
            pygame.draw.circle(surface, ORANGE, (rect.x + 15, rect.y + rect.height // 2), 5)
        text_x = rect.x + 30
    else:
        text_x = rect.x + 20

    draw_text(text, font, border_color, surface, text_x, rect.y + (rect.height // 2 - 9))

def reset_boss_attack():
    global bullets, attack_duration, player_pos
    bullets = []
    attack_duration = 220
    player_pos = [BOX_RECT.centerx, BOX_RECT.centery]

def execute_action(option_index):
    global boss_hp, boss_dialogue, game_state, player_hp
    if option_index == 0:
        boss_hp -= 40
        boss_dialogue = "Naruto threw a Giant Shuriken! Madara blocked with his Gunbai."
        if boss_hp <= 0:
            game_state = 'VICTORY'
        else:
            game_state = 'BOSS_ATTACK'
            reset_boss_attack()
    elif option_index == 1:
        boss_dialogue = "Naruto tried Talk-no-Jutsu... Madara laughed in his face."
        game_state = 'BOSS_ATTACK'
        reset_boss_attack()
    elif option_index == 2:
        player_hp = min(player_max_hp, player_hp + 10)
        boss_dialogue = "Naruto ate Ichiraku Ramen (+10 HP)!"
        game_state = 'BOSS_ATTACK'
        reset_boss_attack()
    elif option_index == 3:
        boss_dialogue = "Madara rejects peace: 'Too weak.'"
        game_state = 'BOSS_ATTACK'
        reset_boss_attack()

running = True
while running:
    clock.tick(FPS)
    screen.fill(BLACK)

    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == 'MENU':
            if event.type == pygame.MOUSEMOTION:
                for idx, b_rect in enumerate(button_rects):
                    if b_rect.collidepoint(mouse_pos):
                        selected_option = idx

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for idx, b_rect in enumerate(button_rects):
                    if b_rect.collidepoint(mouse_pos):
                        selected_option = idx
                        execute_action(selected_option)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_RIGHT:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_z):
                    execute_action(selected_option)

    if game_state == 'BOSS_ATTACK':
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_pos[0] - 8 > BOX_RECT.left:
            player_pos[0] -= player_speed
        if keys[pygame.K_RIGHT] and player_pos[0] + 8 < BOX_RECT.right:
            player_pos[0] += player_speed
        if keys[pygame.K_UP] and player_pos[1] - 8 > BOX_RECT.top:
            player_pos[1] -= player_speed
        if keys[pygame.K_DOWN] and player_pos[1] + 8 < BOX_RECT.bottom:
            player_pos[1] += player_speed

        bullet_timer += 1
        if bullet_timer % 12 == 0:
            spawn_x = random.randint(BOX_RECT.left + 15, BOX_RECT.right - 25)
            bullets.append([spawn_x, BOX_RECT.top, random.choice([-1, 0, 1]), random.randint(4, 7)])

        player_rect = pygame.Rect(player_pos[0] - 8, player_pos[1] - 8, 16, 16)
        for bullet in bullets[:]:
            bullet[0] += bullet[2]
            bullet[1] += bullet[3]

            bullet_rect = pygame.Rect(bullet[0], bullet[1], 20, 30)
            if bullet_rect.colliderect(player_rect):
                player_hp -= 4
                bullets.remove(bullet)
                if player_hp <= 0:
                    game_state = 'GAME_OVER'
            elif bullet[1] > BOX_RECT.bottom or bullet[0] < BOX_RECT.left or bullet[0] > BOX_RECT.right:
                bullets.remove(bullet)

        attack_duration -= 1
        if attack_duration <= 0:
            game_state = 'MENU'

    if boss_img:
        screen.blit(boss_img, (310, 20))
    else:
        draw_text("MADARA UCHIHA", font, RED, screen, 330, 40)

    pygame.draw.rect(screen, RED, (300, 210, 200, 12))
    pygame.draw.rect(screen, GREEN, (300, 210, int(200 * (max(0, boss_hp) / boss_max_hp)), 12))

    pygame.draw.rect(screen, WHITE, BOX_RECT, 4)

    if game_state == 'MENU':
        draw_wrapped_text(boss_dialogue, font, WHITE, screen, BOX_RECT)
    elif game_state == 'BOSS_ATTACK':
        if player_img:
            screen.blit(player_img, (int(player_pos[0]) - 8, int(player_pos[1]) - 8))
        else:
            pygame.draw.circle(screen, ORANGE, (int(player_pos[0]), int(player_pos[1])), 8)

        for bullet in bullets:
            if gunbai_img:
                screen.blit(gunbai_img, (bullet[0], bullet[1]))
            else:
                pygame.draw.rect(screen, PURPLE, (bullet[0], bullet[1], 15, 25))

    elif game_state == 'VICTORY':
        draw_wrapped_text("YOU WON! Madara acknowledged your strength!", font, GREEN, screen, BOX_RECT)
    elif game_state == 'GAME_OVER':
        draw_wrapped_text("GAME OVER - Trapped in the Infinite Tsukuyomi!", font, RED, screen, BOX_RECT)

    draw_text(f"NARUTO   LV 19   HP {max(0, player_hp)}/{player_max_hp}", font, WHITE, screen, 250, 470)

    for i, option in enumerate(options):
        is_selected = (i == selected_option and game_state == 'MENU')
        draw_code_button(screen, option, button_rects[i], is_selected)

    pygame.display.flip()

pygame.quit()
sys.exit()