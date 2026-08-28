class Message:
    def __init__(self,x,y,sprite,life):
        self.x=x
        self.y=y
        self.sprite=sprite
        self.life=life
        self.age=0.0
        self.dead=False

    def update(self, dt):
        self.age+=dt
        if self.age>self.life:
            self.dead=True