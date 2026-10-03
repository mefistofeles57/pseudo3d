import pygame
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from GameContext import GameContext

CLAVE=(255,0,255)

def a_color_clave(img):
    # pixel art sin semitransparencias: color clave en vez de alfa por pixel
    sup=pygame.Surface(img.get_size()).convert()
    sup.fill(CLAVE)
    sup.blit(img,(0,0))
    sup.set_colorkey(CLAVE,pygame.RLEACCEL)
    return sup

class Background:
    def __init__(self,img,rolling,v_mov,mov,context:"GameContext",bg_color=(0,0,0),x=0.0,y=0.0,resize=1.0,color_clave=False):
        self.img=img
        self.f_img1=pygame.image.load(str(img)).convert_alpha()
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
            #self.f_img2=pygame.transform.flip(self.f_img1, True, False)
            self.f_img2=self.f_img1

        if color_clave:
            self.f_img1=a_color_clave(self.f_img1)
            #if rolling:
            #    self.f_img2=a_color_clave(self.f_img2)

        self.alpha=255
        self.f_img1.set_alpha(255, pygame.RLEACCEL)
        #if rolling:
        #    self.f_img2.set_alpha(255, pygame.RLEACCEL)            



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
            self.y_t=pos_y+(self.y-self.context.camera.horizon)

    def draw(self,s:pygame.Surface,fase=0.0):
        img_h=self.f_img1.get_height()
        alpha=255
        bajada=0
        if fase>0.0:
            if self.y_t-img_h<s.get_height()*0.25:
                alpha=int(255*(1.0-fase))
            elif self.rolling:
                bajada=int(fase*img_h)
            else:
                bajada=int(fase*(self.context.camera.horizon-(self.y_t-img_h)))
        posicion=self.x
        y=self.y_t+bajada
        if alpha!=self.alpha:
            self.alpha=alpha
            self.f_img1.set_alpha(alpha, pygame.RLEACCEL)
            #if self.rolling:
            #    self.f_img2.set_alpha(alpha, pygame.RLEACCEL)
        s.blit(self.f_img1, (posicion-self.f_img1.get_width(),y-img_h))
        if self.rolling:
            s.blit(self.f_img2, (posicion,y-self.f_img2.get_height()))
            if self.bg_color is not None:
                pygame.draw.rect(s,self.bg_color,pygame.Rect((0,self.y_t,self.context.screen.get_width(),self.context.screen.get_height()-self.y_t)),0)            

    def swapFondo(self):
        if self.f_img1!=None and self.f_img2!=None:
            aux=self.f_img1
            self.f_img1=self.f_img2
            self.f_img2=aux
