from Object import Object

class TempObject(Object):
    def __init__(self, x_rel, z, sprite_frames):
        super().__init__()
        self.x_rel=x_rel
        self.z=z

        self.img = sprite_frames
        self.age = 0.0
        self.life = 0.45
        self.dead = False

        self.frame = 0
        self.numframes=0

    def update(self, dt):
        self.age += dt
        t = self.age / self.life

        if t >= 1.0:
            self.dead = True
            return

        self.frame = min(int(t * self.numframes), self.numframes - 1)


class Humo(TempObject):
    def __init__(self, x_rel, z, speed, vx, metadata,flip=False):
        if flip:
            img="humo.flip"
        else:
            img="humo"
        super().__init__(x_rel, z, img)
        self.life = 0.35
        self.numframes=metadata.frames
        self.collidable=False
        self.metadata=metadata
        self.speed=speed
        self.vx=vx

    def update(self, dt):
        if not self.dead:
            super().update(dt)

            self.z += self.speed * dt
            self.x_rel += self.vx * dt

            self.speed *= 0.98 ** (dt * 60.0)
            self.vx    *= 0.95 ** (dt * 60.0)