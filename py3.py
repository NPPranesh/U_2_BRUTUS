import pygame
import random

# Initialize Pygame
pygame.init()

# Screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Cave Battle")

# Colors
WHITE = (255, 255, 255)
RED_SHADES = [(139, 0, 0), (178, 34, 34), (220, 20, 60), (255, 0, 0)]  # evil enemy shades

# Load background
background = pygame.image.load("cave_pixel.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Load player sprite
player_img = pygame.image.load("player.png").convert_alpha()  # transparent PNG
player_size = 50
player_img = pygame.transform.scale(player_img, (player_size, player_size))
player_x = WIDTH // 2
player_y = HEIGHT - player_size - 10
player_speed = 5

# Bullets
bullet_speed = 10
bullets = []

# Enemy
enemy_radius = 25
enemy_speed = 2
enemies = []

# Spawn multiple enemies
for _ in range(5):
    enemies.append({
        "x": random.randint(enemy_radius, WIDTH - enemy_radius),
        "y": random.randint(50, 200),
        "color": random.choice(RED_SHADES),
        "speed": enemy_speed
    })

# Health
player_health = 100
font = pygame.font.SysFont(None, 30)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Game loop
running = True
while running:
    clock.tick(FPS)
    screen.blit(background, (0, 0))

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

    # Auto-shooting bullets
    if len(bullets) == 0 or bullets[-1]["y"] < player_y - 100:
        bullets.append({"x": player_x + player_size // 2, "y": player_y})

    # Move bullets
    for bullet in bullets[:]:
        bullet["y"] -= bullet_speed
        if bullet["y"] < 0:
            bullets.remove(bullet)

    # Draw bullets
    for bullet in bullets:
        pygame.draw.rect(screen, WHITE, (bullet["x"] - 5, bullet["y"], 10, 20))

    # Move and draw enemies
    for enemy in enemies[:]:
        # Enemy chases player
        if enemy["x"] < player_x + player_size // 2:
            enemy["x"] += enemy["speed"]
        elif enemy["x"] > player_x + player_size // 2:
            enemy["x"] -= enemy["speed"]
        if enemy["y"] < player_y + player_size // 2:
            enemy["y"] += enemy["speed"]
        elif enemy["y"] > player_y + player_size // 2:
            enemy["y"] -= enemy["speed"]

        # Collision with player
        if abs(player_x + player_size // 2 - enemy["x"]) < enemy_radius + player_size // 2 and \
                abs(player_y + player_size // 2 - enemy["y"]) < enemy_radius + player_size // 2:
            player_health -= 1

        # Collision with bullets
        for bullet in bullets[:]:
            if abs(bullet["x"] - enemy["x"]) < enemy_radius and abs(bullet["y"] - enemy["y"]) < enemy_radius:
                bullets.remove(bullet)
                enemies.remove(enemy)
                # Spawn new enemy
                enemies.append({
                    "x": random.randint(enemy_radius, WIDTH - enemy_radius),
                    "y": random.randint(50, 200),
                    "color": random.choice(RED_SHADES),
                    "speed": enemy_speed
                })

        pygame.draw.circle(screen, enemy["color"], (int(enemy["x"]), int(enemy["y"])), enemy_radius)

    # Draw player
    screen.blit(player_img, (player_x, player_y))

    # Draw health
    health_text = font.render(f"Health: {player_health}", True, WHITE)
    screen.blit(health_text, (10, 10))

    pygame.display.flip()

    if player_health <= 0:
        running = False

pygame.quit()
