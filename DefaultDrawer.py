import pygame
from Camera import Camera
from Point import Point
from Road import VisibleSegment
from Road import Road

class DefaultDrawer:
    def draw(self,surface:pygame.Surface,c:Camera,vs:VisibleSegment,pc1,pc2):
        borde_i=-1
        borde_d=c.w

        profile=vs.visualProfile
        #la coordenada z es la escala



        # se produce cierto jitter subpixel en la cuantización alrededor de la distancia 15. Se ha podido comprobar forzando la monotonía,
        # pero no es aplicable a otras geometrias, como las elevaciones

        p1=Point( pc1.x-(profile.half_width*pc1.z) , pc1.y )
        p2=Point( pc1.x+(profile.half_width*pc1.z) , pc1.y )
        p3=Point( pc2.x-(profile.half_width*pc2.z) , pc2.y )
        p4=Point( pc2.x+(profile.half_width*pc2.z) , pc2.y )

        road_color=profile.road_colors[vs.index%2]
        outside_color=profile.outside_colors[vs.index%2]


        #dibuja el exterior izquierdo
        #solo si está dentro de la pantalla
        if p1.x>=0:
            puntos=((borde_i,p1.y),(p1.x,p1.y),(p3.x,p3.y),(borde_i,p3.y))
            self.pinta(surface,puntos,outside_color)
        #dibuja el exterior derecho
        if p2.x<c.w:
            puntos=((p2.x,p2.y),(borde_d,p2.y),(borde_d,p4.y),(p4.x,p4.y))
            self.pinta(surface,puntos,outside_color)
        #dibuja el trapecio de la carretera
        if p1.y<c.h:
            puntos=((p1.x,p1.y),(p2.x,p2.y),(p4.x,p4.y),(p3.x,p3.y))
            self.pinta(surface,puntos,road_color)

        #arcenes
        if profile.arcen_width>0.0:
            mod=vs.index%profile.arcen_freq
            color=profile.arcen_color[mod]
            if color!=None:
                #izquierdo
                pl1=Point(pc1.x-((profile.half_width+profile.arcen_width)*pc1.z),pc1.y)
                pl2=Point(pc1.x-((profile.half_width)*pc1.z),pc1.y)
                pl4=Point(pc2.x-((profile.half_width+profile.arcen_width)*pc2.z),pc2.y)
                pl3=Point(pc2.x-((profile.half_width)*pc2.z),pc2.y)
                puntos=(pl1.list2d(),pl2.list2d(),pl3.list2d(),pl4.list2d())
                self.pinta(surface,puntos,color)
                #derecho
                pl1=Point(pc1.x+((profile.half_width+profile.arcen_width)*pc1.z),pc1.y)
                pl2=Point(pc1.x+((profile.half_width)*pc1.z),pc1.y)
                pl4=Point(pc2.x+((profile.half_width+profile.arcen_width)*pc2.z),pc2.y)
                pl3=Point(pc2.x+((profile.half_width)*pc2.z),pc2.y)
                puntos=(pl1.list2d(),pl2.list2d(),pl3.list2d(),pl4.list2d())
                self.pinta(surface,puntos,color)
        #lineas
        for linea in c.road.getLines(vs.index):
            item=linea.getPoints(vs,pc1,pc2)
            if item!=None:
                (puntos,color)=item
                if color!=None:
                    self.pinta(surface,puntos,color)

    def drawObj(self,surface:pygame.Surface,c:Camera,cache,obj):
        #proyecta cada punto... tal vez haya que usar la LUT
        p1=c.project(Point(obj.x,obj.y,obj.z))
        img=cache.getImage(obj.img,p1.z)
        anchor=cache.anchor[obj.img]
        if img!=None:
            punto=(p1.x-(img.get_width()*anchor),p1.y-img.get_height())
            surface.blit(img,punto)

    def pinta(self,surface,puntos,color):
        pygame.draw.polygon(surface,color,puntos,0)

