import array
import math
import sys
import time
import pygame


# Canales del mixer apartados para motores: uno por coche
CANALES_RESERVADOS = 8

_libres = None
_bancos = {}


def _reservar_canales():
    global _libres
    if _libres is None:
        pygame.mixer.set_reserved(CANALES_RESERVADOS)
        _libres = list(range(CANALES_RESERVADOS))


def _leer_sonido(fichero):
    # pygame lo decodifica y lo deja en el formato y la frecuencia del mixer
    # (el módulo wave no existe en la versión web de Python)
    frecuencia, formato, canales = pygame.mixer.get_init()
    muestras = array.array("h")
    muestras.frombytes(pygame.mixer.Sound(fichero).get_raw())
    if canales > 1:
        mono = array.array("h")
        for i in range(0, len(muestras), canales):
            mono.append(sum(muestras[i:i + canales]) // canales)
        muestras = mono
    return muestras, frecuencia


def _remuestrear(muestras, paso):
    largo = len(muestras)
    n = max(1, round(largo / paso))
    # paso ajustado para que el bucle cierre exacto
    paso = largo / n
    salida = array.array("h", bytes(2 * n))
    for k in range(n):
        pos = k * paso
        i0 = int(pos)
        i1 = i0 + 1
        if i1 >= largo:
            i1 = 0
        a = muestras[i0]
        salida[k] = int(a + (muestras[i1] - a) * (pos - i0))
    return salida


class _Banco:
    # Versiones mono del bucle a tonos crecientes, separadas por el factor 'paso'
    def __init__(self, fichero, pitch_min, pitch_max, paso):
        frecuencia_mixer, formato, canales_mixer = pygame.mixer.get_init()
        if formato != -16:
            raise ValueError("El mixer tiene que estar en 16 bits con signo")
        muestras, frecuencia = _leer_sonido(fichero)
        self.frecuencia = frecuencia_mixer
        self.canales = canales_mixer
        self.pitch_min = pitch_min
        self.log_paso = math.log(paso)
        n = max(2, int(math.ceil(math.log(pitch_max / pitch_min) / self.log_paso)) + 1)
        self.versiones = []
        for i in range(n):
            pitch = pitch_min * paso ** i
            self.versiones.append(_remuestrear(muestras, pitch * frecuencia / frecuencia_mixer))

    def tramo(self, version, inicio, n):
        # n muestras mono de la versión a partir de 'inicio', dando la vuelta al bucle
        datos = self.versiones[version]
        largo = len(datos)
        salida = array.array("h")
        while n > 0:
            trozo = min(n, largo - inicio)
            salida.extend(datos[inicio:inicio + trozo])
            n -= trozo
            inicio = 0
        return salida

    def a_mixer(self, mono):
        # mono -> formato del mixer (mismo valor en todos los canales)
        if self.canales == 1:
            return mono.tobytes()
        salida = array.array("h", bytes(2 * len(mono) * self.canales))
        for c in range(self.canales):
            salida[c::self.canales] = mono
        return salida.tobytes()


class SonidoMotor:
    PITCH_MIN = 1.3
    PITCH_MAX = 3.7
    PASO = 1.02
    HISTERESIS = 0.8
    # cuánto audio se deja escrito por delante de lo que está sonando: es el retardo
    # de respuesta al tono y aguanta frames de hasta esa duración sin cortes.
    # En el navegador el mixer pide bloques de 4096 muestras (93 ms) de golpe
    if sys.platform == "emscripten":
        ADELANTO = 0.25
    else:
        ADELANTO = 0.15
    CINTA = 1.0
    MEZCLA_MS = 25

    def __init__(self, fichero, volumen=0.8):
        clave = (fichero, self.PITCH_MIN, self.PITCH_MAX, self.PASO)
        if clave not in _bancos:
            _bancos[clave] = _Banco(fichero, self.PITCH_MIN, self.PITCH_MAX, self.PASO)
        self.banco = _bancos[clave]
        b = self.banco
        self.bytes_frame = 2 * b.canales
        self.frames_cinta = int(self.CINTA * b.frecuencia)
        self.frames_adelanto = int(self.ADELANTO * b.frecuencia)
        self.frames_mezcla = int(self.MEZCLA_MS / 1000 * b.frecuencia)
        # el bucle del mixer es una cinta circular en la que se escribe por delante de lo que suena
        self.cinta = pygame.mixer.Sound(buffer=bytes(self.frames_cinta * self.bytes_frame))
        self.plano = memoryview(self.cinta).cast("B")
        self.pitch = self.PITCH_MIN
        self.volumen = volumen
        self.pan = 0.0
        self.id = None
        self.canal = None
        self.version = 0
        self.pos = 0
        self.escrito = 0
        self.t_inicio = 0.0

    def start(self):
        # Se puede llamar cada frame: si no quedaban canales libres, lo vuelve a intentar
        if self.canal is not None:
            return
        _reservar_canales()
        if len(_libres) == 0:
            return
        self.id = _libres.pop(0)
        self.canal = pygame.mixer.Channel(self.id)
        self.plano[:] = bytes(len(self.plano))
        self.escrito = 0
        self.version = self._version_objetivo()
        self.pos = 0
        # entrada fundida desde silencio, y el resto del adelanto
        n = self.frames_mezcla
        nueva = self.banco.tramo(self.version, 0, n)
        entrada = array.array("h", bytes(2 * n))
        for k in range(n):
            entrada[k] = int(nueva[k] * k / n)
        self._escribir(entrada)
        self.pos = n % len(self.banco.versiones[self.version])
        self._escribir(self._siguiente(self.frames_adelanto - n))
        self.canal.play(self.cinta, loops=-1)
        self.t_inicio = time.perf_counter()
        self._aplicar_volumen()

    def stop(self):
        if self.canal is None:
            return
        self.canal.fadeout(60)
        _libres.append(self.id)
        self.id = None
        self.canal = None

    def close(self):
        self.stop()

    def set_pitch(self, pitch):
        # hay que llamarlo cada frame: además de fijar el tono, rellena la cinta
        self.pitch = max(self.PITCH_MIN, min(self.PITCH_MAX, pitch))
        self._rellenar()

    def set_volume(self, volumen):
        self.volumen = max(0.0, min(1.0, volumen))
        self._aplicar_volumen()

    def set_pan(self, pan):
        # -1 todo a la izquierda, 0 centro, 1 todo a la derecha
        self.pan = max(-1.0, min(1.0, pan))
        self._aplicar_volumen()

    def _posicion(self):
        x = math.log(self.pitch / self.banco.pitch_min) / self.banco.log_paso
        return max(0.0, min(float(len(self.banco.versiones) - 1), x))

    def _version_objetivo(self):
        return int(round(self._posicion()))

    def _cabeza(self):
        # frame que está sonando ahora, contando desde el arranque
        return int((time.perf_counter() - self.t_inicio) * self.banco.frecuencia)

    def _rellenar(self):
        if self.canal is None:
            return
        cabeza = self._cabeza()
        if self.escrito < cabeza:
            # la cabeza nos ha adelantado (un frame muy largo): se continúa desde ella
            self.escrito = cabeza
        objetivo = cabeza + self.frames_adelanto
        if self.escrito >= objetivo:
            return
        if abs(self._posicion() - self.version) > self.HISTERESIS:
            self._cruzar(self._version_objetivo())
        falta = objetivo - self.escrito
        if falta > 0:
            self._escribir(self._siguiente(falta))

    def _siguiente(self, n):
        datos = self.banco.tramo(self.version, self.pos, n)
        self.pos = (self.pos + n) % len(self.banco.versiones[self.version])
        return datos

    def _cruzar(self, nueva):
        # la versión nueva entra en el mismo punto del bucle y se mezcla muestra a muestra
        vieja = self.version
        largo_viejo = len(self.banco.versiones[vieja])
        largo_nuevo = len(self.banco.versiones[nueva])
        inicio = int(self.pos / largo_viejo * largo_nuevo) % largo_nuevo
        n = self.frames_mezcla
        a = self.banco.tramo(vieja, self.pos, n)
        b = self.banco.tramo(nueva, inicio, n)
        mezcla = array.array("h", bytes(2 * n))
        for k in range(n):
            mezcla[k] = int(a[k] + (b[k] - a[k]) * k / n)
        self._escribir(mezcla)
        self.version = nueva
        self.pos = (inicio + n) % largo_nuevo

    def _escribir(self, mono):
        datos = self.banco.a_mixer(mono)
        inicio = (self.escrito % self.frames_cinta) * self.bytes_frame
        primero = min(len(datos), len(self.plano) - inicio)
        self.plano[inicio:inicio + primero] = datos[:primero]
        if primero < len(datos):
            self.plano[0:len(datos) - primero] = datos[primero:]
        self.escrito += len(mono)

    def _aplicar_volumen(self):
        if self.canal is None:
            return
        izquierda = 1.0
        derecha = 1.0
        if self.pan > 0:
            izquierda = 1.0 - self.pan
        elif self.pan < 0:
            derecha = 1.0 + self.pan
        self.canal.set_volume(self.volumen * izquierda, self.volumen * derecha)
