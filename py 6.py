import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Sprite Game")

# Load sprite sheet
player_sprite = pygame.image.load("player.png").convert_alpha()
sprite_width = 32
sprite_height = 32
player_image = player_sprite.subsurface((0, 0, sprite_width, sprite_height))

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Clock
clock = pygame.time.Clock()

# Player
player_x, player_y = WIDTH // 2, HEIGHT // 2
player_speed = 5

# Bullets
bullets = []
bullet_speed = 10

# Enemies
enemies = []
for _ in range(5):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    enemies.append([x, y, 20])  # x, y, radius

def draw_window():
    win.fill(WHITE)
    # Draw player
    win.blit(player_image, (player_x, player_y))

    # Draw bullets
    for bullet in bullets:
        pygame.draw.circle(win, BLUE, (int(bullet[0]), int(bullet[1])), 5)

    # Draw enemies
    for enemy in enemies:
        pygame.draw.circle(win, RED, (int(enemy[0]), int(enemy[1])), enemy[2])

    pygame.display.update()

run = True
while run:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed
    if keys[pygame.K_UP]:
        player_y -= player_speed
    if keys[pygame.K_DOWN]:
        player_y += player_speed
    if keys[pygame.K_SPACE]:
        bullets.append([player_x + sprite_width // 2, player_y + sprite_height // 2])

    # Move bullets
    for bullet in bullets[:]:
        bullet[1] -= bullet_speed
        if bullet[1] < 0:
            bullets.remove(bullet)

    # Move enemies toward player
    for enemy in enemies:
        dx = player_x - enemy[0]
        dy = player_y - enemy[1]
        dist = math.hypot(dx, dy)
        if dist != 0:
            enemy[0] += dx / dist * 2
            enemy[1] += dy / dist * 2

    # Bullet collision with enemies
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if math.hypot(bullet[0] - enemy[0], bullet[1] - enemy[1]) < enemy[2]:
                bullets.remove(bullet)
                enemies.remove(enemy)
                break

    draw_window()

pygame.quit()
