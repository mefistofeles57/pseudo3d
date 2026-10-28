import colorsys
import pygame

#rampas de color por filtro: la luminancia de cada color se cambia por un tono de la rampa
RAMPAS={
    "noche":[(18,11,36),(30,20,54),(46,30,76),(66,42,98),(92,58,122),(124,78,140),(164,104,150),(206,146,168),(240,206,200)]
}

def color_filtrado(r,g,b,rampa):
    h,l,s=colorsys.rgb_to_hls(r/255,g/255,b/255)
    #lo que brilla (naranjas y rojos saturados y claros) se queda: pilotos, bombillas, reflectantes
    if s>0.6 and l>0.45 and (h<0.11 or h>0.95):
        return (r,g,b)
    lum=0.299*r+0.587*g+0.114*b
    i=min(len(rampa)-1,int(lum/256*len(rampa)))
    return rampa[i]

def color_tono(r,g,b):
    #conserva el tono: oscurece, baja la saturacion y lo acerca un poco al morado
    h,l,s=colorsys.rgb_to_hls(r/255,g/255,b/255)
    if s>0.6 and l>0.45 and (h<0.11 or h>0.95):
        return (r,g,b)
    dh=((0.78-h+0.5)%1.0)-0.5
    h=(h+dh*0.15)%1.0
    rr,gg,bb=colorsys.hls_to_rgb(h,l*0.6,s*0.75)
    return (int(rr*255),int(gg*255),int(bb*255))

def aplicar(surf,nombre,conservar=None):
    out=surf.copy()
    datos=pygame.image.tobytes(out,"RGBA")
    colores=set(memoryview(datos).cast("I"))
    pa=pygame.PixelArray(out)
    for v in colores:
        r=v&255
        g=(v>>8)&255
        b=(v>>16)&255
        a=v>>24
        if a==0:
            continue
        if conservar!=None and [r,g,b] in conservar:
            continue
        if nombre=="noche_color":
            nuevo=color_tono(r,g,b)
        else:
            nuevo=color_filtrado(r,g,b,RAMPAS[nombre])
        if nuevo!=(r,g,b):
            pa.replace((r,g,b,a),(nuevo[0],nuevo[1],nuevo[2],a))
    pa.close()
    return out