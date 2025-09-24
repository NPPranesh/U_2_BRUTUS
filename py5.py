import pygame
import random
import math

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
# NOTE: Make sure to have a file named 'cave_pixel.png' in the same directory.
try:
    background = pygame.image.load("cave_pixel.png")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
except pygame.error:
    print("Warning: 'cave_pixel.png' not found. Using a black background.")
    background = None
# Player
player_width = 80
player_height = 80
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - player_height - 10
player_speed = 5

# --- Player Sprite Loading ---
# NOTE: Save your uploaded image as 'player_sprite.png' in the same directory.
try:
    player_image = pygame.image.load("character.png").convert_alpha()
    player_image = pygame.transform.scale(player_image, (player_width, player_height))
except pygame.error:
    print("Warning: 'player_sprite.png' not found. Using a blue rectangle as fallback.")
    player_image = pygame.Surface((player_width, player_height))
    player_image.fill((0, 0, 255))

# Bullets
bullet_size = 10
bullet_speed = 10
bullets = []
last_shot_time = 0
bullet_cooldown = 200  # milliseconds

# Enemy
enemy_radius = 25
enemy_speed = 2
enemies = []


# Function to spawn a new enemy from a random side (top, left, or right)
def spawn_enemy():
    """Generates a new enemy dictionary with a random spawn location."""
    spawn_side = random.choice(["top", "left", "right"])

    if spawn_side == "top":
        x = random.randint(enemy_radius, WIDTH - enemy_radius)
        y = random.randint(50, 200)
    elif spawn_side == "left":
        x = -enemy_radius  # Spawn just off-screen
        y = random.randint(enemy_radius, HEIGHT - enemy_radius)
    else:  # "right"
        x = WIDTH + enemy_radius  # Spawn just off-screen
        y = random.randint(enemy_radius, HEIGHT - enemy_radius)

    return {
        "x": x,
        "y": y,
        "color": random.choice(RED_SHADES),
        "speed": enemy_speed
    }


# Spawn initial enemies
for _ in range(5):
    enemies.append(spawn_enemy())

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
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill((0, 0, 0))  # Fallback to black

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x - player_speed > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x + player_speed + player_width < WIDTH:
        player_x += player_speed
    if keys[pygame.K_UP] and player_y - player_speed > 0:
        player_y -= player_speed
    if keys[pygame.K_DOWN] and player_y + player_speed + player_height < HEIGHT:
        player_y += player_speed

    # Manual shooting with cooldown
    current_time = pygame.time.get_ticks()

    bullet_spawn_x = player_x + player_width // 2
    bullet_spawn_y = player_y + player_height // 2

    if keys[pygame.K_w] and current_time - last_shot_time > bullet_cooldown:
        bullets.append({"x": bullet_spawn_x, "y": bullet_spawn_y, "vx": 0, "vy": -bullet_speed})
        last_shot_time = current_time
    elif keys[pygame.K_s] and current_time - last_shot_time > bullet_cooldown:
        bullets.append({"x": bullet_spawn_x, "y": bullet_spawn_y, "vx": 0, "vy": bullet_speed})
        last_shot_time = current_time
    elif keys[pygame.K_a] and current_time - last_shot_time > bullet_cooldown:
        bullets.append({"x": bullet_spawn_x, "y": bullet_spawn_y, "vx": -bullet_speed, "vy": 0})
        last_shot_time = current_time
    elif keys[pygame.K_d] and current_time - last_shot_time > bullet_cooldown:
        bullets.append({"x": bullet_spawn_x, "y": bullet_spawn_y, "vx": bullet_speed, "vy": 0})
        last_shot_time = current_time

    # Move bullets based on their velocity vectors
    for bullet in bullets[:]:
        bullet["x"] += bullet["vx"]
        bullet["y"] += bullet["vy"]
        # Remove bullets that go off-screen
        if bullet["x"] < 0 or bullet["x"] > WIDTH or bullet["y"] < 0 or bullet["y"] > HEIGHT:
            bullets.remove(bullet)

    # Draw bullets
    for bullet in bullets:
        pygame.draw.circle(screen, WHITE, (int(bullet["x"]), int(bullet["y"])), 5)

    # Move and draw enemies
    for enemy in enemies[:]:
        # Enemy chases player
        dx = (player_x + player_width / 2) - enemy["x"]
        dy = (player_y + player_height / 2) - enemy["y"]
        dist = math.hypot(dx, dy)
        if dist != 0:
            enemy["x"] += (dx / dist) * enemy["speed"]
            enemy["y"] += (dy / dist) * enemy["speed"]

        # Collision with player
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        enemy_rect = pygame.Rect(enemy["x"] - enemy_radius, enemy["y"] - enemy_radius, enemy_radius * 2,
                                 enemy_radius * 2)
        if player_rect.colliderect(enemy_rect):
            player_health -= 1

        # Collision with bullets
        for bullet in bullets[:]:
            bullet_dist = math.hypot(bullet["x"] - enemy["x"], bullet["y"] - enemy["y"])
            if bullet_dist < enemy_radius + 5:  # 5 is bullet radius
                bullets.remove(bullet)
                enemies.remove(enemy)
                enemies.append(spawn_enemy())

        pygame.draw.circle(screen, enemy["color"], (int(enemy["x"]), int(enemy["y"])), enemy_radius)

    # Draw the player image
    screen.blit(player_image, (player_x, player_y))

    # Draw health
    health_text = font.render(f"Health: {player_health}", True, WHITE)
    screen.blit(health_text, (10, 10))

    pygame.display.flip()

    if player_health <= 0:
        running = False

pygame.quit()