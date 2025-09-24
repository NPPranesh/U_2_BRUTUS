from ursina import *
import random

app = Ursina()

# -----------------------------
# Player
# -----------------------------
player = Entity(model='cube', color=color.red, scale=(1,1,1), position=(0,0,0), collider='box')

# Ground
ground = Entity(model='plane', scale=(50,1,50), color=color.gray, collider='box')

# Camera
camera.parent = player
camera.position = (0, 10, -20)
camera.rotation_x = 20

# -----------------------------
# Stats
# -----------------------------
score = 0
score_text = Text(text=f"Score: {score}", position=(-0.85,0.45), scale=2)

# Player health bar
max_health = 100
current_health = max_health
health_bar_bg = Entity(model='quad', color=color.dark_gray, scale=(0.32,0.04), position=(-0.7,0.42))
health_bar = Entity(model='quad', color=color.green, scale=(0.3,0.03), position=(-0.7,0.42))

# -----------------------------
# Movement
# -----------------------------
speed = 5
jump_power = 8
gravity = -0.3
y_velocity = 0
is_jumping = False

# -----------------------------
# Bullets
# -----------------------------
bullets = []
enemy_bullets = []

# -----------------------------
# Enemy settings
# -----------------------------
wave_number = 1
enemy_speed = 2.5
enemies = []
evil_colors = [color.rgb(50,0,0), color.rgb(0,0,50), color.rgb(20,0,20), color.rgb(0,50,0), color.rgb(50,0,50)]

# -----------------------------
# Power-ups
# -----------------------------
powerups = []
shield_active = False
shield_timer = 0

# -----------------------------
# Functions
# -----------------------------
def spawn_enemies(number, boss=False):
    global enemies
    enemies = []
    for _ in range(number):
        if boss:
            e = Entity(model='cube', color=color.rgb(80,0,80), scale=(2,2,2),
                       position=(random.randint(-15,15),0,random.randint(-15,15)), collider='box')
            e.health = 100 + wave_number*20
            e.shoot_interval = 0.5
            e.health_bar_bg = Entity(parent=e, model='quad', color=color.dark_gray, scale=(2.2,0.2), y=1.5, z=0)
            e.health_bar = Entity(parent=e, model='quad', color=color.red, scale=(2,0.15), y=1.5, z=0)
        else:
            e = Entity(model='cube', color=random.choice(evil_colors), scale=(1,1,1),
                       position=(random.randint(-15,15),0,random.randint(-15,15)), collider='box')
            e.health = 20
            e.shoot_interval = random.uniform(1,2)
        e.direction = Vec3(random.choice([-1,1]),0,random.choice([-1,1]))
        enemies.append(e)

spawn_enemies(wave_number + 4)

# -----------------------------
# Player autoshoot
# -----------------------------
fire_rate = 0.3
def shoot():
    bullet = Entity(model='sphere', color=color.yellow, scale=0.2,
                    position=player.position + Vec3(0,0.5,0))
    bullet.direction = Vec3(camera.forward.x,0,camera.forward.z).normalized()
    bullets.append(bullet)


def invoke_interval(shoot, fire_rate, ignore_paused):
    pass


invoke_interval(shoot, fire_rate, ignore_paused=True)

# -----------------------------
# Enemy shooting
# -----------------------------
def enemy_shoot(enemy):
    bullet = Entity(model='sphere', color=color.orange, scale=0.2, position=enemy.position + Vec3(0,0.5,0))
    bullet.direction = (player.position - enemy.position).normalized()
    enemy_bullets.append(bullet)
    invoke(enemy_shoot, enemy, delay=enemy.shoot_interval)

for e in enemies:
    enemy_shoot(e)

# -----------------------------
# Spawn power-up
# -----------------------------
def spawn_powerup():
    type = random.choice(['health','firerate','shield'])
    color_map = {'health':color.green,'firerate':color.cyan,'shield':color.gold}
    pu = Entity(model='sphere', color=color_map[type], scale=0.5,
                position=(random.randint(-20,20),0,random.randint(-20,20)))
    pu.type = type
    # Floating text above power-up
    pu.text = Text(text=type.capitalize(), scale=1, color=color.white, origin=(0,0), position=(pu.x,1,pu.z))
    powerups.append(pu)
    invoke(spawn_powerup, delay=random.randint(10,15))

spawn_powerup()

# -----------------------------
# Game update
# -----------------------------
def update():
    global y_velocity, is_jumping, score, current_health, wave_number, enemy_speed, fire_rate, shield_active, shield_timer

    # Player movement
    forward = camera.forward
    right = camera.right
    forward.y = 0
    right.y = 0
    forward = forward.normalized()
    right = right.normalized()
    if held_keys['w']: player.position += forward * time.dt * speed
    if held_keys['s']: player.position -= forward * time.dt * speed
    if held_keys['a']: player.position -= right * time.dt * speed
    if held_keys['d']: player.position += right * time.dt * speed

    # Jump + gravity
    if is_jumping:
        player.y += y_velocity * time.dt
        y_velocity += gravity
        if player.y <= 0:
            player.y = 0
            is_jumping = False
            y_velocity = 0

    # Enemy movement
    for enemy in enemies:
        enemy.position += enemy.direction * time.dt * enemy_speed
        if abs(enemy.x) > 25: enemy.direction.x *= -1
        if abs(enemy.z) > 25: enemy.direction.z *= -1
        if hasattr(enemy, 'health_bar'):
            enemy.health_bar.scale_x = 2 * (enemy.health / max(enemy.health,20))

    # Player bullets
    for bullet in bullets[:]:
        bullet.position += bullet.direction * time.dt * 20
        for enemy in enemies:
            if bullet.intersects(enemy).hit:
                enemy.health -= 20
                destroy(bullet)
                bullets.remove(bullet)
                if enemy.health <= 0:
                    enemy.position = Vec3(random.randint(-15,15),0,random.randint(-15,15))
                    enemy.direction = Vec3(random.choice([-1,1]),0,random.choice([-1,1]))
                    enemy.color = random.choice(evil_colors)
                    score += 1
                    score_text.text = f"Score: {score}"
                    if hasattr(enemy, 'health_bar'): enemy.health = 20
                break
        if abs(bullet.x) > 50 or abs(bullet.z) > 50:
            if bullet in bullets: destroy(bullet); bullets.remove(bullet)

    # Enemy bullets
    for bullet in enemy_bullets[:]:
        bullet.position += bullet.direction * time.dt * 15
        if distance(player.position, bullet.position) < 0.5:
            if not shield_active:
                current_health -= 10
                health_bar.scale_x = 0.3 * (current_health / max_health)
                if current_health <= 0: game_over_screen()
            destroy(bullet)
            enemy_bullets.remove(bullet)
        elif abs(bullet.x) > 50 or abs(bullet.z) > 50:
            destroy(bullet)
            enemy_bullets.remove(bullet)

    # Power-up collection
    for pu in powerups[:]:
        if distance(player.position, pu.position) < 1:
            if pu.type == 'health':
                current_health = min(max_health, current_health + 30)
                health_bar.scale_x = 0.3 * (current_health / max_health)
            elif pu.type == 'firerate':
                fire_rate = max(0.1, fire_rate - 0.1)
            elif pu.type == 'shield':
                shield_active = True
                shield_timer = 5
            destroy(pu)
            powerups.remove(pu)

    # Shield timer
    if shield_active:
        shield_timer -= time.dt
        if shield_timer <= 0: shield_active = False

    # Next wave logic
    if score >= wave_number * 5:
        wave_number += 1
        enemy_speed += 0.5
        if wave_number % 5 == 0:
            spawn_enemies(1, boss=True)
        else:
            spawn_enemies(wave_number + 4)
        for e in enemies: enemy_shoot(e)

# -----------------------------
# Player input
# -----------------------------
def input(key):
    global is_jumping, y_velocity
    if key == 'space' and not is_jumping:
        is_jumping = True
        y_velocity = jump_power

# -----------------------------
# Game over
# -----------------------------
def game_over_screen():
    Text(text="GAME OVER", scale=3, color=color.red, origin=(0,0))
    Text(text=f"Final Score: {score}", scale=2, color=color.black, origin=(0,0), position=(0,-0.1))
    application.pause()

# Run
app.run()