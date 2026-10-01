import json

from MapGenerator import MapGenerator
from Road import Segment, Line


class CircuitParser:

    OBJECT_DEFAULTS = {
        "step": 1.0,
        "offset": 0.0,
        "x": 0.0,
        "random_x": 0.0,
        "random_step": 0.0,
        "profile": None,
        "collidable": True,
        "anim": False,
        "frametime": 0.1,
    }

    def __init__(self, context, curves, heights, profiles=None, line_profiles=None, scene_profiles=None):
        self.context = context

        self.curves = curves
        self.heights = heights

        self.profiles = profiles if profiles is not None else {}
        self.line_profiles = line_profiles if line_profiles is not None else {}
        self.scene_profiles = scene_profiles if scene_profiles is not None else {}

        self.objects = []
        self.checkpoints = []
        self.pending_lines = []

        self.commands = {
            "R": self.command_road,
            "O": self.command_object,
            "V": self.command_vegetation,
            "F": self.command_forest,
            "MK": self.command_mark,
            "CHK": self.command_checkpoint,
            "BMP": self.command_bumps,
            "fork": self.command_fork,
            "E": self.command_enemy,
            "block": self.command_block,
            "LOAD": self.command_load,
            "LINE": self.command_line,
            "escenario": self.command_escenario,
            "FINISH": self.command_finish
        }

        self.last_segment=0
        self.current_tramo=None

    # ============================================================
    # LOAD
    # ============================================================

    def load(self, filename):
        inicio = len(self.context.road.segments)

        with open(filename, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith("#"):
                    continue
                command = json.loads(linea)
                self.parse_command(command)

        self.context.objects = self.objects
        self.context.checkpoints = self.checkpoints
        self.aplicar_lineas_pendientes(inicio)

    def cargar_generador(self, filename, comandos_por_paso=15):
        inicio = len(self.context.road.segments)

        with open(filename, "r", encoding="utf-8") as f:
            n = 0
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith("#"):
                    continue
                command = json.loads(linea)
                self.parse_command(command)
                n += 1
                if n % comandos_por_paso == 0:
                    yield

        self.context.objects = self.objects
        self.context.checkpoints = self.checkpoints
        self.aplicar_lineas_pendientes(inicio)

    def aplicar_lineas_pendientes(self, inicio):
        fin = len(self.context.road.segments) - 1
        for nombre, position, x in self.pending_lines:
            perfil = self.line_profiles[nombre]
            self.context.road.addLine(Line(perfil, position, x), inicio, fin)
        self.pending_lines = []

    # ============================================================
    # ESCENARIO
    # ============================================================

    def command_escenario(self, data):
        tipo = data.get("tipo")
        if tipo is None:
            raise ValueError(
                "Command 'escenario' requires 'tipo'"
            )
        if tipo not in self.scene_profiles:
            raise ValueError(
                f"Unknown escenario '{tipo}'"
            )

        self.context.escenario = self.scene_profiles[tipo]
        MapGenerator.setProfile(self.context.escenario)

    # ============================================================
    # LINE
    # ============================================================

    def command_line(self, data):
        nombre = data.get("profile")
        if nombre is None:
            raise ValueError(
                "Command 'LINE' requires 'profile'"
            )
        if nombre not in self.line_profiles:
            raise ValueError(
                f"Unknown line profile '{nombre}'"
            )

        position = data.get("position", 0.0)
        x = data.get("x", 0.0)

        self.pending_lines.append((nombre, position, x))

    # ============================================================
    # BLOCK
    # ============================================================

    def command_block(self, data):
        nombre = data.get("name", "")
        print(f"Parsing block: {nombre}")

    # ============================================================
    # COMMAND
    # ============================================================

    def parse_command(self, command):
        if not isinstance(command, dict):
            raise ValueError(
                f"Invalid command: {command}"
            )

        cmd = command.get("command")

        if cmd is None:
            raise ValueError(
                f"Command without 'command': {command}"
            )

        handler = self.commands.get(cmd)

        if handler is None:
            raise ValueError(
                f"Unknown circuit command '{cmd}'"
            )

        handler(command)

    # ============================================================
    # UTILITIES
    # ============================================================

    def get_segments(self, command):
        segments = command.get("segments")
        if segments is not None:
            if not isinstance(segments, int) or isinstance(segments, bool):
                raise ValueError(
                    f"'segments' must be a positive integer: {segments}"
                )
            if segments <= 0:
                raise ValueError(
                    f"'segments' must be a positive integer: {segments}"
                )

        return segments


    def get_side(self, data):
        side = data.get("side", 0)
        if side not in (-1, 0, 1):
            raise ValueError(f"'side' must be -1, 0 or 1: {side}")
        return side



    def get_current_tramo(self, segments):
        if segments is None:
            if not self.current_tramo:
                raise ValueError(
                    "This command requires a previous road section "
                    "when 'segments' is omitted"
                )
            return self.current_tramo
        first_segment=self.last_segment+1
        if first_segment+segments > len(self.context.road.segments):
            raise ValueError(
                f"Requested {segments} segments, "
                f"but only {len(self.context.road.segments)-self.last_segment} exist"
            )

        last_segment=first_segment+segments
        return self.context.road.segments[first_segment:last_segment]

    # ============================================================
    # CR, CL, CHR, CHL
    # ============================================================

    def command_road(self, data):

        self.last_segment=len(self.context.road.segments)-1

        start = self.last_segment+1

        pattern = self.parse_pattern(data)

        self.context.road.add(pattern)

        self.current_tramo = self.context.road.segments[start:]

    # ============================================================
    # O
    # ============================================================

    def command_object(self, command):
        segments = self.get_segments(command)

        image = command.get("img")

        if image is None:
            raise ValueError(
                "Command 'O' requires 'img'"
            )

        tramo = self.get_current_tramo(segments)

        params = {}

        for key, default in self.OBJECT_DEFAULTS.items():
            value = command.get(key, default)

            # Resolver profile desde YAML
            if key == "profile" and value is not None:
                value = self.get_profile(value)

            params[key] = value

        params["side"] = self.get_side(command)

        self.objects = MapGenerator.objects(
            self.objects,
            tramo,
            image,
            **params
        )

    # ============================================================
    # V
    # ============================================================
    def command_vegetation(self, data):
        segments = self.get_segments(data)

        tramo = self.get_current_tramo(segments)

        img = data["img"]

        self.objects = self.context.vegetacion(
            self.objects,
            tramo,
            x=data.get("x", 2.0),
            step_x=data.get("step_x", 1.0),
            step_z=data.get("step_z", 5.0),
            offset_z=data.get("offset", 0.0),
            number=data.get("number", 1),
            side=self.get_side(data),
            objeto=img
        )
    # ============================================================
    # F
    # ============================================================
    def command_forest(self, data):
        segments = self.get_segments(data)

        tramo = self.get_current_tramo(segments)

        img = data["img"]

        self.objects = self.context.bosque(
            self.objects,
            tramo,
            x=data.get("x", 2.0),
            step_x=data.get("step_x", 1.0),
            step_z=data.get("step_z", 5.0),
            offset_z=data.get("offset", 0.0),
            number=data.get("number", 1),
            random_x=data.get("random_x", 0.0),
            random_step=data.get("random_step", 0.0),
            side=self.get_side(data),
            objeto=img
        )
    # ============================================================
    # MK
    # ============================================================
    def command_mark(self, data):


        img = data["img"]

        MapGenerator.addMark(
            self.current_tramo[data["segment"]],
            img,
            x=data.get("x", 0.0),
            z=data.get("z", 0.0),
            w=data.get("w", 1.0),
            h=data.get("h", 1.0)
        )
    # ============================================================
    # CHK
    # ============================================================
    def command_checkpoint(self, data):
        if not self.current_tramo:
            raise ValueError(
                "Command 'CHK' requires a previous road section"
            )

        segment = data.get("segment", 0)

        try:
            s = self.current_tramo[segment]
        except IndexError:
            raise ValueError(
                f"CHK segment index {segment} out of range "
                f"for current tramo ({len(self.current_tramo)} segments)"
            )

        z_rel = data.get("z", 0.25)
        time = data.get("time", 55.0)

        # Asset
        self.objects = MapGenerator.objects(
            self.objects,
            [s],
            "checkpoint",
            step=1.0,
            offset=0.5,
            x=1.3,
            profile=self.profiles["checkpoint"]
        )

        # Checkpoint
        MapGenerator.addCheckpoint(
            s,
            z_rel,
            time
        )

        # Indicador
        self.checkpoints.append(
            s.z + z_rel
        )
    # ============================================================
    # LOAD
    # ============================================================
    def command_load(self, data):
        if not self.current_tramo:
            raise ValueError(
                "Command 'LOAD' requires a previous road section"
            )

        segment = data.get("segment", 0)

        try:
            s = self.current_tramo[segment]
        except IndexError:
            raise ValueError(
                f"LOAD segment index {segment} out of range "
                f"for current tramo ({len(self.current_tramo)} segments)"
            )

        z_rel = data.get("z", 0.25)

        next_data = data.get("next")
        if next_data is None:
            raise ValueError(
                "Command 'LOAD' requires 'next'"
            )

        next_map = {int(k): v for k, v in next_data.items()}

        MapGenerator.addLoadCircuit(
            s,
            z_rel,
            next_map
        )
    # ============================================================
    # FINISH
    # ============================================================
    def command_finish(self, data):
        if not self.current_tramo:
            raise ValueError(
                "Command 'FINISH' requires a previous road section"
            )

        segment = data.get("segment", -1)

        try:
            s = self.current_tramo[segment]
        except IndexError:
            raise ValueError(
                f"FINISH segment index {segment} out of range "
                f"for current tramo ({len(self.current_tramo)} segments)"
            )

        z_rel = data.get("z", 0.5)

        MapGenerator.addFinish(s, z_rel)
    # ============================================================
    # E
    # ============================================================
    def command_enemy(self, data):
        if not self.current_tramo:
            raise ValueError(
                "Command 'E' requires a previous road section"
            )

        segment = data.get("segment", 0)

        try:
            s = self.current_tramo[segment]
        except IndexError:
            raise ValueError(
                f"E segment index {segment} out of range "
                f"for current tramo ({len(self.current_tramo)} segments)"
            )

        z_rel = data.get("z", 0.0)
        x_rel = data.get("x_rel", 0.0)
        speed = data.get("speed", 10.0)
        img = data.get("img","enemigo.1")
        side = self.get_side(data)

        # Enemy
        MapGenerator.addEnemy(
            s,
            z_rel,
            x_rel,
            speed,
            img,
            side
        )

    # ============================================================
    # BMP
    # ============================================================
    def command_bumps(self, data):
        repeats = data.get("repeats", 3)
        segments = data.get("segments", 4)
        slope = data.get("slope", 0.025)

        if repeats <= 0:
            raise ValueError(
                f"Invalid BMP repeats: {repeats}"
            )

        if segments <= 0:
            raise ValueError(
                f"Invalid BMP segments: {segments}"
            )

        self.last_segment=len(self.context.road.segments)-1

        start = self.last_segment+1

        self.context.add_bumps(
            repeats=repeats,
            segments=segments,
            slope=slope,
            w=self.context.escenario.ancho_defecto
        )

        self.current_tramo = self.context.road.segments[start:]
    # ============================================================
    # PROFILE
    # ============================================================

    def get_profile(self, name):
        if not isinstance(name, str):
            raise ValueError(
                f"Profile must be a string in YAML: {name}"
            )

        if name not in self.profiles:
            raise ValueError(
                f"Unknown profile '{name}'"
            )

        return self.profiles[name]



    def parse_pattern(self, data):
        command = data.get("command")

        if command != "R":
            raise ValueError(
                f"Unknown pattern command '{command}'"
            )

        segments = data.get("segments")

        if segments is None:
            raise ValueError(
                "Pattern 'R' requires 'segments'"
            )

        ancho = self.context.escenario.ancho_defecto
        w0 = data.get("w0", ancho)
        w1 = data.get("w1", ancho)
        curve = self.get_constant(self.curves, data.get("curve"), "curve")
        height = self.get_constant(self.heights, data.get("height"), "height")

        return MapGenerator.pattern(curve, height, segments, w0, w1)

    def get_constant(self, table, key, kind):
        if key is None:
            return 0.0

        if key not in table:
            raise ValueError(
                f"Unknown {kind} constant '{key}'"
            )

        return table[key]

    # ============================================================
    # FORK
    # ============================================================

    def command_fork(self, data):
        road = self.context.road

        segments = self.get_segments(data)

        if segments is None:
            raise ValueError(
                "Command 'fork' requires 'segments'"
            )

        curve = self.get_constant(self.curves, data.get("curve"), "curve")

        # las dos carreteras nacen pegadas: d parte de w
        w = data.get("w", self.context.escenario.ancho_defecto)

        self.last_segment = len(road.segments) - 1

        start = self.last_segment + 1

        pattern = MapGenerator.fork(
            Segment.FORK,
            curve,
            segments,
            w
        )

        road.add(pattern)

        self.current_tramo = road.segments[start:]
        