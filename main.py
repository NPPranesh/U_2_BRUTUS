import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Square vs Circle in Cave")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Load pixelated cave background
background = pygame.image.load("cave_pixel.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Player (square) settings
player_size = 50
player_x = WIDTH // 2
player_y = HEIGHT - player_size - 10
player_speed = 5

# Enemy (circle) settings
enemy_radius = 30
enemy_x = random.randint(enemy_radius, WIDTH - enemy_radius)
enemy_y = 50
enemy_speed = 3

# Clock
clock = pygame.time.Clock()
FPS = 60

# Health
player_health = 100
font = pygame.font.SysFont(None, 30)

# Game loop
running = True
while running:
    clock.tick(FPS)
    screen.blit(background, (0, 0))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x - player_speed > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x + player_speed + player_size < WIDTH:
        player_x += player_speed
    if keys[pygame.K_UP] and player_y - player_speed > 0:
        player_y -= player_speed
    if keys[pygame.K_DOWN] and player_y + player_speed + player_size < HEIGHT:
        player_y += player_speed

    # Enemy movement (attacks player)
    if enemy_x < player_x + player_size // 2:
        enemy_x += enemy_speed
    elif enemy_x > player_x + player_size // 2:
        enemy_x -= enemy_speed
    if enemy_y < player_y + player_size // 2:
        enemy_y += enemy_speed
    elif enemy_y > player_y + player_size // 2:
        enemy_y -= enemy_speed

    # Collision detection
    if abs(player_x + player_size // 2 - enemy_x) < enemy_radius + player_size // 2 and \
            abs(player_y + player_size // 2 - enemy_y) < enemy_radius + player_size // 2:
        player_health -= 1

    # Draw player and enemy
    pygame.draw.rect(screen, BLUE, (player_x, player_y, player_size, player_size))
    pygame.draw.circle(screen, RED, (int(enemy_x), int(enemy_y)), enemy_radius)

    # Draw health bar
    health_text = font.render(f"Health: {player_health}", True, WHITE)
    screen.blit(health_text, (10, 10))

    pygame.display.flip()

    # Check for game over
    if player_health <= 0:
        running = False

pygame.quit()
