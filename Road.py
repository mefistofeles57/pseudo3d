from Point import Point


#Representación estática de un segmento en el mapa
class Segment:
    #tipos de segmento. normal, fork y join
    #de momento join no se usa
    NORMAL=0
    FORK=1
    JOIN=2

    def __init__(self,length=0.0,curve=0.0,height=0.0,profile=None,w0=1.0,w1=1.0):
        self.type=Segment.NORMAL
        #distancia al eje del fork desde el inicio de la curva.
        self.d=0.0
        #longitud del segmento
        self.length=length
        #desplazamiento x local
        self.curve=curve
        #desplazamiento y local
        self.height=height
        #perfil
        self.visualProfile=profile
        #indice del mapa
        self.index=0
        #posicion global en z
        self.z=0.0
        #listado de marcas en el segmento
        self.road_marks=[]
        #listado de eventos en el segmento
        self.events = []
        #medio ancho de carretera al inicio y al final del segmento
        self.w0=w0
        self.w1=w1

    #calculo de curva. Cambia en los forks según la rama
    def curve_for(self,side):
        # side: -1 izquierda, +1 derecha
        if self.type==Segment.FORK:
            return side*self.curve
        return self.curve

#Segmento dentro del buffer del frame
class VisibleSegment:
    #se construye a partir de un segmento del mapa y el segmento anterior del buffer
    def __init__(self,s:Segment,origin,playerx=None,playery=None,side=1):
        if origin!=None:
            x=origin.end.x
            y=origin.end.y
            c=origin.curve
            h=origin.height
            #el valor d acumula la distancia con el eje de simetria del fork
            if origin.type==Segment.FORK:
                d=(origin.d+origin.curve)
            else:
                d=None
            if origin.type==Segment.FORK and s.type!=Segment.FORK:
                # el tramo posterior se ancla al final de la rama del jugador
                # para compensar que los tramos de fork están desplazados con respecto a su eje de simetría
                if side==-1:
                    x+=origin.w1-2*(origin.d+origin.curve)
                    c=-origin.curve
                else:
                    x+=origin.w1
        else:
            x=y=c=h=0.0
            d=None
            if playerx!=None:
                x=-playerx
            if playery!=None:
                y=-playery
        #segmento del mapa asociado
        self.segment=s
        #desplazamiento x del segmento dentro del buffer
        self.curve=c+s.curve_for(1)
        #desplazamiento y del segmento dentro del buffer
        self.height=h+s.height
        #coordenadas 3d de inicio y fin
        self.start=Point(x,y,s.z)
        self.end=Point(x+self.curve,y+self.height,s.z+s.length)
        self.visualProfile=s.visualProfile
        self.index=s.index
        self.length=self.end.z-self.start.z
        self.road_marks=s.road_marks
        self.events = s.events
        self.w0=s.w0
        self.w1=s.w1

        self.type=s.type
        if s.type==Segment.FORK:
            if d is not None:
                self.d=d 
            else:
                self.d=s.d
        else:
            self.d=0.0



    #interpola la distancia en un punto z del centro con el eje de simetría del fork
    def d_at(self, z):
        if self.length<=0.0:
            return self.d
        t=(z-self.start.z)/self.length
        t=max(0.0,min(1.0,t))
        return self.d+self.curve*t

#perfil de linea de carretera.
#grosor es el grosor de la linea
#freq dice el numero de elementos y color es una lista con un color para cada indice%freq (None es sin pintar)
#offset es el desplazamiento del inicio del patrón
class LineProfile:
    def __init__(self,grosor,offset,freq,color):
        self.grosor=grosor
        self.offset=offset
        self.freq=freq
        self.color=color

class Line:
    def __init__(self,profile:LineProfile,position,x):
        self.profile=profile
        #origen de posicionamiento (0.0 centro +-1.0 extremos)
        self.position=position
        #desplamiento desde el origen
        self.x=x

    def getPoints(self,vs:VisibleSegment,pc1:Point,pc2:Point):
        p=self.profile
        mod=(vs.index+p.offset)%p.freq
        if mod<len(p.color):
            color=p.color[mod]
        else:
            color=None
        if color!=None:
            w0=vs.w0
            w1=vs.w1
            x1=pc1.x+((self.position*w1+self.x)*pc1.z)
            x4=pc2.x+((self.position*w0+self.x)*pc2.z)
            if self.position<0:
                ancho=p.grosor
            else:
                ancho=-p.grosor
            x2=x1+(ancho*pc1.z)
            x3=x4+(ancho*pc2.z)
            y1=pc1.y
            y2=y1
            y3=pc2.y
            y4=y3
            puntos=((x1,y1),(x2,y2),(x3,y3),(x4,y4))
            return (puntos,color)
class Road:

    def __init__(self):
        self.segments=[]
        self.current_segment=0
        self.objects=[]
        self.current_object=0
        self.lines=[]
        self.line_bounds=[]

    def add(self,segments):
        for segment in segments:
            segment.index=len(self.segments)
            if segment.index>0:
                s_ant=self.segments[segment.index-1]
                segment.z=s_ant.z+segment.length
            
            self.segments.append(segment)

    def addLine(self,line:Line,firstIndex,lastIndex):
        self.lines.append(line)
        self.line_bounds.append((firstIndex,lastIndex))

    def getLines(self,index):
        lineas=[]
        for (i,item) in enumerate(self.line_bounds):
            if item[0]<=index and item[1]>=index:
                lineas.append(self.lines[i])
        return lineas


