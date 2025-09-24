import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("WASD Avoidance Game (Multiple Enemies)")

# Colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Font for text
font = pygame.font.Font(None, 50)

# Player properties
player_size = 50
player_x = screen_width // 2 - player_size // 2
player_y = screen_height - player_size - 10
player_speed = 0.7

# Enemy properties
enemy_size = 50
enemy_speed = 0.3  # Changed to a decimal value
num_enemies = 3

# Create a list to hold all enemies
enemies = []

# List to hold the enemies' precise, floating-point positions
enemy_positions = []


def create_enemy():
    x = random.randint(0, screen_width - enemy_size)
    y = 0
    enemy_positions.append([float(x), float(y)])
    return pygame.Rect(x, y, enemy_size, enemy_size)


# Populate the enemy list initially
for _ in range(num_enemies):
    enemies.append(create_enemy())


# --- Start Screen with 3-second delay ---
def show_start_screen():
    screen.fill(BLACK)
    text = font.render("Get Ready!", True, WHITE)
    text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()

    # Pause for 3 seconds
    pygame.time.wait(3000)


show_start_screen()

# Game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get state of all keyboard buttons for smooth movement
    keys = pygame.key.get_pressed()

    # Player movement
    if keys[pygame.K_a]:
        player_x -= player_speed
    if keys[pygame.K_d]:
        player_x += player_speed
    if keys[pygame.K_w]:
        player_y -= player_speed
    if keys[pygame.K_s]:
        player_y += player_speed

    # Keep the player on screen
    if player_x < 0:
        player_x = 0
    if player_x > screen_width - player_size:
        player_x = screen_width - player_size
    if player_y < 0:
        player_y = 0
    if player_y > screen_height - player_size:
        player_y = screen_height - player_size

    # Move, check boundaries, and check collisions for EACH enemy in the list
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

    for i, enemy in enumerate(enemies):
        # Move the enemy using the floating-point position
        enemy_positions[i][1] += enemy_speed

        # Update the enemy's Rect position by rounding the float
        enemy.y = round(enemy_positions[i][1])

        # Reset enemy if it goes off-screen
        if enemy.y > screen_height:
            enemy_positions[i][1] = 0.0  # Reset float position
            enemy_positions[i][0] = float(random.randint(0, screen_width - enemy_size))
            enemy.x = round(enemy_positions[i][0])

        # Collision detection with the player
        if player_rect.colliderect(enemy):
            running = False  # End the game

    # Drawing
    screen.fill(BLACK)
    pygame.draw.rect(screen, RED, player_rect)

    # Draw EACH enemy in the list
    for enemy in enemies:
        pygame.draw.rect(screen, GREEN, enemy)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()