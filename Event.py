from Enemy import Enemy
from Message import Message
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from GameContext import GameContext

class Event:
    def __init__(self,z):
        self.z=z
        self.enabled=True

class EnemySpawn(Event):
    def __init__(self,z,x_rel,speed):
        super().__init__(z)
        self.x_rel=x_rel
        self.speed=speed

    def execute(self,context:"GameContext"):
        if self.enabled:
            #crear un nuevo Enemy en el horizonte, posicion x_rel y velocidad speed
            horizonte=context.camera.view_distance
            enemigo=Enemy(self.x_rel, horizonte+context.camera.z, self.speed, context)
            #añadir el enemigo a la lista de objetos temporales
            context.frame_data.tempobjbuffer.append(enemigo)
            self.enabled=False

class Checkpoint(Event):
    def __init__(self,z,time):
        super().__init__(z)
        self.time=time

    def execute(self,context:"GameContext"):
        if self.enabled:
            context.root.sounds["checkpoint"].play()
            context.score+=1000+int(context.timer)*100
            context.timer+=self.time
            x=context.screen.get_width() // 2
            y=int(context.screen.get_height()*0.45)
            context.root.messages.append(Message(x,y,context.root.resources.checkpoint,2.0))
            self.enabled=False
