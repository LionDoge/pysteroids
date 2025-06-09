from ursina import *
import math
from asteroids import Asteroid
import random

app = Ursina()
window.color = color.black
camera.orthographic = True
camera.fov = 1

current_level = 0
bullet_speed = 0.3
bullet_size = 0.01
bullet_dmg = 0.1
score = 0
bigAsteroidLimit = 0.07 # minimum size of a big asteroid for it to be able to split into smaller ones.

ship = Entity(model=Cone(4, 0.1, 0.3), color=color.azure,
               scale=(.2, .2), position=(0, 0), origin=(0, 0.1, 0))

ship.accel = 0.2
ship.velocity = Vec2(0, 0)
ship.shooting_cooldown = 0.2
ship.last_shoot_time = 0.0
info_text = Text(text=f"rot {ship.rotation.z}", position=(0, .4), scale=1, origin=(0, 0))
# ball = Entity(model='circle', color=color.red, scale=.1, position=(0, 0))
# ball.velocity = Vec2(0.1, 0)

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

def update_text(rot, speed, pos):
    info_text.text = f"score {score} rot {rot:.2f} speed {speed:.2f} pos {pos.x:.2f}, {pos.y:.2f}"

bullets = []
asteroids = []
def get_asteroids_count():
    return len(asteroids)

def shoot_bullet(from_entity: Entity):
    bullet = Entity(model='circle', color=color.white, scale=bullet_size, position=from_entity.position)
    ent_rot_rad = -1.0 * (math.radians(ship.rotation_z) - math.pi/2)
    bullet.velocity = Vec2(
        math.cos(ent_rot_rad) * 0.5,
        math.sin(ent_rot_rad) * 0.5
    )
    bullets.append(bullet)

asteroid_debug = True
def spawn_asteroids_randomized(count: int, level: int):
    asteroid_speed_level_scale = 0.05
    asteroid_speed_min = 0.05
    asteroid_speed_max_base = 0.3

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
        health = 5 + (2 * level)

        asteroid = Asteroid(
            scale=scale,
            velocity=velocity,
            rotation_speed=rot_speed,
            health=health,
            position=position
        )
        asteroids.append(asteroid)

def destroy_asteroid(asteroid: Entity):
    asteroids.remove(asteroid)
    destroy(asteroid)
    

def next_level(level):
    spawn_asteroids_randomized(1 + level, level)

def update():
    global current_level
    global score
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
    update_text(ship.rotation_z, ship.velocity.length(), ship.position)

    if held_keys['space']:
        if time.time() >= ship.last_shoot_time + ship.shooting_cooldown:
            ship.last_shoot_time = time.time()
            shoot_bullet(ship)
    
    for bullet in bullets:
        bullet.position += bullet.velocity * time.dt
        if is_out_of_bounds(bullet.position, bullet_size):
            bullets.remove(bullet)
            destroy(bullet)

    for asteroid in asteroids:
        if asteroid_debug:
            if not hasattr(asteroid, 'debug'):
                asteroid.debug = Text(position=(0, 0), scale=0.5, origin=(0, 0))
            asteroid.debug.text = f"scale {asteroid.scale.x:.2f} | vel {asteroid.velocity.x:.2f}, {asteroid.velocity.y:.2f} | health {asteroid.health}"
            asteroid.debug.position = Vec2(asteroid.position.x, asteroid.position.y + 0.05)

        asteroid.position += asteroid.velocity * time.dt
        asteroid.position = wrap_around_position(asteroid.position, 0.05)
        asteroid.rotation_z += asteroid.rotation_speed * time.dt
        asteroid.rotation_z = asteroid.rotation_z % 360
        if asteroid.health <= 0:
            destroy_asteroid(asteroid)
    

app.run()