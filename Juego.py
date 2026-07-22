
import pygame
import math
#from Camera import Camera
#from Road import Road
from MapGenerator import MapGenerator
from Road import Line

class Player():
    def __init__(self):
        self.speed=5.0


class Juego:
    def __init__(self, width=1280, height=720, title="Outrun prototype",fps=60):
        from Camera import Camera
        from Road import Road
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

        self.road=Road()
        self.camera=Camera(self.screen,self.road)
        self.createMap(self.road)
        self.player=Player()

        self.keys=None

        #self.fondo=self.create_vertical_gradient(self.width,self.height,(40, 120, 255),(180, 235, 255))


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self,dt):
        self.camera.update(dt,self)
        if len(self.camera.buffer)>0:
            self.bg_color=self.camera.buffer[-1].visualProfile.bgcolor

    def draw(self):
        self.screen.fill(self.bg_color)

        #self.screen.blit(self.fondo, (0, 0))

        self.camera.draw(self.screen)

        txt="altura: "+str(j.camera.height)+" : "+ \
        "pitch: "+str(j.camera.pitch)+" : "+ \
        "fov: "+str(round(j.camera.fov))+" : "+ \
        "distance: "+str(j.camera.view_distance)+" : "+ \
        "horizon: "+str(j.camera.horizon)
        texto = self.font.render(
        txt,
        True,              # antialiasing
        (255, 255, 255)    # color blanco
        )

        self.screen.blit(texto, (10, 10))

        pygame.display.flip()

    def createMap(self,road):
        from Escenario import Escenario
        from Road import Road
        objects=[]
        MapGenerator.setProfile(Escenario(self.camera.LUTh,self.camera.LUTm,self.camera.LUTl))
        for i in range(5):
            #recta
            road.add(MapGenerator.pattern(MapGenerator.NONE,0.0,0,10,0))

            #colina
            road.add(MapGenerator.pattern(MapGenerator.HILL,-0.1,10,0,10))
            objects=MapGenerator.objects(objects,road.segments[-10:],"farola",2.0,0.6,1.0)
            objects=MapGenerator.objects(objects,road.segments[-10:],"farola.flip",2.0,0.6,-1.0)
            #carteles de curva lado derecho
            #recta
            road.add(MapGenerator.pattern(MapGenerator.NONE,0.0,0,10,0))
            objects=MapGenerator.objects(objects,road.segments[-10:],"arbol",2.5,0.6,1.0)
            objects=MapGenerator.objects(objects,road.segments[-10:],"arbol",2.5,0.6,-1.0)
            #curva izq
            road.add(MapGenerator.pattern(MapGenerator.CURVE,-0.5,50,0,50))
            #map,count,image,step,offset,x
            objects=MapGenerator.objects(objects,road.segments[-80:-70],"signal.arrow.flip",2.5,0.5,1.0)
            objects=MapGenerator.objects(objects,road.segments[-80:-70],"signal.arrow.flip",2.5,0.5,-1.0)
            #recta
            road.add(MapGenerator.pattern(MapGenerator.NONE,0.0,0,20,0))
            objects=MapGenerator.objects(objects,road.segments[-20:],"arbol",2.5,0.6,1.0)
            objects=MapGenerator.objects(objects,road.segments[-20:],"arbol",2.5,0.6,-1.0)
            #bajada
            road.add(MapGenerator.pattern(MapGenerator.HILL,0.1,10,0,10))
            objects=MapGenerator.objects(objects,road.segments[-10:],"farola",2.0,0.6,1.0)
            objects=MapGenerator.objects(objects,road.segments[-10:],"farola.flip",2.0,0.6,-1.0)
            #recta
            road.add(MapGenerator.pattern(MapGenerator.NONE,0.0,0,20,0))
            objects=MapGenerator.objects(objects,road.segments[-20:],"arbol",2.5,0.6,1.0)
            objects=MapGenerator.objects(objects,road.segments[-20:],"arbol",2.5,0.6,-1.0)
            #curva der
            road.add(MapGenerator.pattern(MapGenerator.CURVE,0.5,50,0,50))
            #map,count,image,step,offset,x
            objects=MapGenerator.objects(objects,road.segments[-80:-70],"signal.arrow",2.5,0.5,1.0)
            objects=MapGenerator.objects(objects,road.segments[-80:-70],"signal.arrow",2.5,0.5,-1.0)
            #arbustos
            objects=MapGenerator.objects(objects,road.segments[-390:],"arbusto",1.0,0.4,-1.5,0.3,0.3)
            objects=MapGenerator.objects(objects,road.segments[-390:],"arbusto",1.0,0.4,1.5,0.3,0.3)
            objects=MapGenerator.objects(objects,road.segments[-390:],"arbusto.flip",1.0,0.4,-2.0,0.3,0.3)
            objects=MapGenerator.objects(objects,road.segments[-390:],"arbusto.flip",1.0,0.4,2.0,0.3,0.3)
            objects=MapGenerator.objects(objects,road.segments[-390:],"arbusto",1.0,0.4,-2.5,0.3,0.3)
            objects=MapGenerator.objects(objects,road.segments[-390:],"arbusto",1.0,0.4,2.5,0.3,0.3)
            objects=MapGenerator.objects(objects,road.segments[-390:],"arbusto.flip",1.0,0.4,-3.0,0.3,0.3)
            objects=MapGenerator.objects(objects,road.segments[-390:],"arbusto.flip",1.0,0.4,3.0,0.3,0.3)
            objects=MapGenerator.objects(objects,road.segments[-390:],"arbusto",1.0,0.4,-3.5,0.3,0.3)
            objects=MapGenerator.objects(objects,road.segments[-390:],"arbusto",1.0,0.4,3.5,0.3,0.3)
            objects=MapGenerator.objects(objects,road.segments[-390:],"arbusto",1.0,0.4,-4.0,0.3,0.3)
            objects=MapGenerator.objects(objects,road.segments[-390:],"arbusto",1.0,0.4,4.0,0.3,0.3)
            objects=MapGenerator.objects(objects,road.segments[-390:],"piedra",10.0,0.3,-1.5,0.3,0.3)
            objects=MapGenerator.objects(objects,road.segments[-390:],"piedra.flip",10.0,0.3,1.5,0.3,0.3)

        ##position,x,width,offset,freq,color
        l=Line(0.3,-0.0025,0.005,0,2,[(255,255,255),None])
        road.addLine(l,0,road.segments[-1].index)
        l=Line(-0.3,-0.0025,0.005,0,2,[(255,255,255),None])
        road.addLine(l,0,road.segments[-1].index)
        l=Line(-1.0,0.01,0.01,0,1,[(255,255,255)])
        road.addLine(l,0,road.segments[-1].index)
        l=Line(1.0,-0.01,-0.01,0,1,[(255,255,255)])
        road.addLine(l,0,road.segments[-1].index)

        road.objects=objects


    def run(self):
        while self.running:
            dt=self.clock.tick(self.fps)/1000.0

            self.handle_events()
            self.keys=pygame.key.get_pressed()

            self.update(dt)
            self.draw()

        pygame.quit()



if __name__ == "__main__":

    j=Juego()
    j.run()
