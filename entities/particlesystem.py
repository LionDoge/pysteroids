from ursina import *
import numpy as np

class ParticleSystem(Entity):
    def __init__(self, num_particles, frames, **kwargs):
        self.points = np.array([Vec3(0,0,0) for i in range(num_particles)])
        self.directions = np.array([Vec3(0,0,0) for i in range(num_particles)])
        for i in range(num_particles):
            angle = (i/num_particles) * 2 * np.pi
            speed = np.random.uniform(0.01, 0.05) * (1/frames) * 4
            self.directions[i] = Vec3(np.cos(angle) * speed, np.sin(angle) * speed, 0)
        self.frames = []
        for i in range(frames):
            self.points += self.directions
            self.frames.append(copy(self.points))

        super().__init__(model=Mesh(vertices=self.points, mode='point', static=False, render_points_in_3d=False, thickness=5), t=0, duration=1, **kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)


    def update(self):
        self.t += time.dt
        if self.t >= self.duration:
            destroy(self)
            return

        self.model.vertices = self.frames[floor(self.t * 60)]
        self.model.generate()