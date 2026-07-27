import pygame
from Camera import Camera
from Point import Point
from Road import VisibleSegment
from Road import Road
from Object import Object

class DefaultDrawer:

    def brillo(self,distancia,max):
        min_brillo=1.0
        max_brillo=0.3
        min_distancia=0.0
        max_distancia=max

        #y = y₁ + (x - x₁) × (y₂ - y₁) / (x₂ - x₁)

        y=min_brillo +(((distancia-min_distancia)*(max_brillo-min_brillo))/(max_distancia-min_distancia))
        return y


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

        #road_color=profile.road_colors[vs.index%2]
        #outside_color=profile.outside_colors[vs.index%2]
        road_color=profile.road_colors[0]
        outside_color=profile.outside_colors[0]
        brillo=self.brillo(vs.start.z-c.z,c.view_distance)
        road_color=(road_color[0]*brillo,road_color[1]*brillo,road_color[2]*brillo)
        outside_color=(outside_color[0]*brillo,outside_color[1]*brillo,outside_color[2]*brillo)


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
            color=(color[0]*brillo,color[1]*brillo,color[2]*brillo)
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

    def drawObj(self,surface:pygame.Surface,c:Camera,obj:Object,vs:VisibleSegment,shadow=False):
        if (obj.img=="piedra" or obj.img=="piedra.flip") and shadow:
            pass
        p1=c.project(Point(obj.x,obj.y,obj.z))
        cache=vs.visualProfile.cache
        img=cache.getImage(obj.img,p1.z)
        metadata=cache.metadata[obj.img]
        if img!=None:
            if shadow==False:
                punto=(p1.x-(img.get_width()*metadata.anchor_x),p1.y-img.get_height()*metadata.anchor_y)
                surface.blit(img,punto)
            elif metadata.shadow:
                self.drawShadow(surface,img,p1,vs)

    def drawShadow(self,surface:pygame.Surface,img,p:Point,obj:VisibleSegment):
        #calcula el tamaño de la sombra en función al ancho del objeto y a un tamaño fijo
        #dibuja una elipse en el punto p con el ancho calculado y el color y alfa indicados en el vp
        profile=obj.visualProfile
        shadow_color=profile.shadow_color
        shadow_alpha=profile.shadow_alpha
        shadow_width_factor=profile.shadow_width_factor
        shadow_height=profile.shadow_height


        scale=p.z
        width=img.get_width()*shadow_width_factor
        height=shadow_height*scale


        shadow = pygame.Surface((width, height), pygame.SRCALPHA)

        pygame.draw.ellipse(
            shadow,
            (shadow_color[0], shadow_color[1], shadow_color[2], shadow_alpha),      # RGBA
            (0, 0, width, height)
        )

        surface.blit(shadow, (p.x - width // 2, p.y - height // 2))




    def pinta(self,surface,puntos,color):
        pygame.draw.polygon(surface,color,puntos,0)

