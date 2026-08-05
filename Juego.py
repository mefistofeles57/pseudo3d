import pygame
import math
from GameContext import GameContext
from Point import Point

class Juego:
    def __init__(self, width=1280, height=720, title="Outrun prototype",fps=60):
        pygame.init()
        pygame.display.set_caption(title)

        self.width=width
        self.height=height
        self.fps=fps

        self.screen=pygame.display.set_mode((self.width,self.height))



        self.clock=pygame.time.Clock()
        self.running=True

        self.font = pygame.font.Font(None, 36)
        #objetos de juego

        self.context=GameContext(self.screen)

        # situar el coche en la carretera y la camara detrás

        self.context.player.x=0.0
        self.context.player.y=0.0
        self.context.player.z=self.context.camera.player_z


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self,dt):
        self.context.camera.update(dt)

    def draw(self):

        self.context.camera.draw(self.screen)

        txt="altura: "+str(self.context.camera.height)+" : "+ \
        "pitch: "+str(self.context.camera.pitch)+" : "+ \
        "fov: "+str(round(self.context.camera.fov))+" : "+ \
        "distance: "+str(self.context.camera.view_distance)+" : "+ \
        "horizon: "+str(self.context.camera.horizon)
        texto = self.font.render(
        txt,
        True,              # antialiasing
        (255, 255, 255)    # color blanco
        )

        self.screen.blit(texto, (10, 10))

        pygame.display.flip()



    def run(self):

        while self.running:
            dt=self.clock.tick(self.fps)/1000.0

            self.handle_events()
            self.context.keys=pygame.key.get_pressed()

            self.update(dt)
            self.draw()

        pygame.quit()



if __name__ == "__main__":

    j=Juego()
    j.run()
