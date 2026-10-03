import random
from RoadMark import RoadMark
from Road import Segment
from Object import Object
from Event import EnemySpawn,Checkpoint,Finish,LoadCircuit

class MapGenerator:
    rng=random.Random(0)

    visualProfile=None
    visualObjProfile=None
    @staticmethod
    def setProfile(profile):
        MapGenerator.visualProfile=profile

    @staticmethod
    def setObjProfile(profile):
        MapGenerator.visualObjProfile=profile

    @staticmethod
    def genSegment(curve,height,w0=1.0,w1=1.0):
        return Segment(1.0,curve,height,profile=MapGenerator.visualProfile,w0=w0,w1=w1)

    @staticmethod
    def pattern(curve,height,length,w0=1.0,w1=1.0):
        segments=[]
        w0_val=w0
        step=(w1-w0)/length if w0!=w1 else 0.0
        for _ in range(length):
            w1_val=w0_val+step
            segments.append(MapGenerator.genSegment(curve,height,w0_val,w1_val))
            w0_val=w1_val
        return segments
    
    @staticmethod
    def values(max,length):
        values=[]
        at=0.0
        dt=1.0/length
        prev=0.0
        for _ in range(length):
            at+=dt
            value=-max*MapGenerator.smoothstep(at)
            values.append(value-prev)
            prev=value
        return values


    @staticmethod
    def smoothstep(t):
        return (3*(t*t)) - (2*(t*t*t))
    
    @staticmethod
    def objects(objetos,tramo,image,step,offset,x,random_x=0.0,random_step=0.0,profile=None,collidable=True,anim=False,frametime=0.1,side=0,lod=None):
        z_pos=tramo[0].z+offset
        z_end=tramo[-1].z+tramo[-1].length
        i=0
        while z_pos<z_end:
            #añadir el objeto en z_pos
            if anim:
                obj=Object(anim=True,frametime=frametime)
            else:
                obj=Object()
            if profile==None:
                obj.profile=MapGenerator.visualObjProfile
            else:
                obj.profile=profile
            obj.img=image
            #posisiona aqui el objeto
            obj.z=z_pos
            obj.x_rel=x
            #añadir un random a la posicion z
            if random_step!=0:
                obj.z+=MapGenerator.rng.uniform(0,random_step)
            if random_x!=0:
                obj.x_rel+=MapGenerator.rng.uniform(0,random_x)
            obj.collidable=collidable
            obj.side=side
            if lod!=None:
                if i%8==0:
                    obj.lod_hasta=9999
                elif i%4==0:
                    obj.lod_hasta=lod[2]
                elif i%2==0:
                    obj.lod_hasta=lod[1]
                else:
                    obj.lod_hasta=lod[0]

            objetos.append(obj)

            i+=1
            z_pos+=step
        #añadir los objetos detras de z_end
        return objetos

    @staticmethod
    def addMark(s:Segment,img,x,z,w,h):
        rm=RoadMark()
        rm.img=img
        rm.offset_x=x
        rm.offset_z=z
        rm.width=w
        rm.height=h
        s.road_marks.append(rm)

    @staticmethod
    def addEnemy(s:Segment,z_rel, x_rel,speed,img,side=0):
        e=EnemySpawn(z_rel,x_rel,speed,img,side)
        s.events.append(e)


    @staticmethod
    def addCheckpoint(s:Segment,z_rel, time):
        e=Checkpoint(z_rel,time)
        s.events.append(e)

    @staticmethod
    def addFinish(s:Segment,z_rel):
        e=Finish(z_rel)
        s.events.append(e)

    @staticmethod
    def fork(type,curve,length,w):
        segments=[]
        d=w
        for _ in range(length):
            s=MapGenerator.genSegment(curve,0.0,w,w)
            s.type=type
            s.d=d
            d+=curve
            segments.append(s)
        return segments

    @staticmethod
    def addLoadCircuit(s: Segment, z_rel, next_map):
        e = LoadCircuit(z_rel, next_map)
        s.events.append(e)