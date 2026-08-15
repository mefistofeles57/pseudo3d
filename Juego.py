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

        self.context=GameContext(self.screen,self)

        # situar el coche en la carretera y la camara detrás

        self.context.player.x=0.0
        self.context.player.y=0.0
        self.context.player.z=self.context.camera.player_z
        self.debug_text=""


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self,dt):
        self.context.camera.update(dt)

    def draw(self):

        self.context.camera.draw(self.screen)

        txt="speed: "+str(round(self.context.player.speed*20,2))+ \
            " acel: "+str(round(self.context.player.p_acelerador,2))+ \
            " freno: "+str(round(self.context.player.p_freno,2))+ \
            " volante: "+str(round(self.context.player.volante,2))+ \
            " marcha: "+str(self.context.player.marcha)
        texto = self.font.render(
        txt,
        True,              # antialiasing
        (255, 255, 255)    # color blanco
        )

        self.screen.blit(texto, (10, 10))
        txt="FPS: "+str(round(self.clock.get_fps(),2))+ \
            " debug: "+self.debug_text
        texto = self.font.render(
        txt,
        True,              # antialiasing
        (255, 255, 255)    # color blanco
        )

        self.screen.blit(texto, (10, 35))

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
