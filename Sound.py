import wave
import time
import numpy as np
import sounddevice as sd


class EngineSound:
    def __init__(self, filename, base_pitch=1.0):
        self.sample = self._load_wav(filename)

        self.sample_pos = 0.0
        self.pitch = base_pitch
        self.volume = 0.8

        self.stream = sd.OutputStream(
            samplerate=44100,
            channels=1,
            dtype="float32",
            callback=self._callback,
            blocksize=512,
        )

    def _load_wav(self, filename):
        with wave.open(filename, "rb") as wav:
            channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            rate = wav.getframerate()
            frames = wav.readframes(wav.getnframes())

        if sample_width != 2:
            raise ValueError("Se espera un WAV PCM de 16 bits")

        data = np.frombuffer(frames, dtype=np.int16)

        if channels > 1:
            data = data.reshape(-1, channels).mean(axis=1)

        data = data.astype(np.float32) / 32768.0

        # De momento exigimos 44100 Hz para simplificar.
        if rate != 44100:
            raise ValueError(
                f"El WAV está a {rate} Hz; se esperan 44100 Hz"
            )

        return data

    def _callback(self, outdata, frames, time_info, status):
        if status:
            print(status)

        output = np.empty(frames, dtype=np.float32)

        length = len(self.sample)

        for i in range(frames):
            # Índices de las dos muestras que rodean la posición.
            pos = self.sample_pos

            i0 = int(pos)
            i1 = i0 + 1

            if i1 >= length:
                i1 = 0

            frac = pos - i0

            # Interpolación lineal.
            value = (
                self.sample[i0] * (1.0 - frac)
                + self.sample[i1] * frac
            )

            output[i] = value * self.volume

            # Aquí está el pitch.
            self.sample_pos += self.pitch

            while self.sample_pos >= length:
                self.sample_pos -= length

        outdata[:, 0] = output

    def start(self):
        self.stream.start()

    def stop(self):
        self.stream.stop()

    def close(self):
        self.stream.close()

    def set_pitch(self, pitch):
        self.pitch = max(0.1, pitch)

    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))


