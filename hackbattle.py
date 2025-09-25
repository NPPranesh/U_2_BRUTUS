import pygame
import sys
import random
import math
import os

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Vampire Survivors Clone")

try:
    BACKGROUND = pygame.image.load("background.jpeg").convert()
    BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))
except Exception:
    BACKGROUND = None


if os.path.exists("player.png"):
    PLAYER_IMG_RAW = pygame.image.load("player.png").convert_alpha()
    PLAYER_IMG = pygame.transform.scale(PLAYER_IMG_RAW, (60, 60))  # auto-scale
else:
    PLAYER_IMG = None

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
GRAY = (150, 150, 150)
DARK_GRAY = (80, 80, 80)
YELLOW = (255, 255, 0)
BLUE = (50, 150, 255)
PINK = (255, 100, 150)
PURPLE = (180, 0, 180)
ORANGE = (255, 165, 0)

FONT = pygame.font.SysFont("Arial", 36)
SMALL = pygame.font.SysFont("Arial", 20)


MENU = "menu"
GAME = "game"
LEVEL_UP = "level_up"
GAME_OVER = "game_over"
game_state = MENU

class Button:
    def __init__(self, text, x, y, w, h, color, hover_color, action=None, disabled=False):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.disabled = disabled

    def draw(self, screen):
        mouse = pygame.mouse.get_pos()
        if self.disabled:
            pygame.draw.rect(screen, DARK_GRAY, self.rect)
        elif self.rect.collidepoint(mouse):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)

        color = WHITE if not self.disabled else GRAY
        surf = SMALL.render(self.text, True, color) if len(self.text) > 18 else FONT.render(self.text, True, color)
        screen.blit(surf, surf.get_rect(center=self.rect.center))

    def click(self, event):
        if self.disabled:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.action:
                self.action()

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.speed = 5
        self.level = 1
        self.xp = 0
        self.xp_to_next = 5
        self.damage = 1
        self.max_hp = 5
        self.hp = self.max_hp
        self.xp_multiplier = 1.0
        self.magnet_radius = 0
        self.image = PLAYER_IMG  # Use loaded image if available

    def move(self, keys):
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.rect.y += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        self.rect.clamp_ip(SCREEN.get_rect())

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, GREEN, self.rect)

        pygame.draw.rect(screen, RED, (10, 40, 200, 20))
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, GREEN, (10, 40, 200 * hp_ratio, 20))

    def add_xp(self, amount):
        gained = int(amount * self.xp_multiplier)
        self.xp += gained
        if self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = int(self.xp_to_next * 1.5)
            return True
        return False

    def take_damage(self, amount):
        self.hp -= amount
        return self.hp <= 0

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

class Enemy:
    def __init__(self, x, y, strength, boss=False):
        size = 30 if not boss else 60
        self.rect = pygame.Rect(x, y, size, size)
        self.color = RED if not boss else PURPLE
        self.speed = 2 + strength * 0.1
        self.hp = (2 + strength) * (5 if boss else 1)
        self.damage = 1 if not boss else 2

    def move_towards_player(self, player):
        dx, dy = player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            dx, dy = dx / dist, dy / dist
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

class Bullet:
    def __init__(self, x, y, dx, dy, dmg):
        self.rect = pygame.Rect(int(x)-5, int(y)-5, 10, 10)
        self.dx, self.dy = dx, dy
        self.speed = 7
        self.damage = dmg

    def move(self):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed

    def draw(self, s):
        pygame.draw.rect(s, YELLOW, self.rect)

class OrbitingOrb:
    def __init__(self, player, radius=60, speed=0.05, damage=1):
        self.player = player
        self.radius = radius
        self.angle = 0
        self.speed = speed
        self.damage = damage
        self.size = 15
        self.rect = pygame.Rect(0, 0, self.size, self.size)

    def update(self):
        self.angle += self.speed
        cx, cy = self.player.rect.center
        self.rect.centerx = int(cx + math.cos(self.angle) * self.radius)
        self.rect.centery = int(cy + math.sin(self.angle) * self.radius)

    def draw(self, s):
        pygame.draw.circle(s, ORANGE, self.rect.center, self.size // 2)

class ExplosionSpell:
    def __init__(self, player, cooldown=4000, radius=100, damage=2):
        self.player = player
        self.cooldown = cooldown
        self.radius = radius
        self.damage = damage
        self.last_cast = pygame.time.get_ticks()
        self.active = False
        self.duration = 500
        self.start_time = 0

    def update(self, enemies, gems, hearts):
        now = pygame.time.get_ticks()
        if not self.active and now - self.last_cast >= self.cooldown:
            self.active = True
            self.start_time = now
            self.last_cast = now
            cx, cy = self.player.rect.center
            for e in enemies[:]:
                if math.hypot(e.rect.centerx - cx, e.rect.centery - cy) <= self.radius:
                    e.hp -= self.damage
                    if e.hp <= 0:
                        enemies.remove(e)
                        gems.append(XPGem(e.rect.x, e.rect.y))
                        if random.random() < 0.2:
                            hearts.append(Heart(e.rect.x, e.rect.y))
        if self.active and now - self.start_time >= self.duration:
            self.active = False

    def draw(self, screen):
        if self.active:
            pygame.draw.circle(screen, (255, 100, 0), self.player.rect.center, self.radius, 3)

class XPGem:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 12, 12)
    def draw(self, s): pygame.draw.rect(s,YELLOW, self.rect)

class Heart:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 14, 14)
    def draw(self, s): pygame.draw.rect(s, PINK, self.rect)

def upgrade_fire_rate():  global shoot_delay, game_state; shoot_delay = max(200, int(shoot_delay * 0.8)); game_state = GAME
def upgrade_damage():     global player, orbiting_orbs, explosion_spell, game_state; player.damage += 1; [setattr(o,"damage",o.damage+1) for o in orbiting_orbs]; explosion_spell.damage += 1; game_state = GAME
def upgrade_speed():      global player, game_state; player.speed += 1; game_state = GAME
def upgrade_orb():        global orbiting_orbs, player, game_state; orbiting_orbs.append(OrbitingOrb(player, 60+20*len(orbiting_orbs))) if len(orbiting_orbs)<3 else [setattr(o,"damage",o.damage+1) for o in orbiting_orbs]; game_state = GAME
def upgrade_max_hp():     global player, game_state; player.max_hp += 2; player.hp = player.max_hp; game_state = GAME
def upgrade_xp_boost():   global player, game_state; player.xp_multiplier += 0.25; game_state = GAME
def upgrade_magnet():     global player, game_state; player.magnet_radius += 50; game_state = GAME

UPGRADE_POOL = [
    {"name": "Increase Fire Rate", "func": upgrade_fire_rate, "rarity": "Common"},
    {"name": "Increase Damage", "func": upgrade_damage, "rarity": "Common"},
    {"name": "Increase Speed", "func": upgrade_speed, "rarity": "Common"},
    {"name": "Add/Upgrade Orb", "func": upgrade_orb, "rarity": "Rare"},
    {"name": "Max HP Boost",    "func": upgrade_max_hp, "rarity": "Rare"},
    {"name": "XP Boost",        "func": upgrade_xp_boost, "rarity": "Rare"},
    {"name": "Magnet Radius",   "func": upgrade_magnet, "rarity": "Epic"},
]

RARITY_COLOR = {
    "Common": GREEN,
    "Rare": ORANGE,
    "Epic": PURPLE,
}

def build_levelup_buttons():
    return [Button(up["name"], SCREEN_WIDTH//2-200, 220+80*i, 400, 50, RARITY_COLOR[up["rarity"]], GRAY, action=up["func"]) for i,up in enumerate(random.sample(UPGRADE_POOL,3))]

def start_game():
    global game_state, player, enemies, bullets, gems, hearts, orbiting_orbs, explosion_spell, shoot_delay, shoot_timer, enemy_timer, strength, start_time, upgrade_buttons
    game_state = GAME
    player = Player(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
    enemies, bullets, gems, hearts = [], [], [], []
    orbiting_orbs = [OrbitingOrb(player)]
    explosion_spell = ExplosionSpell(player)
    shoot_delay, shoot_timer, enemy_timer, strength = 1000, 0, 0, 0
    start_time = pygame.time.get_ticks()
    upgrade_buttons = []

def back_to_menu():  global game_state; game_state = MENU
start_btn = Button("Start Game", SCREEN_WIDTH//2-100, SCREEN_HEIGHT//2-40,200,80,RED,GRAY,action=start_game)
menu_btn = Button("Main Menu", SCREEN_WIDTH//2-100, SCREEN_HEIGHT//2+40,200,60,RED,GRAY,action=back_to_menu)

# --- Globals ---
player = None; enemies=[]; bullets=[]; gems=[]; hearts=[]; orbiting_orbs=[]; explosion_spell=None
shoot_delay=1000; shoot_timer=0; enemy_timer=0; strength=0; start_time=0; upgrade_buttons=[]

clock = pygame.time.Clock()
running=True
while running:
    SCREEN.blit(BACKGROUND,(0,0)) if BACKGROUND else SCREEN.fill(BLACK)
    for event in pygame.event.get():
        if event.type==pygame.QUIT: running=False
        if game_state==MENU: start_btn.click(event)
        elif game_state==LEVEL_UP:
            for b in upgrade_buttons: b.click(event)
        elif game_state==GAME_OVER: menu_btn.click(event)

    # --- MENU ---
    if game_state==MENU:
        SCREEN.blit(FONT.render("Ceaser",True,WHITE),(SCREEN_WIDTH//2-70,150))
        start_btn.draw(SCREEN)
    # --- GAME ---
    elif game_state==GAME:
        keys=pygame.key.get_pressed(); player.move(keys); player.draw(SCREEN)
        pygame.draw.rect(SCREEN,WHITE,(10,10,200,20),2)
        pygame.draw.rect(SCREEN,BLUE,(10,10,200*player.xp/player.xp_to_next,20))
        elapsed=(pygame.time.get_ticks()-start_time)//1000
        SCREEN.blit(FONT.render(f"{elapsed//60:02}:{elapsed%60:02}",True,WHITE),(SCREEN_WIDTH//2-40,10))
        now=pygame.time.get_ticks()

        if now-enemy_timer>2000: enemies.append(Enemy(random.randint(0,SCREEN_WIDTH),0,strength)); enemy_timer=now
        if now-shoot_timer>shoot_delay and enemies:
            e=min(enemies,key=lambda en:math.hypot(en.rect.centerx-player.rect.centerx,en.rect.centery-player.rect.centery))
            dx,dy=e.rect.centerx-player.rect.centerx,e.rect.centery-player.rect.centery; d=math.hypot(dx,dy)
            if d>0: bullets.append(Bullet(player.rect.centerx,player.rect.centery,dx/d,dy/d,player.damage))
            shoot_timer=now

        for b in bullets[:]:
            b.move(); b.draw(SCREEN)
            if not SCREEN.get_rect().colliderect(b.rect): bullets.remove(b); continue
            for en in enemies[:]:
                if b.rect.colliderect(en.rect):
                    en.hp-=b.damage; bullets.remove(b)
                    if en.hp<=0: enemies.remove(en); gems.append(XPGem(en.rect.x,en.rect.y))
                    break

        for o in orbiting_orbs:
            o.update(); o.draw(SCREEN)
            for en in enemies[:]:
                if o.rect.colliderect(en.rect):
                    en.hp-=o.damage
                    if en.hp<=0: enemies.remove(en); gems.append(XPGem(en.rect.x,en.rect.y))

        explosion_spell.update(enemies,gems,hearts); explosion_spell.draw(SCREEN)

        for g in gems[:]:
            g.draw(SCREEN)
            dx,dy=player.rect.centerx-g.rect.centerx,player.rect.centery-g.rect.centery; d=math.hypot(dx,dy)
            if player.magnet_radius>0 and d<=player.magnet_radius and d>0: g.rect.move_ip(int(dx/d*4),int(dy/d*4))
            if player.rect.colliderect(g.rect):
                gems.remove(g); leveled=player.add_xp(1)
                if leveled: upgrade_buttons=build_levelup_buttons(); game_state=LEVEL_UP

        for h in hearts[:]:
            h.draw(SCREEN)
            if player.rect.colliderect(h.rect): hearts.remove(h); player.heal(1)

        # --- FIXED ENEMY COLLISION ---
        for en in enemies[:]:
            en.move_towards_player(player); en.draw(SCREEN)
            if player.rect.colliderect(en.rect):
                dead=player.take_damage(en.damage); enemies.remove(en)
                if dead: game_state=GAME_OVER

    # --- LEVEL UP ---
    elif game_state==LEVEL_UP:
        SCREEN.blit(FONT.render("LEVEL UP! Choose:",True,WHITE),(SCREEN_WIDTH//2-150,150))
        for b in upgrade_buttons: b.draw(SCREEN)

    # --- GAME OVER ---
    elif game_state==GAME_OVER:
        SCREEN.blit(FONT.render("GAME OVER",True,WHITE),(SCREEN_WIDTH//2-100,200))
        menu_btn.draw(SCREEN)

    pygame.display.flip(); clock.tick(60)

pygame.quit(); sys.exit()
