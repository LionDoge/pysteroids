from ursina import *
from models.ship import ShipModel, ShipCollision

class Ship(Entity):
    def __init__(self, accel=0.2, shooting_cooldown=0.2, health=3, **kwargs):
        super().__init__(model=ShipModel(), scale=0.2, origin=(0, 0.1, 0), **kwargs)
        self.accel = accel
        self.shooting_cooldown = shooting_cooldown
        self.damage_cooldown = 3
        self.health = health
        self.velocity = Vec2(0, 0)
        self.last_shoot_time = 0.0
        self.collider = MeshCollider(self, mesh=ShipCollision())
        self.last_damage_time = 0.0

    def take_damage(self, amount: int):
        self.health -= amount
        duration = 0.6
        for i in range(3):
            self.blink(Vec4(self.color[0], self.color[1], self.color[2], 0.0), curve=curve.linear_boomerang, duration=duration, delay=i*duration)
        def set_alpha(_):
            self.alpha = 1
        invoke(set_alpha, 3 * duration + 0.1)
        
        
