from ursina import *
from models.ship import ShipModel, ShipCollision
import asteroidsconstants as ac

class Ship(Entity):
    def __init__(self, ui_info_offset=(0,0), accel=0.2, shooting_cooldown=0.2, health=3, **kwargs):
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
        
        
