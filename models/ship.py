from ursina import *

class ShipModel(Mesh):
    def __init__(self, mode='line', **kwargs):
        self.vertices = [
            Vec3(-0.1, 0, 0),
            Vec3(0, 0.05, 0),
            Vec3(0.1, 0, 0),
            Vec3(0, 0.25, 0),
        ]
            
        if mode == 'line':
            self.vertices.append(self.vertices[0])

        super().__init__(vertices=self.vertices, mode=mode, thickness=2, **kwargs)

class ShipCollision(Mesh):
    def __init__(self, **kwargs):
        self.vertices = [
            Vec3(-0.1, 0, 0),
            Vec3(0, 0.25, 0),
            Vec3(0.1, 0, 0),
        ]
        super().__init__(vertices=self.vertices, **kwargs)