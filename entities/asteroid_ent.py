from ursina import *
from models.asteroid import AsteroidModel

class Asteroid(Entity):
    def __init__(self, scale=0.1, velocity=Vec2(0,0), rotation_speed=0, health=1, **kwargs):
        super().__init__(model=AsteroidModel(), color=color.gray, scale=scale, collider="sphere", **kwargs)
        self.velocity = velocity
        self.rotation_speed = rotation_speed
        self.health = health
        #self.collider = SphereCollider(self, radius=scale)
    def remove(self):
        destroy(self)
        if hasattr(self, 'debug'):
            destroy(self.debug)