from Road import VisibleSegment

class Object:
    def __init__(self):
        self.img=""
        self.metadata=None
        self.profile=None
        self.z=0.0
        self.x_rel=0.0
        self.collidable=True


class VisibleObject(Object):
    def __init__(self,obj: Object,seg: VisibleSegment):
        super().__init__()
        self.__dict__.update(obj.__dict__)
        self.obj=obj


        #interpolar x e y
        z_pos=self.z
        x=self.x_rel
        
        length=seg.end.z-seg.start.z

        pct=(z_pos-seg.start.z)/length
        dx=seg.start.x+((seg.end.x-seg.start.x)*pct)
        self.x=x+dx
        self.y=seg.start.y+((seg.end.y-seg.start.y)*pct)



