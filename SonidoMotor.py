import array
import math
import time
import wave
import pygame


# Canales del mixer apartados para motores: 2 por coche (jugador + 3 enemigos)
CANALES_RESERVADOS = 8

_libres = None
_bancos = {}


def _reservar_canales():
    global _libres
    if _libres is None:
        pygame.mixer.set_reserved(CANALES_RESERVADOS)
        _libres = list(range(CANALES_RESERVADOS))


def _leer_wav(fichero):
    with wave.open(fichero, "rb") as wav:
        canales = wav.getnchannels()
        ancho = wav.getsampwidth()
        frecuencia = wav.getframerate()
        datos = wav.readframes(wav.getnframes())
    if ancho != 2:
        raise ValueError("Se espera un WAV PCM de 16 bits")
    muestras = array.array("h")
    muestras.frombytes(datos)
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
    # Versiones del bucle a tonos crecientes, separadas por el factor 'paso', guardadas en el formato del mixer
    def __init__(self, fichero, pitch_min, pitch_max, paso):
        frecuencia_mixer, formato, canales_mixer = pygame.mixer.get_init()
        if formato != -16:
            raise ValueError("El mixer tiene que estar en 16 bits con signo")
        muestras, frecuencia = _leer_wav(fichero)
        self.frecuencia = frecuencia_mixer
        self.bytes_frame = 2 * canales_mixer
        self.pitch_min = pitch_min
        self.log_paso = math.log(paso)
        n = max(2, int(math.ceil(math.log(pitch_max / pitch_min) / self.log_paso)) + 1)
        self.datos = []
        for i in range(n):
            pitch = pitch_min * paso ** i
            mono = _remuestrear(muestras, pitch * frecuencia / frecuencia_mixer)
            datos = mono
            if canales_mixer > 1:
                datos = array.array("h", bytes(2 * len(mono) * canales_mixer))
                for c in range(canales_mixer):
                    datos[c::canales_mixer] = mono
            self.datos.append(datos.tobytes())

    def frames(self, version):
        return len(self.datos[version]) // self.bytes_frame

    def sonido(self, version, inicio):
        # el bucle empezando en el frame 'inicio': sigue siendo un bucle perfecto
        b = inicio * self.bytes_frame
        datos = self.datos[version]
        return pygame.mixer.Sound(buffer=datos[b:] + datos[:b])


class SonidoMotor:
    PITCH_MIN = 1.3
    PITCH_MAX = 3.7
    PASO = 1.02
    HISTERESIS = 0.8
    # pygame aplica los fundidos a saltos, uno por bloque de audio (~11.6 ms):
    # un fundido largo da saltos pequeños, que no se oyen como clic
    FUNDIDO_MS = 120
    # no se empieza otro cambio hasta que el fundido anterior ha terminado
    ESPERA_CAMBIO = 0.14

    def __init__(self, fichero, volumen=0.8):
        clave = (fichero, self.PITCH_MIN, self.PITCH_MAX, self.PASO)
        if clave not in _bancos:
            _bancos[clave] = _Banco(fichero, self.PITCH_MIN, self.PITCH_MAX, self.PASO)
        self.banco = _bancos[clave]
        self.pitch = self.PITCH_MIN
        self.volumen = volumen
        self.pan = 0.0
        self.ids = None
        self.canales = None
        self.activo = 0
        self.version = 0
        self.t0 = 0.0
        self.inicio = 0

    def start(self):
        # Se puede llamar cada frame: si no quedaban canales libres, lo vuelve a intentar
        if self.canales is not None:
            return
        _reservar_canales()
        if len(_libres) < 2:
            return
        self.ids = [_libres.pop(0), _libres.pop(0)]
        self.canales = [pygame.mixer.Channel(self.ids[0]), pygame.mixer.Channel(self.ids[1])]
        self.activo = 0
        self._sonar(self._version_objetivo(), 0)

    def stop(self):
        if self.canales is None:
            return
        for canal in self.canales:
            canal.stop()
        _libres.extend(self.ids)
        self.ids = None
        self.canales = None

    def close(self):
        self.stop()

    def set_pitch(self, pitch):
        self.pitch = max(self.PITCH_MIN, min(self.PITCH_MAX, pitch))
        if self.canales is None:
            return
        if time.perf_counter() - self.t0 < self.ESPERA_CAMBIO:
            return
        x = self._posicion()
        if abs(x - self.version) > self.HISTERESIS:
            self._cambiar(self._version_objetivo())

    def set_volume(self, volumen):
        self.volumen = max(0.0, min(1.0, volumen))
        self._aplicar_volumen()

    def set_pan(self, pan):
        # -1 todo a la izquierda, 0 centro, 1 todo a la derecha
        self.pan = max(-1.0, min(1.0, pan))
        self._aplicar_volumen()

    def _posicion(self):
        x = math.log(self.pitch / self.banco.pitch_min) / self.banco.log_paso
        return max(0.0, min(float(len(self.banco.datos) - 1), x))

    def _version_objetivo(self):
        return int(round(self._posicion()))

    def _fase(self):
        # punto del bucle por el que va la versión actual, de 0 a 1
        n = self.banco.frames(self.version)
        transcurrido = int((time.perf_counter() - self.t0) * self.banco.frecuencia)
        return ((self.inicio + transcurrido) % n) / n

    def _cambiar(self, version):
        # la nueva versión entra por el otro canal en el mismo punto del bucle y la vieja se funde
        n = self.banco.frames(version)
        inicio = int(self._fase() * n) % n
        self.canales[self.activo].fadeout(self.FUNDIDO_MS)
        self.activo = 1 - self.activo
        self._sonar(version, inicio)

    def _sonar(self, version, inicio):
        canal = self.canales[self.activo]
        canal.play(self.banco.sonido(version, inicio), loops=-1, fade_ms=self.FUNDIDO_MS)
        self.version = version
        self.inicio = inicio
        self.t0 = time.perf_counter()
        self._aplicar_volumen()

    def _aplicar_volumen(self):
        # solo el canal activo: el otro se está fundiendo y no hay que tocarlo
        if self.canales is None:
            return
        izquierda = 1.0
        derecha = 1.0
        if self.pan > 0:
            izquierda = 1.0 - self.pan
        elif self.pan < 0:
            derecha = 1.0 + self.pan
        self.canales[self.activo].set_volume(self.volumen * izquierda, self.volumen * derecha)
