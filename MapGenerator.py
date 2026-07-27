import random
from Road import Segment
from Object import Object

class MapGenerator:
    CURVE=0
    HILL=1
    NONE=0

    visualProfile=None
    @staticmethod
    def setProfile(profile):
        MapGenerator.visualProfile=profile

    @staticmethod
    def genSegment(type,value):
        if type==MapGenerator.CURVE:
            s=Segment(1.0,value,0.0,profile=MapGenerator.visualProfile)
        if type==MapGenerator.HILL:
            s=Segment(1.0,0.0,value,profile=MapGenerator.visualProfile)
        return s

    @staticmethod
    def pattern(type,max_curvature,entry_length,flat_length,exit_length):
        segments=[]
        #curva de entrada
        if entry_length>0:
            values=MapGenerator.values(max_curvature,entry_length)
            for value in values:
                segments.append(MapGenerator.genSegment(type,value))
            #zona intermedia
        for i in range(flat_length):
            s=Segment(1.0,max_curvature,0.0,profile=MapGenerator.visualProfile)
            segments.append(s)
        #salida
        if exit_length>0:
            values=MapGenerator.values(max_curvature,entry_length)
            for value in reversed(values):
                segments.append(MapGenerator.genSegment(type,value))
        return segments

    @staticmethod
    def values(max,length):
        values=[]
        at=0.0
        dt=1.0/length
        for i in range(length):
            at+=dt
            value=-max*MapGenerator.smoothstep(at)
            values.append(value)
        return values


    @staticmethod
    def smoothstep(t):
        return (3*(t*t)) - (2*(t*t*t))
    
    @staticmethod
    def merge(curve,hill):
        base=curve
        sec=hill
        c2h=False
        if len(hill)>len(curve):
            base=hill
            sec=curve
            c2h=True
        for i in range(len(sec)-1):
            if c2h:
                base[i].height=sec[i].height
            else:
                base[i].curve=sec[i].curve
        return base

    @staticmethod
    def objects(objetos,tramo,image,step,offset,x,random_x=0.0,random_step=0.0):
        objects=[]
        z_pos=tramo[0].start.z+offset
        if random_x!=0 or random_step!=0:
            rng=random.Random(z_pos)
        z_end=tramo[-1].end.z
        s_pointer=0
        obj_pointer=0
        count=len(tramo)
        while z_pos<z_end:
            #copiar en object todos los elementos de objetos anteriores a z_pos
            for item in objetos[obj_pointer:]:
                if item.z<=z_pos:
                    objects.append(item)
                    obj_pointer+=1
                else:
                    break
            #buscar el tramo que contiene z_pos
            for i in range(s_pointer,count):
                seg=tramo[i]
                if seg.start.z<=z_pos and seg.end.z>z_pos:
                    obj=Object()
                    obj.img=image
                    #posisiona aqui el objeto
                    #interpolar x e y
                    pct=(z_pos-seg.start.z)/seg.length
                    obj.x=seg.start.x+((seg.end.x-seg.start.x)*pct)+x
                    if random_x!=0:
                        obj.x+=rng.uniform(0,random_x)
                    obj.y=seg.start.y+((seg.end.y-seg.start.y)*pct)
                    obj.z=z_pos
                    #añadir un random no acumulable a la posicion z
                    if random_step!=0:
                        obj.z+=rng.uniform(0,random_step)

                    objects.append(obj)
                    break
            s_pointer=i
            z_pos+=step
        #añadir los objetos restantes
        for item in objetos[obj_pointer:]:
            objects.append(item)
        return objects
