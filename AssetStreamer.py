import time
import json
import pygame
from pathlib import Path
from Road import Segment

class AssetStreamer:

    def __init__(self,cache,archivo,ventana=50,paso=10.0):
        self.cache=cache
        self.ventana=ventana
        self.paso=paso
        self.ultima_z=None
        self.cola_carga=[]
        self.cola_liberar=[]
        self.gen=None

        with open(archivo,"r",encoding="utf-8") as f:
            datos=json.load(f)

        self.catalogo={}
        for asset in datos["assets"]:
            asset.setdefault("flip",False)
            asset.setdefault("shadow",False)
            asset.setdefault("escala",1.0)
            asset.setdefault("permanente",False)
            self.catalogo[asset["name"]]=asset

        for asset in self.catalogo.values():
            if asset["permanente"]:
                self.cola_carga.append(asset["name"])

    def nombreBase(self,nombre):
        if nombre.endswith(".flip"):
            return nombre[:-len(".flip")]
        return nombre

    def actualizar(self,road,z_jugador):
        if self.ultima_z!=None and z_jugador-self.ultima_z<self.paso:
            return
        self.ultima_z=z_jugador

        necesarios=set(nombre for nombre,asset in self.catalogo.items() if asset["permanente"])

        inicio=road.current_segment
        fin=min(inicio+self.ventana,len(road.segments)-1)
        z_inicio=road.segments[inicio].z
        z_fin=road.segments[fin].z

        for o in road.objects:
            if o.z<z_inicio:
                continue
            if o.z>z_fin:
                break
            nombre=self.nombreBase(o.img)
            if nombre in self.catalogo:
                necesarios.add(nombre)

        cargados=set(self.cache.metadata.keys())

        for nombre in necesarios-cargados:
            if nombre not in self.cola_carga:
                self.cola_carga.append(nombre)

        for nombre in cargados-necesarios:
            asset=self.catalogo.get(nombre)
            if asset!=None and not asset["permanente"] and nombre not in self.cola_liberar:
                self.cola_liberar.append(nombre)



    def avanzar(self,presupuesto):
        fin=time.perf_counter()+presupuesto
        if self.gen is None:
            if not self.cola_liberar and not self.cola_carga:
                return
            self.gen=self.procesar()
        while time.perf_counter()<fin:
            try:
                next(self.gen)
            except StopIteration:
                self.gen=None
                return

    def procesar(self):
        while self.cola_liberar:
            self.cache.unload(self.cola_liberar.pop(0))
            yield
        while self.cola_carga:
            nombre=self.cola_carga.pop(0)
            for _ in self.cargarAsset(self.catalogo[nombre]):
                yield

    def cargarAsset(self,asset):
        ruta=str(self.cache.base/"img"/asset["file"])

        if asset["type"]=="image":
            img=pygame.image.load(ruta).convert_alpha()
            for _ in self.cache.generarImagen(asset["name"],img,asset["anchor"],asset["shadow"],asset["escala"]):
                yield
            if asset["flip"]:
                img2=pygame.transform.flip(pygame.image.load(ruta).convert_alpha(),True,False)
                ancla=(1-asset["anchor"][0],asset["anchor"][1])
                for _ in self.cache.generarImagen(asset["name"]+".flip",img2,ancla,asset["shadow"],asset["escala"]):
                    yield
        else:
            hoja=pygame.image.load(ruta).convert_alpha()
            frames=self.cache.load_frames(hoja,asset["ancho"],asset["alto"])
            for _ in self.cache.generarAnimacion(asset["name"],frames,asset["anchor"],asset["shadow"],asset["escala"]):
                yield
            if asset["flip"]:
                hoja2=pygame.transform.flip(pygame.image.load(ruta).convert_alpha(),True,False)
                frames2=list(reversed(self.cache.load_frames(hoja2,asset["ancho"],asset["alto"])))
                ancla=(1-asset["anchor"][0],asset["anchor"][1])
                for _ in self.cache.generarAnimacion(asset["name"]+".flip",frames2,ancla,asset["shadow"],asset["escala"]):
                    yield

    def procesarCompleto(self):
        for _ in self.procesar():
            pass