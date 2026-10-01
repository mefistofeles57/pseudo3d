from Road import VisibleSegment
from Road import Segment

class Object:

    NONE=0
    CAR=1
    PLAYER=2

    def __init__(self,anim=False,frametime=0.1):
        self.img=""
        self.metadata=None
        self.profile=None
        self.z=0.0
        self.x_rel=0.0
        self.collidable=True
        self.vs_index=-1
        self.side=0        
        self.type=Object.NONE
        self.isAnim=anim
        self.frametime=frametime
        self.age=0.0
        self.frame=0
        self.capas=()
        
    def load_metadata(self,cache):
        self.metadata=cache.metadata[self.img]

    @staticmethod
    def resolverCache(profile):
        if profile!=None and profile.cache!=None:
            return profile.cache
        from MapGenerator import MapGenerator
        return MapGenerator.visualProfile.cache

    def getVS(self, context, index=0):
        if self.vs_index==-1 or self.vs_index+index>len(context.frame_data.buffer)-1:
            return None
        return context.frame_data.buffer[self.vs_index+index]

    def update(self, dt):
        if self.metadata==None:
            cache=Object.resolverCache(self.profile)
            self.metadata=cache.metadata.get(self.img)
            if self.metadata==None:
                return
        self.age += dt
        if self.age>self.frametime:
            self.frame+=1
            self.frame%=self.metadata.frames
            self.age-=self.frametime

class VisibleObject(Object):
    def __init__(self,obj: Object,seg: VisibleSegment):
        super().__init__()
        self.__dict__.update(obj.__dict__)
        self.obj=obj
        if obj.isAnim:
            self.frame=obj.frame

        #interpolar x e y
        z_pos=self.z
        x=self.x_rel

        length=seg.end.z-seg.start.z

        pct=(z_pos-seg.start.z)/length
        dx=seg.start.x+(pct*seg.curve)
        dy=seg.start.y+(pct*seg.height)

        self.x_shift=0.0
        if seg.type==Segment.FORK:
            if self.side==-1:
                self.x_shift=seg.w0-2*seg.d_at(z_pos)
            elif self.side==1:
                self.x_shift=seg.w0
        dx=dx+self.x_shift

        self.x=x+dx
        self.y=dy


