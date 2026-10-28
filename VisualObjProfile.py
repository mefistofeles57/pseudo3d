class VisualObjProfile:
    def __init__(self):
        self.shadow_color=(0,0,0)
        self.shadow_alpha=60
        self.shadow_width_factor=1.4
        self.shadow_height=0.05
        self.shadow_offset_x=0.0
        self.shadow_offset_z=0.0
        self.cache=None
        self.collide_radius=0.0
        self.collide_radius2=0.0
        self.cable=False
        self.cable_alto=0.0
        self.cable_dx=[]
        self.cable_flecha=0.0
        self.cable_vano=0.0
        self.cable_color=(40,34,30)
        self.sombra_suelo=False
        self.sombra_atras=0.045
        self.sombra_delante=0.10
        #farolas
        self.luz=False
        self.luz_color=(255,158,74)
        self.luz_ancho=1.3
        self.luz_alto=0.15
        self.luz_hacia_centro=0.3
        self.luz_offset_z=0.0
        self.luz_escalones=[(1.0,0.15),(0.7,0.3),(0.4,0.45)]        