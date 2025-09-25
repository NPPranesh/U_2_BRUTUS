import pygame
import math
import random
import sys
from pathlib import Path

# ----------------- Configuration -----------------
PLAYER_SPRITE_PATH = "player.png"
TILESET_PATH = "roguelikeDungeon_transparent.png"
SCREEN_W, SCREEN_H = 800, 600
TILE_SIZE = 32
FPS = 60
PLAYER_SPEED = 4
BULLET_SPEED = 10
ENEMY_SPEED = 1.8
ENEMY_COUNT = 5
# --------------------------------------------------

pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("2D Sprite Game — Rewritten")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 20)

# --- Safe image loader with fallback ---
def safe_load(path, convert_alpha=True):
    p = Path(path)
    if not p.exists():
        # create placeholder surface if file missing
        s = pygame.Surface((64, 64), pygame.SRCALPHA)
        s.fill((200, 50, 50, 255))
        pygame.draw.line(s, (0,0,0), (0,0),(63,63),3)
        pygame.draw.line(s, (0,0,0), (63,0),(0,63),3)
        return s
    img = pygame.image.load(str(p))
    return img.convert_alpha() if convert_alpha else img.convert()

# Load spritesheets (safe)
player_sprite = safe_load(PLAYER_SPRITE_PATH)
tileset = safe_load(TILESET_PATH)

# --- Auto-detect frame size (tries common sizes) ---
sheet_w = player_sprite.get_width()
sheet_h = player_sprite.get_height()
possible_sizes = [8, 16, 24, 32, 48, 64]
sprite_w = sprite_h = None
for s in possible_sizes:
    if sheet_w % s == 0 and sheet_h % s == 0 and (sheet_w // s) <= 12 and (sheet_h // s) <= 12:
        sprite_w = s
        sprite_h = s
        break
# Fallback heuristics
if sprite_w is None:
    if sheet_w % 3 == 0 and sheet_h % 4 == 0:
        sprite_w = sheet_w // 3
        sprite_h = sheet_h // 4
    else:
        sprite_w = 32
        sprite_h = 32

frames_per_row = sheet_w // sprite_w
rows = sheet_h // sprite_h

# clamp minimal sizes
frames_per_row = max(1, frames_per_row)
rows = max(1, rows)

# Helper to extract tiles safely from tileset
tileset_w = tileset.get_width()
tileset_h = tileset.get_height()
tiles_x = max(1, tileset_w // TILE_SIZE)
tiles_y = max(1, tileset_h // TILE_SIZE)

def get_tile(tx, ty):
    if 0 <= tx < tiles_x and 0 <= ty < tiles_y:
        rect = pygame.Rect(tx * TILE_SIZE, ty * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        return tileset.subsurface(rect).copy()
    # fallback: empty tile
    s = pygame.Surface((TILE_SIZE, TILE_SIZE))
    s.fill((150, 150, 150))
    return s

# Extract animation frames for row (safe)
def get_frames_for_row(row_idx):
    if row_idx >= rows:
        row_idx = rows - 1
    frames = []
    for c in range(frames_per_row):
        rect = pygame.Rect(c * sprite_w, row_idx * sprite_h, sprite_w, sprite_h)
        # safety clamp: if rect goes beyond, break
        if rect.right <= sheet_w and rect.bottom <= sheet_h:
            frames.append(player_sprite.subsurface(rect).copy())
    # ensure at least one frame exists
    if not frames:
        fallback = pygame.Surface((sprite_w, sprite_h), pygame.SRCALPHA)
        fallback.fill((255, 0, 255, 128))
        frames = [fallback]
    return frames

# Directions mapping to rows (safe: clamp to available rows)
direction_rows = {"down": 0, "left": 1, "right": 2, "up": 3}
animations = {}
for d, r in direction_rows.items():
    animations[d] = get_frames_for_row(min(r, rows - 1))

# Simple tile map (fits 25 cols x 6 rows -> 800x192)
level_map = [
    [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],
    [2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2],
    [2,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,2],
    [2,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,2],
    [2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2],
    [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],
]
# Map tile graphics (use safe get_tile)
tile_graphics = {
    0: get_tile(0, 5),    # water (safe fallback if out of bounds)
    1: get_tile(5, 5),    # sand
    2: get_tile(8, 2),    # wood
}

# Game state
player_x = SCREEN_W // 2
player_y = SCREEN_H // 2
direction = "down"
frame_index = 0
frame_delay = 10
frame_counter = 0

bullets = []  # each bullet: dict x,y,vx,vy
enemies = []

def spawn_enemy():
    # spawn away from player
    while True:
        x = random.randint(0, SCREEN_W)
        y = random.randint(0, SCREEN_H)
        if math.hypot(x - player_x, y - player_y) > 120:
            break
    radius = random.randint(12, 20)
    color = (150 + random.randint(0,80), 20 + random.randint(0,40), 20 + random.randint(0,40))
    return {"x": x, "y": y, "r": radius, "col": color}

for _ in range(ENEMY_COUNT):
    enemies.append(spawn_enemy())

# Helper drawing functions
def draw_map():
    for r, row in enumerate(level_map):
        for c, t in enumerate(row):
            tile = tile_graphics.get(t)
            if tile:
                screen.blit(tile, (c * TILE_SIZE, r * TILE_SIZE))

def draw_player():
    frame_list = animations.get(direction, [animations["down"][0]])
    # ensure frame_index in range for this direction
    idx = frame_index % len(frame_list)
    surf = frame_list[idx]
    # center player at its coordinates
    px = int(player_x - surf.get_width() // 2)
    py = int(player_y - surf.get_height() // 2)
    screen.blit(surf, (px, py))

def draw_bullets():
    for b in bullets:
        pygame.draw.circle(screen, (30, 144, 255), (int(b["x"]), int(b["y"])), 4)

def draw_enemies():
    for e in enemies:
        pygame.draw.circle(screen, e["col"], (int(e["x"]), int(e["y"])), e["r"])
        # small health bar (visual only)
        pygame.draw.rect(screen, (0,0,0), (e["x"]-e["r"], e["y"]-e["r"]-8, e["r"]*2, 4))
        pygame.draw.rect(screen, (0,200,0), (e["x"]-e["r"]+1, e["y"]-e["r"]-7, int((e["r"]*2-2)), 3))

# Main loop
running = True
while running:
    dt = clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                # shoot a bullet in current facing direction
                bx = player_x
                by = player_y
                if direction == "left":
                    vx, vy = -BULLET_SPEED, 0
                elif direction == "right":
                    vx, vy = BULLET_SPEED, 0
                elif direction == "up":
                    vx, vy = 0, -BULLET_SPEED
                else:  # down
                    vx, vy = 0, BULLET_SPEED
                bullets.append({"x": bx, "y": by, "vx": vx, "vy": vy})

    keys = pygame.key.get_pressed()
    moving = False
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_x -= PLAYER_SPEED
        direction = "left"
        moving = True
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_x += PLAYER_SPEED
        direction = "right"
        moving = True
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player_y -= PLAYER_SPEED
        direction = "up"
        moving = True
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player_y += PLAYER_SPEED
        direction = "down"
        moving = True

    # keep player on-screen
    player_x = max(0, min(SCREEN_W, player_x))
    player_y = max(0, min(SCREEN_H, player_y))

    # animate player
    if moving:
        frame_counter += 1
        if frame_counter >= frame_delay:
            frame_index = (frame_index + 1) % frames_per_row
            frame_counter = 0
    else:
        frame_index = 0
        frame_counter = 0

    # update bullets
    for b in bullets[:]:
        b["x"] += b["vx"]
        b["y"] += b["vy"]
        # remove off-screen bullets
        if b["x"] < -10 or b["x"] > SCREEN_W + 10 or b["y"] < -10 or b["y"] > SCREEN_H + 10:
            bullets.remove(b)

    # update enemies (chase player)
    for e in enemies:
        dx = player_x - e["x"]
        dy = player_y - e["y"]
        dist = math.hypot(dx, dy)
        if dist != 0:
            e["x"] += dx / dist * ENEMY_SPEED
            e["y"] += dy / dist * ENEMY_SPEED

    # bullet-enemy collisions
    for b in bullets[:]:
        for e in enemies[:]:
            if math.hypot(b["x"] - e["x"], b["y"] - e["y"]) < e["r"]:
                # hit: remove enemy and bullet, spawn new enemy after short delay (instant spawn here)
                try:
                    bullets.remove(b)
                except ValueError:
                    pass
                try:
                    enemies.remove(e)
                except ValueError:
                    pass
                enemies.append(spawn_enemy())
                break

    # enemy-player collision (simple game over)
    for e in enemies:
        if math.hypot(player_x - e["x"], player_y - e["y"]) < e["r"] + 8:
            # simple visual feedback then exit
            text = font.render("You were caught! Game over — press ESC to quit.", True, (255, 255, 255))
            screen.blit(text, (20, SCREEN_H - 30))
            pygame.display.flip()
            pygame.time.delay(1200)
            running = False
            break

    # draw
    screen.fill((100, 120, 140))
    draw_map()
    draw_bullets()
    draw_enemies()
    draw_player()

    # HUD
    hud = font.render(f"Enemies: {len(enemies)} | FramesPerRow: {frames_per_row} | Rows: {rows} | SpriteSize: {sprite_w}x{sprite_h}", True, (255,255,255))
    screen.blit(hud, (8, SCREEN_H - 22))

    pygame.display.flip()

pygame.quit()
sys.exit()
