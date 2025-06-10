from ursina import *
from ursina.shaders.screenspace_shaders import pixelation_shader
import math
import random
from entities.asteroid_ent import Asteroid
from entities.ship_ent import Ship
from entities.particlesystem import ParticleSystem
import asteroidsconstants as ac
from enum import Enum
from gameui import *

DEBUG_TEXT = True
app = Ursina(show_ursina_splash=False)
window.color = color.black
camera.orthographic = True
camera.fov = 1

bullet_speed = 0.3
bullet_size = 0.01
bullet_dmg = 1
bigAsteroidLimit = 0.08 # minimum size of a big asteroid for it to be able to split into smaller ones.

sfx_shoot = Audio(ac.ASSET_DIR + ac.SFX_SHIP_SHOOT, loop=False, autoplay=False)
sfx_asteroid_destroy = Audio(ac.ASSET_DIR + ac.SFX_ASTEROID_DESTROY, loop=False, autoplay=False)
sfx_damaged = Audio(ac.ASSET_DIR + ac.SFX_SHIP_DAMAGED, loop=False, autoplay=False)
def wrap_around_position(pos, pad):
    x = pos.x * (1 / window.aspect_ratio)
    y = pos.y

    pad_x = pad * (1 / window.aspect_ratio)

    if x < -0.5 - pad_x:
        pos.x = (0.5 * window.aspect_ratio) + pad_x
    elif x > 0.5 + pad_x:
        pos.x = (-0.5 * window.aspect_ratio) - pad_x

    if y < -0.5 - pad:
        pos.y = 0.5 + pad
    elif y > 0.5 + pad:
        pos.y = -0.5 - pad
    return pos

def is_out_of_bounds(pos, pad):
    x = pos.x * (1 / window.aspect_ratio)
    y = pos.y

    pad_x = pad * (1 / window.aspect_ratio)

    if x < -0.5 - pad_x or x > 0.5 + pad_x or y < -0.5 - pad or y > 0.5 + pad:
        return True
    return False

if DEBUG_TEXT:
    global info_text
    info_text = Text(position=(0, .4), scale=1, origin=(0, 0))

def update_text(rot, speed, pos, health):
    if not DEBUG_TEXT:
        return
    info_text.text = f"score {score} rot {rot:.2f} speed {speed:.2f} pos {pos.x:.2f}, {pos.y:.2f} hp {health}"

bullets = []
asteroids = []
def get_asteroids_count():
    return len(asteroids)

def shoot_bullet(from_entity: Entity):
    bullet = Entity(model=Circle(mode='line'), color=from_entity.color, scale=bullet_size, position=from_entity.position, collider='sphere')
    ent_rot_rad = -1.0 * (math.radians(ship.rotation_z) - math.pi/2)
    bullet.velocity = Vec2(
        math.cos(ent_rot_rad) * 0.5,
        math.sin(ent_rot_rad) * 0.5
    )
    bullets.append(bullet)
    sfx_shoot.play()

def spawn_asteroids_randomized(count: int, level: int):
    asteroid_speed_level_scale = 0.03
    asteroid_speed_min = 0.05
    asteroid_speed_max_base = 0.25

    for i in range(count):
        # TODO: aspect ratio aware position
        pos_x = random.uniform(-0.3, 0.3)
        pos_y = random.uniform(-0.3, 0.3)
        #angle = (i / max(count-1, 1)) * offset * math.pi * 2
        position = Vec2(
            pos_x,
            pos_y,
        )

        # randomize speed and direction
        speed = max(random.random() * asteroid_speed_max_base, asteroid_speed_min) + (asteroid_speed_level_scale * level)
        velocity_angle = random.random() * 2 * math.pi
        velocity = Vec2(
            math.cos(velocity_angle) * speed,
            math.sin(velocity_angle) * speed
        )

        # randomize scale
        asteroid_scale_limit_upper = 0.25
        asteroid_scale_limit_lower = 0.1 # maximum size of the low bound of size
        asteroid_scale_per_level = 0.05
        scale_upper = min(0.08 + (asteroid_scale_per_level * level), asteroid_scale_limit_upper)
        scale_lower = min(0.01 + (asteroid_scale_per_level * level), asteroid_scale_limit_lower)
        scale = random.uniform(scale_lower, scale_upper)
        # randomize rotation speed
        rot_speed = random.uniform(-0.25, 0.25) * 360
        # level based health
        health = 1 + (2 * level)

        asteroid = Asteroid(
            scale=scale,
            velocity=velocity,
            rotation_speed=rot_speed,
            health=health,
            position=position
        )
        asteroids.append(asteroid)

def damage_asteroid(asteroid: Asteroid, amount: int) -> bool:
    asteroid.health -= amount
    if asteroid.health <= 0:
        if asteroid.scale.x > bigAsteroidLimit:
            spawnRangeRadius = 0.01
            spawnCount = random.randint(2, 6)
            for i in range(spawnCount): 
                angle = (float(i) / float(spawnCount)) * 2 * math.pi
                aSin = math.sin(angle)
                aCos = math.cos(angle)
                asteroid_pos = asteroid.position + Vec2(aCos * spawnRangeRadius, aSin * spawnRangeRadius)
                speed = random.uniform(0.03, 0.1 + (0.03 * current_level)) 

                new_asteroid = Asteroid(
                    scale=random.uniform(0.05, bigAsteroidLimit - 0.01),
                    velocity=Vec2(aCos * speed, aSin * speed),
                    rotation_speed=random.uniform(-0.25, 0.25) * 360,
                    health=2 + (current_level - 1),
                    position=asteroid_pos
                )
                asteroids.append(new_asteroid)
        return True
    return False

def next_level(level):
    spawn_asteroids_randomized(1 + level, level)

class GameState(Enum):
    PLAYING = 1
    LOST = 2
    MENU = 3

current_level = 0
score = 0
ship = None
game_state = GameState.MENU
def init_game():
    global current_level, score, ship, game_state
    current_level = 0
    score = 0
    for b in bullets:
        destroy(b)
    bullets.clear()
    for a in asteroids:
        a.remove()
    asteroids.clear()
    if ship is not None:
        ship.clear()
        destroy(ship)
    ship = Ship(color=color.azure, position=(0, 0), health=1)
    game_state = GameState.PLAYING

game_ui = GameUI(init_game)

def update():
    global current_level
    global score
    global game_state
    if game_state == GameState.MENU:
        return
    if game_state == GameState.LOST:
        if held_keys['r']:
            init_game()
            game_ui.clear_lose_screen()
        return
    
    if get_asteroids_count() == 0:
        current_level += 1
        next_level(current_level)

    ship.rotation_z += (held_keys['d'] - held_keys['a']) * time.dt * 200
    ship.rotation_z = ship.rotation_z % 360  # keep rotation in [0, 360)

    ship_rot_rad = -1.0 * (math.radians(ship.rotation_z) - math.pi/2)
    new_vel_x = ship.velocity.x + ship.accel * math.cos(ship_rot_rad) * time.dt * (held_keys['w'] - held_keys['s'])
    new_vel_y = ship.velocity.y + ship.accel * math.sin(ship_rot_rad) * time.dt * (held_keys['w'] - held_keys['s'])
    ship.velocity = Vec2(new_vel_x, new_vel_y)
    ship.position = ship.position + ship.velocity * time.dt
    ship.position = wrap_around_position(ship.position, 0.05)
    update_text(ship.rotation_z, ship.velocity.length(), ship.position, ship.health)

    if held_keys['space']:
        if time.time() >= ship.last_shoot_time + ship.shooting_cooldown:
            ship.last_shoot_time = time.time()
            shoot_bullet(ship)
    
    for bullet in bullets:
        bullet.position += bullet.velocity * time.dt
        if is_out_of_bounds(bullet.position, bullet_size):
            bullets.remove(bullet)
            destroy(bullet)

    #alive_asteroids = [a for a in asteroids if a.health > 0]
    asteroids_to_destroy = list()
    for asteroid in asteroids:
    
        asteroid.position += asteroid.velocity * time.dt
        asteroid.position = wrap_around_position(asteroid.position, 0.05)
        asteroid.rotation_z += asteroid.rotation_speed * time.dt
        asteroid.rotation_z = asteroid.rotation_z % 360

        if DEBUG_TEXT:
            if not hasattr(asteroid, 'debug'):
                asteroid.debug = Text(position=(0, 0), scale=0.5, origin=(0, 0))
            asteroid.debug.text = f"scale {asteroid.scale.x:.2f} | vel {asteroid.velocity.x:.2f}, {asteroid.velocity.y:.2f} | health {asteroid.health}"
            asteroid.debug.position = Vec2(asteroid.position.x, asteroid.position.y + 0.05)

        hit_info = asteroid.intersects()
        if hit_info.hit:
            if hit_info.entity == ship:
                if time.time() >= ship.last_damage_time + ship.damage_cooldown:
                    ship.take_damage(1)
                    sfx_damaged.play()
                    print(f"Ship hit by asteroid! Health: {ship.health}")
                    ship.last_damage_time = time.time()
            elif hit_info.entity in bullets:
                bullet = hit_info.entity
                if bullet in bullets:
                    bullets.remove(bullet)
                    destroy(bullet)
                    p = ParticleSystem(num_particles=50, frames=60, thickness=5, position=asteroid.position, color=color.white, rotation_y=random.random()*360)
                    p.fade_out(duration=.2, delay=1-.2, curve=curve.linear)
                    if damage_asteroid(asteroid, bullet_dmg):
                        sfx_asteroid_destroy.play()
                        asteroids_to_destroy.append(asteroid)
                        score += 50 * current_level
                    
                    score += 5
    
    for asteroid in asteroids_to_destroy:
        if asteroid in asteroids:
            asteroids.remove(asteroid)
            asteroid.remove()
            #print(f"Asteroid destroyed! Remaining: {get_asteroids_count()}")
    
    if ship.health <= 0:
        game_state = GameState.LOST
        game_ui.display_lose_screen(score)
        return

window.fullscreen = False
WindowController()
game_ui.draw_menu_screen()
app.run()