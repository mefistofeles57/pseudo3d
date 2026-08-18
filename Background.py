import pygame
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from GameContext import GameContext

class Background:
    def __init__(self,img,rolling,v_mov,mov,context:"GameContext",bg_color=(0,0,0),x=0.0,y=0.0,resize=1.0):
        base = Path(__file__).resolve().parent
        self.img=img
        self.f_img1=pygame.image.load(base/img).convert_alpha()
        #escalar la imagen
        if resize!=1.0:
            self.f_img1 = pygame.transform.scale(self.f_img1,(int(self.f_img1.get_width() * resize), int(self.f_img1.get_height() * resize)))
        self.rolling=rolling
        self.mov=mov
        self.x=x
        self.y_t=y
        self.y=y
        self.v_mov=False
        self.f_img2=None
        self.context=context
        self.w=context.screen.get_width()
        self.v_mov=v_mov
        self.bg_color=bg_color
        if rolling:
            self.f_img2=pygame.transform.flip(self.f_img1, True, False)



    def update(self,move_x,pos_y):
        self.x+=move_x*(self.mov*-1)

        if self.rolling:
            img=self.f_img1
            if self.x+img.get_width()<self.w:
                self.x+=img.get_width()
                self.swapFondo()
            elif self.x-img.get_width()>0:
                self.x-=img.get_width()
                self.swapFondo()
        if self.v_mov:
            self.y_t=pos_y


    def draw(self,s:pygame.Surface):
            posicion=self.x
            s.blit(self.f_img1, (posicion-self.f_img1.get_width(),self.y_t-self.f_img1.get_height()))
            if self.rolling:
                s.blit(self.f_img2, (posicion,self.y_t-self.f_img2.get_height()))
                pygame.draw.rect(s,self.bg_color,pygame.Rect((0,self.y_t,self.context.screen.get_width(),self.context.screen.get_height()-self.y_t)),0)

    def swapFondo(self):
        if self.f_img1!=None and self.f_img2!=None:
            aux=self.f_img1
            self.f_img1=self.f_img2
            self.f_img2=aux
