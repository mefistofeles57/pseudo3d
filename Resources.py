import pygame
from pathlib import Path

class Resources:
    def __init__(self,gen_scale):
        base = Path(__file__).resolve().parent

        self.number43_dim=[(28,28),(20,20),(26,26),(27,27),(29,29),(28,28),(28,28),(23,23),(28,28),(28,28)]
        self.number86_dim=[(56,56),(40,40),(52,52),(54,54),(58,58),(56,56),(56,56),(46,46),(56,56),(56,56)]
        self.number43=pygame.image.load(base/"img"/"font.number.64.png").convert_alpha()
        #escala=2/gen_scale
        self.number86=pygame.transform.scale(self.number43, (self.number43.get_width() * 2, self.number43.get_height() * 2))
        self.number43_items=[]
        self.number86_items=[]

        x=0
        for i in range(10):
            w=self.number43_dim[i][0]
            self.number43_items.append(self.number43.subsurface(x,0,w,43))
            x+=w
        x=0
        for i in range(10):
            w=self.number86_dim[i][0]
            self.number86_items.append(self.number86.subsurface(x,0,w,86))
            x+=w

        text16=pygame.image.load(base/"img"/"text.16.png").convert_alpha()
        text32=pygame.transform.scale(text16, (text16.get_width() * 2, text16.get_height() * 2))
        messages_mini=pygame.image.load(base/"img"/"messages.png").convert_alpha()
        messages=pygame.transform.scale(messages_mini, (messages_mini.get_width() * 2, messages_mini.get_height() * 2))
        gear_mark=pygame.image.load(base/"img"/"gear.png").convert_alpha()
        #gear_mark=pygame.transform.scale(gear_mark, (gear_mark.get_width() * 2, gear_mark.get_height() * 2))

        self.time=text32.subsurface(0,0,102,32)
        #self.score=self.text32.subsurface(104,0,110,32)
        self.score=text16.subsurface(52,0,55,16)
        self.stage=text16.subsurface(108,0,55,16)
        self.gear=text16.subsurface(164,0,44,16)
        self.kmh=text16.subsurface(209,0,33,16)
        self.rpm=text16.subsurface(243,0,34,16)
        self.alas1=text16.subsurface(278,0,8,16)
        self.alas2=text16.subsurface(287,0,4,16)
        self.alas3=text16.subsurface(292,0,3,16)
        self.alas1_f=pygame.transform.flip(self.alas1, True, False)
        self.alas2_f=pygame.transform.flip(self.alas2, True, False)
        self.alas3_f=pygame.transform.flip(self.alas3, True, False)
        self.go=messages.subsurface(0,0,136,86)
        self.checkpoint=messages.subsurface(136,0,484,86)
        self.gameover=messages.subsurface(0,86,632,126)
        self.panel=gear_mark.subsurface(0,0,41,52)
        self.h=gear_mark.subsurface(41,0,26,52)
        self.l=gear_mark.subsurface(67,0,19,52)
        self.rpm_slide=[]
        for i in range(6):
            self.rpm_slide.append(messages_mini.subsurface(i*8,106,8,24))



    def draw_number(self,surface, digits,dim, value, x, y,spacing=0):
        for char in str(value):
            if char.isdigit():
                surface.blit(digits[int(char)], (x, y))
                x += dim[int(char)][1] + spacing

    def draw_number_align(self,surface, digits,dim, value, center_x, y,spacing=0,h_align=0):
        chars = str(value)

        width = sum(
            dim[int(char)][1]
            for char in chars
            if char.isdigit()
        )

        width += spacing * max(0, len(chars) - 1)

        if h_align==0:
            x = center_x - width // 2
        elif h_align<0:
            x = center_x
        else:
            x = center_x - width

        self.draw_number(surface, digits, dim, value, x, y, spacing)

