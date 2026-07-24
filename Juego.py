import pygame
import math
from GameContext import GameContext
from Point import *

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

        #fondo
        self.bg_color=(0,0,230)
        self.font = pygame.font.Font(None, 36)
        #objetos de juego

        self.context=GameContext(self.screen)



        #self.fondo=self.create_vertical_gradient(self.width,self.height,(40, 120, 255),(180, 235, 255))


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self,dt):
        self.context.camera.update(dt,self.context)
        if len(self.context.camera.buffer)>0:
            self.bg_color=self.context.camera.buffer[-1].visualProfile.bgcolor

    def draw(self):
        self.screen.fill(self.bg_color)

        #self.screen.blit(self.fondo, (0, 0))

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
