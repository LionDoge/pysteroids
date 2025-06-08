from ursina import *
import math

app = Ursina()
window.color = color.black
camera.orthographic = True
camera.fov = 1

#score_text = Text(text=f"Test text!", position=(0, .45), scale=2, origin=(0, 0))

ship = Entity(model=Cone(4, 0.1, 0.3), color=color.azure,
               scale=(.2, .2), position=(0, 0), origin=(0, 0.1, 0))

ship.accel = 0.2
ship.velocity = Vec2(0, 0)
info_text = Text(text=f"rot {ship.rotation.z}", position=(0, .4), scale=1, origin=(0, 0))
# ball = Entity(model='circle', color=color.red, scale=.1, position=(0, 0))
# ball.velocity = Vec2(0.1, 0)

def wrap_around_position(pos, pad):
    x = pos.x * (1 / window.aspect_ratio)
    y = pos.y

    pad_x = pad * (1/window.aspect_ratio)

    if x < -0.5 - pad_x:
        pos.x = (0.5 * window.aspect_ratio) + pad_x
    elif x > 0.5 + pad_x:
        pos.x = (-0.5 * window.aspect_ratio) - pad_x

    if y < -0.5 - pad:
        pos.y = 0.5 + pad
    elif y > 0.5 + pad:
        pos.y = -0.5 - pad
    return pos

def update_text(rot, speed, pos):
    info_text.text = f"rot {rot:.2f} speed {speed:.2f} pos {pos.x:.2f}, {pos.y:.2f}"

def update():
    ship.rotation_z += (held_keys['d'] - held_keys['a']) * time.dt * 200
    ship.rotation_z = ship.rotation_z % 360  # keep rotation in [0, 360)

    ship_rot_rad = -1.0 * (math.radians(ship.rotation_z) - math.pi/2)
    new_vel_x = ship.velocity.x + ship.accel * math.cos(ship_rot_rad) * time.dt * (held_keys['w'] - held_keys['s'])
    new_vel_y = ship.velocity.y + ship.accel * math.sin(ship_rot_rad) * time.dt * (held_keys['w'] - held_keys['s'])
    ship.velocity = Vec2(new_vel_x, new_vel_y)
    ship.position = ship.position + ship.velocity * time.dt
    ship.position = wrap_around_position(ship.position, 0.05)
    update_text(ship.rotation_z, ship.velocity.length(), ship.position)


app.run()