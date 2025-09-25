import pygame
import sys
import random
import math
import os

pygame.init()

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 750
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ceaser")

# Load background
try:
    BACKGROUND = pygame.image.load("background.png").convert()
    BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))
except Exception:
    BACKGROUND = None

# Load player image
if os.path.exists("player.png"):
    PLAYER_IMG_RAW = pygame.image.load("player.png").convert_alpha()
    PLAYER_IMG = pygame.transform.scale(PLAYER_IMG_RAW, (60, 60))
else:
    PLAYER_IMG = None

BULLET_IMG_RAW = pygame.image.load("bullet.png").convert_alpha()
BULLET_IMG = pygame.transform.scale(BULLET_IMG_RAW, (40, 40))  # adjust size as needed

BOSS_IMG_RAW = pygame.image.load("boss.png").convert_alpha()
BOSS_IMG = pygame.transform.scale(BOSS_IMG_RAW, (100, 100))

MINION_IMG_RAW = pygame.image.load("enemy.png").convert_alpha()
MINION_IMG = pygame.transform.scale(MINION_IMG_RAW, (60, 60))

XP_GEM_IMG_RAW = pygame.image.load("xp_gem.png").convert_alpha()
XP_GEM_IMG = pygame.transform.scale(XP_GEM_IMG_RAW, (30, 30))

HEART_IMG_RAW = pygame.image.load("heart.png").convert_alpha()
HEART_IMG = pygame.transform.scale(HEART_IMG_RAW, (30, 30))

ORB_IMG_RAW = pygame.image.load("orb.png").convert_alpha()
ORB_IMG = pygame.transform.scale(ORB_IMG_RAW, (15, 15))  # adjust size as needed

# Colors and fonts
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
RED, GREEN, GRAY, DARK_GRAY = (200, 0, 0), (0, 200, 0), (150, 150, 150), (80, 80, 80)
YELLOW, BLUE, PINK, PURPLE, ORANGE = (255, 255, 0), (50, 150, 255), (255, 100, 150), (180, 0, 180), (255, 165, 0)
FONT = pygame.font.SysFont("Arial", 36)
SMALL = pygame.font.SysFont("Arial", 20)

# Game states
MENU, GAME, LEVEL_UP, GAME_OVER = "menu", "game", "level_up", "game_over"
game_state = MENU

# ---------------- BUTTON CLASS ----------------
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

# ---------------- PLAYER CLASS ----------------
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
        self.image = PLAYER_IMG
        self.life_steal = 0.0

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
        # HP bar
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

# ---------------- ENEMY CLASS ----------------
class Enemy:
    def __init__(self, x, y, strength, boss=False):
        size = 30 if not boss else 100
        self.rect = pygame.Rect(x, y, size, size)
        self.color = RED if not boss else PURPLE
        self.speed = 2 + strength * 0.1
        self.hp = (2 + strength) * (5 if boss else 1)
        self.damage = 1 if not boss else 2
        self.boss = boss

    def move_towards_player(self, player):
        dx, dy = player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            dx, dy = dx / dist, dy / dist
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed

    def draw(self, screen):
        if not self.boss and MINION_IMG:
            screen.blit(MINION_IMG, self.rect)
        elif self.boss and BOSS_IMG:
            screen.blit(BOSS_IMG, self.rect)

class Boss(Enemy):
    def __init__(self, x, y, strength):
        super().__init__(x, y, strength, boss=True)
        self.rect = pygame.Rect(x, y, 100, 100)
        self.max_hp = 100 + strength * 30
        self.hp = self.max_hp
        self.speed = 1.5
        self.damage = 15
        self.phase = 1
        self.spawn_cd = 3000
        self.last_spawn = pygame.time.get_ticks()
        self.color_phase1 = PURPLE
        self.color_phase2 = ORANGE  # Phase 2 color

    def update(self, player, enemies, strength):
        self.move_towards_player(player)
        if self.hp < self.max_hp // 2 and self.phase == 1:
            self.phase = 2
            self.speed += 1.0
            self.damage += 5
        if self.phase == 2:
            now = pygame.time.get_ticks()
            if now - self.last_spawn >= self.spawn_cd:
                for _ in range(3):
                    ex = self.rect.centerx + random.randint(-80, 80)
                    ey = self.rect.centery + random.randint(-80, 80)
                    enemies.append(Enemy(ex, ey, strength))
                self.last_spawn = now

    def draw(self, screen):
        if BOSS_IMG:
            screen.blit(BOSS_IMG, self.rect)
        # HP bar
        bar_w = 300
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(screen, RED, (SCREEN_WIDTH // 2 - bar_w // 2, 70, bar_w, 20))
        pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH // 2 - bar_w // 2, 70, int(bar_w * ratio), 20))
        text = SMALL.render("BOSS", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 50))


# ---------------- BULLET, ORB, EXPLOSION ----------------
class Bullet:
    def __init__(self, x, y, dx, dy, dmg):
        self.rect = pygame.Rect(int(x)-5, int(y)-5, 10, 10)
        self.dx, self.dy = dx, dy
        self.speed = 7
        self.damage = dmg
        self.angle = math.degrees(math.atan2(-dy, dx))
        self.image = pygame.transform.rotate(BULLET_IMG, self.angle)

    def move(self):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed

    def draw(self, s):
        img_rect = self.image.get_rect(center=self.rect.center)
        s.blit(self.image, img_rect)

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
        img_rect = ORB_IMG.get_rect(center=self.rect.center)
        s.blit(ORB_IMG, img_rect)

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
                    self.player.hp = min(self.player.max_hp, self.player.hp + e.damage*self.player.life_steal)
                    if e.hp <= 0:
                        if isinstance(e,Boss):
                            continue
                        enemies.remove(e)
                        gems.append(XPGem(e.rect.x, e.rect.y))
                        if random.random() < 0.2:
                            hearts.append(Heart(e.rect.x, e.rect.y))
        if self.active and now - self.start_time >= self.duration:
            self.active = False

    def draw(self, screen):
        if self.active:
            pygame.draw.circle(screen, (255, 100, 0), self.player.rect.center, self.radius, 3)

# ---------------- GEMS & HEARTS ----------------
class XPGem:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 12, 12)
    def draw(self, s):
            s.blit(XP_GEM_IMG, self.rect)
class Heart:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 14, 14)
    def draw(self, s):
        s.blit(HEART_IMG, self.rect)

#---------------- UPGRADES ----------------
def upgrade_fire_rate():  global shoot_delay, game_state; shoot_delay = max(200, int(shoot_delay * 0.8)); game_state = GAME
def upgrade_damage():     global player, orbiting_orbs, explosion_spell, game_state; player.damage += 1; [setattr(o,"damage",o.damage+1) for o in orbiting_orbs]; explosion_spell.damage += 1; game_state = GAME
def upgrade_speed():      global player, game_state; player.speed += 1; game_state = GAME
def upgrade_orb():        global orbiting_orbs, player, game_state; orbiting_orbs.append(OrbitingOrb(player, 60+20*len(orbiting_orbs))) if len(orbiting_orbs)<3 else [setattr(o,"damage",o.damage+1) for o in orbiting_orbs]; game_state = GAME
def upgrade_max_hp():     global player, game_state; player.max_hp += 2; player.hp = player.max_hp; game_state = GAME
def upgrade_xp_boost():   global player, game_state; player.xp_multiplier += 0.25; game_state = GAME
def upgrade_magnet():     global player, game_state; player.magnet_radius += 50; game_state = GAME
def upgrade_explosion():  global explosion_spell, game_state; explosion_spell.damage +=1; game_state = GAME
def upgrade_orb_speed():  global orbiting_orbs, game_state; [setattr(o,"speed",o.speed+0.02) for o in orbiting_orbs]; game_state=GAME
def upgrade_life_steal(): global player, game_state; player.life_steal += 0.05; game_state=GAME

UPGRADE_POOL = [
    {"name": "Increase Damage", "func": upgrade_damage, "rarity": "Common"},
    {"name": "Increase Speed", "func": upgrade_speed, "rarity": "Common"},
    {"name": "Add/Upgrade Orb", "func": upgrade_orb, "rarity": "Rare"},
    {"name": "Max HP Boost",    "func": upgrade_max_hp, "rarity": "Rare"},
    {"name": "XP Boost",        "func": upgrade_xp_boost, "rarity": "Rare"},
    {"name": "Magnet Radius",   "func": upgrade_magnet, "rarity": "Epic"},
    {"name": "Explosion Damage+", "func": upgrade_explosion, "rarity": "Rare"},
    {"name": "Orb Speed+",      "func": upgrade_orb_speed, "rarity": "Rare"},
    {"name": "Life Steal",      "func": upgrade_life_steal, "rarity": "Epic"},
]

RARITY_COLOR = {"Common": GREEN, "Rare": ORANGE, "Epic": PURPLE}

def build_levelup_buttons():
    return [Button(up["name"], SCREEN_WIDTH//2-200, 220+80*i, 400, 50, RARITY_COLOR[up["rarity"]], GRAY, action=up["func"]) for i,up in enumerate(random.sample(UPGRADE_POOL,3))]

# ---------------- GAME FUNCTIONS ----------------
def start_game():
    global game_state, player, enemies, bullets, gems, hearts, orbiting_orbs, explosion_spell, shoot_delay, shoot_timer, enemy_timer, strength, start_time, upgrade_buttons, boss
    game_state = GAME
    player = Player(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
    enemies, bullets, gems, hearts = [], [], [], []
    orbiting_orbs = [OrbitingOrb(player)]
    explosion_spell = ExplosionSpell(player)
    shoot_delay, shoot_timer, enemy_timer, strength = 1000, 0, 0, 0
    start_time = pygame.time.get_ticks()
    upgrade_buttons = []
    boss = None

def back_to_menu():
    global game_state
    game_state = MENU

start_btn = Button("Start Game", SCREEN_WIDTH//2-100, SCREEN_HEIGHT//2-40,200,80,RED,GRAY,action=start_game)
menu_btn = Button("Main Menu", SCREEN_WIDTH//2-100, SCREEN_HEIGHT//2+40,200,60,RED,GRAY,action=back_to_menu)

# ---------------- GLOBALS ----------------
player=None; enemies=[]; bullets=[]; gems=[]; hearts=[]; orbiting_orbs=[]; explosion_spell=None
shoot_delay=1000; shoot_timer=0; enemy_timer=0; strength=0; start_time=0; upgrade_buttons=[]
boss=None

# ---------------- MAIN LOOP ----------------
clock = pygame.time.Clock()
running = True
while running:
    SCREEN.blit(BACKGROUND,(0,0)) if BACKGROUND else SCREEN.fill(BLACK)
    for event in pygame.event.get():
        if event.type==pygame.QUIT: running=False
        if game_state==MENU: start_btn.click(event)
        elif game_state==LEVEL_UP: [b.click(event) for b in upgrade_buttons]
        elif game_state==GAME_OVER: menu_btn.click(event)

    if game_state==MENU:
        SCREEN.blit(FONT.render("Ceaser",True,WHITE),(SCREEN_WIDTH//2-70,150))
        start_btn.draw(SCREEN)

    elif game_state==GAME:
        keys=pygame.key.get_pressed()
        player.move(keys)
        player.draw(SCREEN)
        # XP bar
        pygame.draw.rect(SCREEN,WHITE,(10,10,200,20),2)
        pygame.draw.rect(SCREEN,BLUE,(10,10,200*player.xp/player.xp_to_next,20))
        elapsed=(pygame.time.get_ticks()-start_time)//1000
        SCREEN.blit(FONT.render(f"{elapsed//60:02}:{elapsed%60:02}",True,WHITE),(SCREEN_WIDTH//2-40,10))
        now=pygame.time.get_ticks()

        # Spawn enemies
        if now-enemy_timer>2000:
            enemies.append(Enemy(random.randint(0,SCREEN_WIDTH),0,strength));
            enemy_timer=now


        # Spawn boss every 25s if none
        if boss is None and elapsed%25==0 and elapsed>0:
            boss = Boss(random.randint(100, SCREEN_WIDTH-100), -100, strength)
            enemies.append(boss)

        # Auto aim shoot
        Justkey = pygame.key.get_just_pressed()
        if Justkey[pygame.K_SPACE] and enemies:
            e=min(enemies,key=lambda en:math.hypot(en.rect.centerx-player.rect.centerx,en.rect.centery-player.rect.centery))
            dx,dy=e.rect.centerx-player.rect.centerx,e.rect.centery-player.rect.centery; d=math.hypot(dx,dy)
            if d>0: bullets.append(Bullet(player.rect.centerx,player.rect.centery,dx/d,dy/d,player.damage))
            shoot_timer=now

        # Bullets
        for b in bullets[:]:
            b.move(); b.draw(SCREEN)
            if not SCREEN.get_rect().colliderect(b.rect): bullets.remove(b); continue
            for en in enemies[:]:
                if b.rect.colliderect(en.rect):
                    en.hp-=b.damage
                    bullets.remove(b)
                    if en.hp<=0:
                        if isinstance(en,Boss):
                            upgrade_buttons = build_levelup_buttons() + [Button("Boss Reward!", SCREEN_WIDTH//2-200, 220+80*3, 400, 50, PURPLE, GRAY, action=random.choice(UPGRADE_POOL)["func"])]
                            game_state = LEVEL_UP
                            boss = None
                        else:
                            enemies.remove(en)
                            gems.append(XPGem(en.rect.x,en.rect.y))
                    break

        # Orbs
        for o in orbiting_orbs:
            o.update(); o.draw(SCREEN)
            for en in enemies[:]:
                if o.rect.colliderect(en.rect):
                    en.hp-=o.damage
                    if en.hp<=0 and not isinstance(en,Boss): enemies.remove(en); gems.append(XPGem(en.rect.x,en.rect.y))

        # Explosion
        explosion_spell.update(enemies,gems,hearts); explosion_spell.draw(SCREEN)

        # Gems
        for g in gems[:]:
            g.draw(SCREEN)
            dx,dy=player.rect.centerx-g.rect.centerx,player.rect.centery-g.rect.centery; d=math.hypot(dx,dy)
            if player.magnet_radius>0 and d<=player.magnet_radius and d>0: g.rect.move_ip(int(dx/d*4),int(dy/d*4))
            if player.rect.colliderect(g.rect):
                gems.remove(g)
                leveled=player.add_xp(1)
                if leveled: upgrade_buttons=build_levelup_buttons(); game_state=LEVEL_UP

        # Hearts
        for h in hearts[:]:
            h.draw(SCREEN)
            if player.rect.colliderect(h.rect): hearts.remove(h); player.heal(1)

        # Enemies move
        for en in enemies[:]:
            if isinstance(en,Boss): en.update(player,enemies,strength)
            else: en.move_towards_player(player)
            en.draw(SCREEN)
            if player.rect.colliderect(en.rect):
                dead=player.take_damage(en.damage)
                if not isinstance(en,Boss): enemies.remove(en)
                if dead: game_state=GAME_OVER

        SCREEN.blit(SMALL.render(f"Lvl {player.level}",True,WHITE),(220,10))
        if elapsed//30+1>strength: strength+=1

    elif game_state==LEVEL_UP:
        SCREEN.blit(FONT.render("LEVEL UP! Choose:",True,WHITE),(SCREEN_WIDTH//2-150,150))
        for b in upgrade_buttons: b.draw(SCREEN)

    elif game_state==GAME_OVER:
        SCREEN.blit(FONT.render("GAME OVER",True,RED),(SCREEN_WIDTH//2-100,200))
        menu_btn.draw(SCREEN)

    pygame.display.flip()
    clock.tick(60)

pygame.quit(); sys.exit()
