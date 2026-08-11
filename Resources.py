import pygame
class Resources:
    smoke_frames = []

    @classmethod
    def load(cls):
        cls.smoke_frames = Resources.load_frames(
            "img/smoke.png",
            frame_width=32,
            frame_height=32
        )

    @staticmethod
    def load_frames(path, frame_width, frame_height):
        sheet = pygame.image.load(path).convert_alpha()

        frames = []
        count = sheet.get_width() // frame_width

        for i in range(count):
            rect = pygame.Rect(
                i * frame_width,
                0,
                frame_width,
                frame_height
            )

            frames.append(sheet.subsurface(rect).copy())

        return frames