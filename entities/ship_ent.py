from ursina import *
from models.ship import ShipModel, ShipCollision
import asteroidsconstants as ac
from util import *
import globals


class Ship(Entity):
    def __init__(self, ui_info_offset=(0,0), accel=0.2, shooting_cooldown=0.2, health=3, movement_keys=('w', 's', 'a', 'd', 'space'), **kwargs):
        super().__init__(model=ShipModel(), scale=0.2, origin=(0, 0.1, 0), **kwargs)
        self.accel = accel
        self.shooting_cooldown = shooting_cooldown
        self.damage_cooldown = 3
        self.health = health
        self.velocity = Vec2(0, 0)
        self.last_shoot_time = 0.0
        self.collider = MeshCollider(self, mesh=ShipCollision())
        self.last_damage_time = 0.0
        self.ui_hearts = [Sprite(ac.ASSET_DIR + ac.SPRITE_HEART,
                position=(-0.1 + 0.1 * i, 0.45) + ui_info_offset, scale=(0.01, 0.01), parent=camera.ui, origin=(0, 0))
                for i in range(self.health)]
        self.movement_keys = movement_keys
        self.sfx_shoot = Audio(ac.ASSET_DIR + ac.SFX_SHIP_SHOOT, loop=False, autoplay=False)
        
    def clear(self):
        for heart in self.ui_hearts:
            destroy(heart)
        self.ui_hearts.clear()
        if hasattr(self, 'debug'):
            destroy(self.debug)
    
    def shoot_bullet(self):
        bullet = Entity(model=Circle(mode='line'), color=self.color, scale=ac.C_BULLET_SIZE, position=self.position, collider='sphere')
        ent_rot_rad = -1.0 * (math.radians(self.rotation_z) - math.pi/2)
        bullet.velocity = Vec2(
            math.cos(ent_rot_rad) * 0.5,
            math.sin(ent_rot_rad) * 0.5
        )
        self.sfx_shoot.play()
        globals.bullets.append(bullet)

    def update(self):
        if globals.game_state != globals.GameState.PLAYING:
            return
        
        self.rotation_z += (held_keys[self.movement_keys[3]] - held_keys[self.movement_keys[2]]) * time.dt * 200
        self.rotation_z = self.rotation_z % 360  # keep rotation in [0, 360)

        ship_rot_rad = -1.0 * (math.radians(self.rotation_z) - math.pi/2)
        new_vel_x = self.velocity.x + self.accel * math.cos(ship_rot_rad) * (held_keys[self.movement_keys[0]] - held_keys[self.movement_keys[1]]) * time.dt
        new_vel_y = self.velocity.y + self.accel * math.sin(ship_rot_rad) * (held_keys[self.movement_keys[0]] - held_keys[self.movement_keys[1]]) * time.dt
        self.velocity = Vec2(new_vel_x, new_vel_y)
        self.position = self.position + self.velocity * time.dt
        self.position = wrap_around_position(self.position, 0.05)

        if held_keys[self.movement_keys[4]]:
            if time.time() >= self.last_shoot_time + self.shooting_cooldown:
                self.last_shoot_time = time.time()
                self.shoot_bullet()
    
    def take_damage(self, amount: int):
        self.health -= amount
        if self.health >= 0:
            self.ui_hearts[self.health].texture = ac.ASSET_DIR + ac.SPRITE_HEART_EMPTY
        duration = 0.6
        for i in range(3):
            self.blink(Vec4(self.color[0], self.color[1], self.color[2], 0.0), curve=curve.linear_boomerang, duration=duration, delay=i*duration)
        def set_alpha(_):
            self.alpha = 1
        invoke(set_alpha, 3 * duration + 0.1)
        
        
