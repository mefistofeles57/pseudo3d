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

        self.scale = 1.0
        self.alpha = 255
        self.frame = 0
        self.numframes=0

    def update(self, dt):
        self.age += dt
        t = self.age / self.life

        if t >= 1.0:
            self.dead = True
            return

        # crecimiento + desvanecido
        self.scale = 0.75 + 1.25 * t
        self.alpha = max(0, int(255 * (1.0 - t)))
        self.frame = min(int(t * self.numframes), self.numframes - 1)


class Humo(TempObject):
    def __init__(self, x_rel, z,metadata,flip=False):
        if flip:
            img="humo.flip"
        else:
            img="humo"
        super().__init__(x_rel, z, img)
        self.drift_x = 0.0      # un pelín hacia fuera si quieres
        self.life = 0.35
        self.numframes=metadata.frames

    def update(self, dt):
        super().update(dt)
        if self.dead:
            return

        self.x_rel += self.drift_x * dt
