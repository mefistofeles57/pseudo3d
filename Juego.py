import pygame
import math
from pathlib import Path
from Estados import NONE,STARTING,GAMEOVER,GAMEOVER_FINAL,NORMAL
from GameContext import GameContext
from Point import Point
from Message import Message
from Resources import Resources

class Juego:
    def __init__(self, width=800, height=450, screen_w=1280, screen_h=720, gen_scale=1, title="Cool Racing",fps=60):
        pygame.mixer.pre_init(
            frequency=44100,
            size=-16,
            channels=2,
            buffer=512
        )
        pygame.init()

        # Canales simultáneos para SFX
        pygame.mixer.set_num_channels(16)

        base = Path(__file__).resolve().parent
        self.sounds = {
            "derrape": pygame.mixer.Sound(base/"sound/derrape.wav"),
            "321go": pygame.mixer.Sound(base/"sound/321go.wav"),
            "checkpoint": pygame.mixer.Sound(base/"sound/checkpoint.wav"),
            "freno": pygame.mixer.Sound(base/"sound/freno.wav"),
            "crash": pygame.mixer.Sound(base/"sound/crash.wav"),
            "gameover": pygame.mixer.Sound(base/"sound/gameover.wav"),
            "hierba": pygame.mixer.Sound(base/"sound/hierba.wav"),
            "marcha": pygame.mixer.Sound(base/"sound/marcha.wav"),
            "choque": pygame.mixer.Sound(base/"sound/choque.wav")
        }
        self.sounds["derrape"].set_volume(0.5)
        self.sounds["freno"].set_volume(0.2)
        self.sounds["hierba"].set_volume(0.3)
        self.sounds["choque"].set_volume(0.5)
        self.sounds["gameover"].set_volume(0.2)

        pygame.display.set_caption(title)

        self.width=width
        self.height=height
        self.screen_w=screen_w
        self.screen_h=screen_h
        self.fps=fps

        #self.screen=pygame.Surface((self.width, self.height))
        
        self.screen=pygame.display.set_mode((self.screen_w,self.screen_h),pygame.SCALED | pygame.RESIZABLE)



        self.clock=pygame.time.Clock()
        self.running=True

        self.font = pygame.font.Font(None, 18)
        self.font100 = pygame.font.Font(None, 100)
        self.font150 = pygame.font.Font(None, 150)

        #objetos de juego

        self.context=GameContext(self.screen,self,gen_scale=(1/gen_scale))

        # situar el coche en la carretera y la camara detrás

        self.context.player.x=0.0
        self.context.player.y=0.0
        self.context.player.z=self.context.camera.player_z
        self.debug_text=""

        #mesajes
        self.messages=[]

        #sprites
        self.resources = Resources(gen_scale)
        
 

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self, dt):
        if self.context.estado == NONE:
            self.context.changeStatus(STARTING)
            return
        if self.context.estado==STARTING:
            self.context.countdown-=dt
            self.context.countdown=max(self.context.countdown,0.0)
            if self.context.countdown<=1e-6:
                self.messages.append(Message(self.screen.get_width() // 2,int(self.screen.get_height() *0.425),self.resources.go,1.0))
                self.context.changeStatus(NORMAL)
        elif self.context.estado!=GAMEOVER and self.context.estado!=GAMEOVER_FINAL:
            self.context.timer-=dt
            self.context.timer = max(self.context.timer, 0.0)
            if self.context.timer <= 1e-6:
                self.context.changeStatus(GAMEOVER)
        elif self.context.estado==GAMEOVER:
            if self.context.timer <= 1e-6:
                if self.context.player.speed<=1e-6:
                    self.context.changeStatus(GAMEOVER_FINAL)
            else:
                self.context.changeStatus(NORMAL)
            

        
        self.context.camera.update(dt)

        #borrar mensajes
        self.update_messages(dt)


    def draw(self):
        if self.context.estado == NONE:
            return

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

        self.print_hud()

        #countdown
        if self.context.estado==STARTING:
            #self.write_message(f"{math.floor(self.context.countdown)+1:1.0f}",self.screen.get_width() // 2, self.screen.get_height() // 2, font=self.font150)
            self.resources.draw_number_align(self.screen, self.resources.number86_items,self.resources.number86_dim, f"{math.floor(self.context.countdown+1.0):1.0f}", self.screen.get_width() // 2, (self.screen.get_height() // 2)-50)
        elif self.context.estado==GAMEOVER_FINAL:
            rect = self.resources.gameover.get_rect(midtop=(self.screen.get_width() // 2, int(self.screen.get_height()*0.4)))
            self.screen.blit(self.resources.gameover,rect)
        else:
            #dibujar mensajes
            for msg in self.messages:
                rect = msg.sprite.get_rect(midtop=(msg.x, msg.y))
                self.screen.blit(msg.sprite,rect)


        #pygame.transform.scale(self.screen, (self.screen_w, self.screen_h), self.escalated_screen)
        pygame.display.flip()



    def run(self):

        self.context.timer=60.0

        while self.running:
            dt=self.clock.tick(self.fps)/1000.0

            self.handle_events()
            self.context.keys=pygame.key.get_pressed()
            self.update(dt)
            self.draw()

        pygame.quit()

    def write_message(self,msg,x,y,font=None):
        if font==None:
            font=self.font150
        text = font.render(
            msg,
            True,
            (255, 210, 50)
        )

        shadow = font.render(
            msg,
            True,
            (140, 70, 0)
        )



        rect = text.get_rect(
            midtop=(x,y)
        )
        shadow_rect = shadow.get_rect(
            midtop=(x + 5, y+5)
        )

        self.context.screen.blit(shadow, shadow_rect)
        self.context.screen.blit(text, rect)

    def update_messages(self,dt):
        alive_messages = []

        for obj in self.messages:
            obj.update(dt)
            if not obj.dead:
                alive_messages.append(obj)

        self.messages = alive_messages

    def draw_wings(self,x,y,flip,number):
        if flip:
            seg1=self.resources.alas3_f
            siz1=3
            seg2=self.resources.alas2_f
            siz2=4
            seg3=self.resources.alas1_f
        else:
            seg1=self.resources.alas1
            siz1=7
            seg2=self.resources.alas2
            siz2=4
            seg3=self.resources.alas3

        alas_x=x
        rect = seg1.get_rect(topleft=(alas_x, y))
        self.screen.blit(seg1,rect)
        alas_x+=siz1

        for _ in range(number):
            rect = seg2.get_rect(topleft=(alas_x, y))
            self.screen.blit(seg2,rect)
            alas_x+=siz2
        rect = seg3.get_rect(topleft=(alas_x, y))
        self.screen.blit(seg3,rect)

    def draw_rpm(self,x,y):
        self.screen.blit(self.resources.rpm,(x,y))
        x_temp=x+40
        y_temp=y-4
        rpm=self.context.player.rpm
        for i in range(20):
            if rpm>0.05*i:
                #pinta_color
                idx=i//4
                self.screen.blit(self.resources.rpm_slide[idx],(x_temp,y_temp))
            else:
                #pinta gris
                self.screen.blit(self.resources.rpm_slide[5],(x_temp,y_temp))
            x_temp+=8

    def print_hud(self):
        #tiempo
        #self.write_message(f"{self.context.timer:3.0f}",self.screen.get_width() // 2, 8)
        rect = self.resources.time.get_rect(midtop=(self.screen.get_width() // 2, 30))
        self.screen.blit(self.resources.time,rect)
        self.resources.draw_number_align(self.screen, self.resources.number86_items,self.resources.number86_dim, f"{math.floor(self.context.timer):3.0f}", self.screen.get_width() // 2, int(self.screen.get_height()*0.1)+4)
        #score
        #alas
        self.draw_wings(self.screen.get_width()*0.05,30,False,15)
        self.draw_wings(self.screen.get_width()*0.155,30,True,15)

        rect = self.resources.score.get_rect(midtop=(int(self.screen.get_width()*0.13), 30))
        self.screen.blit(self.resources.score,rect)
        self.resources.draw_number_align(self.screen, self.resources.number43_items,self.resources.number43_dim, f"{self.context.score:07.0f}", self.screen.get_width()*0.13, 55)
        #stage
        #alas
        self.draw_wings(self.screen.get_width()*0.86,30,False,2)
        self.draw_wings(self.screen.get_width()*0.925,30,True,2)

        rect = self.resources.stage.get_rect(midtop=(int(self.screen.get_width()*0.9), 30))
        self.screen.blit(self.resources.stage,rect)
        self.resources.draw_number_align(self.screen, self.resources.number43_items,self.resources.number43_dim, f"{self.context.stage:1.0f}", self.screen.get_width()*0.9, 55)


        #gear
        #alas
        self.draw_wings(self.screen.get_width()*0.855,int(self.screen.get_height()*0.85),False,5)
        self.draw_wings(self.screen.get_width()*0.92,int(self.screen.get_height()*0.85),True,5)

        rect = self.resources.gear.get_rect(midtop=(int(self.screen.get_width()*0.9), int(self.screen.get_height()*0.85)))
        self.screen.blit(self.resources.gear,rect)

        rect = self.resources.gear.get_rect(midtop=(int(self.screen.get_width()*0.903), int(self.screen.get_height()*0.88)))
        self.screen.blit(self.resources.panel,rect)
        if self.context.player.marcha==0:
            rect = self.resources.gear.get_rect(midtop=(int(self.screen.get_width()*0.913), int(self.screen.get_height()*0.88)))
            self.screen.blit(self.resources.l,rect)
        else:
            rect = self.resources.gear.get_rect(midtop=(int(self.screen.get_width()*0.9094), int(self.screen.get_height()*0.88)))
            self.screen.blit(self.resources.h,rect)

        #velocidad
        #self.write_message(f"{self.context.player.speed*20:3.0f}",75, self.screen.get_height() - 100, font=self.font100)
        self.resources.draw_number_align(self.screen, self.resources.number43_items,self.resources.number43_dim, f"{self.context.player.speed*20:3.0f}", int(self.screen.get_width()*0.1), int(self.screen.get_height()*0.85),1)
        rect = self.resources.kmh.get_rect(midtop=(int(self.screen.get_width()*0.1)+60, int(self.screen.get_height()*0.88)))
        self.screen.blit(self.resources.kmh,rect)
        #RPM
        self.draw_rpm(int(self.screen.get_width()*0.03), int(self.screen.get_height()*0.93))

    def playSound(self, sound, once=True):
        sonido=self.sounds[sound]
        if sonido.get_num_channels() == 0 or not once:
            sonido.play()
    def stopSound(self, sound):
        sonido = self.sounds[sound]
        sonido.stop()


if __name__ == "__main__":

    j=Juego()
    j.run()
