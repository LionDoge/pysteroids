import math
import random
from ursina import *
import globals
globals.init()
from globals import GameState

app = Ursina(show_ursina_splash=False, vsync=False, title="Asteroidy :D")

import asteroidsconstants as ac
from entities.asteroid_ent import Asteroid
from entities.ship_ent import Ship
from entities.particlesystem import ParticleSystem
from gameui import *
from util import *

DEBUG_TEXT = True

window.color = color.black
camera.orthographic = True
camera.fov = 1

sfx_asteroid_destroy = Audio(ac.ASSET_DIR + ac.SFX_ASTEROID_DESTROY, loop=False, autoplay=False)
sfx_damaged = Audio(ac.ASSET_DIR + ac.SFX_SHIP_DAMAGED, loop=False, autoplay=False)

def get_asteroids_count():
    return len(globals.asteroids)

def spawn_asteroids_randomized(count: int, level: int):
    asteroid_speed_level_scale = 0.03
    asteroid_speed_min = 0.05
    asteroid_speed_max_base = 0.25

    for i in range(count):
        ship_pos = ship.position if ship is not None else Vec2(0, 0)
        min_distance = 0.4
        max_distance = 0.7
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(min_distance, max_distance)
        pos_x = ship_pos.x + math.cos(angle) * distance
        pos_y = ship_pos.y + math.sin(angle) * distance
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
        globals.asteroids.append(asteroid)

def damage_asteroid(asteroid: Asteroid, amount: int) -> bool:
    asteroid.health -= amount
    if asteroid.health <= 0:
        if asteroid.scale.x > ac.C_BIG_ASTEROID_LIMIT:
            spawnRangeRadius = 0.01
            spawnCount = random.randint(2, 6)
            for i in range(spawnCount): 
                angle = (float(i) / float(spawnCount)) * 2 * math.pi
                aSin = math.sin(angle)
                aCos = math.cos(angle)
                asteroid_pos = asteroid.position + Vec2(aCos * spawnRangeRadius, aSin * spawnRangeRadius)
                speed = random.uniform(0.03, 0.1 + (0.03 * current_level)) 

                new_asteroid = Asteroid(
                    scale=random.uniform(0.05, ac.C_BIG_ASTEROID_LIMIT - 0.01),
                    velocity=Vec2(aCos * speed, aSin * speed),
                    rotation_speed=random.uniform(-0.25, 0.25) * 360,
                    health=2 + (current_level - 1),
                    position=asteroid_pos
                )
                globals.asteroids.append(new_asteroid)
        return True
    return False

def next_level(level):
    spawn_asteroids_randomized(1 + level, level)

current_level = 0
score = 0
ship = None

def clear_game():
    global current_level, score, ship
    current_level = 0
    score = 0
    for b in globals.bullets:
        destroy(b)
    globals.bullets.clear()
    for a in globals.asteroids:
        a.remove()
    globals.asteroids.clear()
    if ship is not None:
        ship.clear()
        destroy(ship)

def init_game(b_clear = True):
    global ship
    if b_clear:
        clear_game()
    ship = Ship(color=color.azure, position=(0, 0), health=3)
    globals.game_state = GameState.PLAYING

game_ui = GameUI(init_game, DEBUG_TEXT)
def update():
    global current_level
    global score
    if globals.game_state == GameState.MENU:
        return
    elif globals.game_state == GameState.PAUSED:
        return
    
    if globals.game_state == GameState.LOST:
        if held_keys['r']:
            clear_game()
            game_ui.clear_lose_screen()
            game_ui.draw_menu_screen()
            globals.game_state = GameState.MENU
        return
    
    if get_asteroids_count() == 0:
        current_level += 1
        next_level(current_level)

    for bullet in globals.bullets:
        bullet.position += bullet.velocity * time.dt
        if is_out_of_bounds(bullet.position, ac.C_BULLET_SIZE):
            globals.bullets.remove(bullet)
            destroy(bullet)

    asteroids_to_destroy = list()
    for asteroid in globals.asteroids:
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
                    ship.last_damage_time = time.time()

            elif hit_info.entity in globals.bullets:
                bullet = hit_info.entity
                if bullet in globals.bullets:
                    globals.bullets.remove(bullet)
                    destroy(bullet)
                    p = ParticleSystem(num_particles=50, frames=60, thickness=5, position=asteroid.position, color=color.white, rotation_y=random.random()*360)
                    p.fade_out(duration=.2, delay=1-.2, curve=curve.linear)
                    if damage_asteroid(asteroid, ac.C_BULLET_DMG):
                        sfx_asteroid_destroy.play()
                        asteroids_to_destroy.append(asteroid)
                        score += 50 * current_level
                    
                    score += 5
    
    for asteroid in asteroids_to_destroy:
        if asteroid in globals.asteroids:
            asteroid.remove()
            globals.asteroids.remove(asteroid)

    game_ui.update_debug_text(ship.rotation_z, ship.velocity.length(), ship.position, ship.health)
    game_ui.update_score(score)
    if ship.health <= 0:
        globals.game_state = GameState.LOST
        game_ui.display_lose_screen(score)
        return

window.fullscreen = False
WindowController(gameui=game_ui)
game_ui.draw_menu_screen()
app.run()