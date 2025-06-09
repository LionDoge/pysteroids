from ursina import *
import random

class Asteroid(Mesh):
    def __init__(self, resolution=16, radius=.5, mode='line', **kwargs):
        origin = Entity()
        point = Entity(parent=origin)
        point.y = radius

        self.vertices = list()
        for i in range(resolution):
            origin.rotation_z -= 360 / resolution
            origin.scale = random.uniform(0.8, 1.2)
            self.vertices.append(point.world_position)
            

        if mode == 'line':  # add the first point to make the circle whole
            self.vertices.append(self.vertices[0])

        destroy(origin)
        super().__init__(vertices=self.vertices, mode=mode, **kwargs)