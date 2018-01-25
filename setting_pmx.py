import bpy
import logging
import io

logger = logging.getLogger("setting_pmx")

if not logger.handlers:
    hdlr = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)-7s %(asctime)s %(message)s (%(funcName)s)", datefmt="%H:%M:%S")
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.DEBUG) # DEBUG, INFO, WARNING, ERROR, CRITICAL

logger.debug("init logger") # debug, info, warning, error, critical

class LoggingToTextContext():
    def __init__(self, logger):
        self.logger = logger
        self.stream = io.StringIO()
        self.handler = logging.StreamHandler(self.stream)
        formatter = logging.Formatter("%(levelname)-7s %(asctime)s %(message)s (%(funcName)s)", datefmt="%H:%M:%S")
        self.handler.setFormatter(formatter)
        self.handler.setLevel(logging.INFO)
        self.logger.addHandler(self.handler)

    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc_value, traceback):
        log_file_name = "log"
        texts = bpy.data.texts
        text = texts[log_file_name] if log_file_name in texts else texts.new(log_file_name)
        text.clear()
        text.write(self.stream.getvalue())

        self.logger.removeHandler(self.handler)
        self.stream.close()

class SettingPMX():

    def __init__(self):
        logger.info("start")
        logger.info("end")

    def execute(self):
        logger.info("start")

        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        # bpy.ops.screen.delete({'screen': bpy.data.screens["Animation"]})
        bpy.ops.screen.delete({'screen': bpy.data.screens["3D View Full"]})
        bpy.ops.screen.delete({'screen': bpy.data.screens["Game Logic"]})
        bpy.ops.screen.delete({'screen': bpy.data.screens["Motion Tracking"]})
        bpy.ops.screen.delete({'screen': bpy.data.screens["Video Editing"]})
        bpy.context.window.screen = bpy.data.screens['Default']

        bpy.ops.brush.curve_preset(shape='MAX')

        self.scene_setting(bpy.context.scene)

        self.area_setting()

        logger.info("end")

    def scene_setting(self, scene):
        scene.unit_settings.system = 'IMPERIAL'
        scene.unit_settings.scale_length = 409/900
        scene.render.engine = 'CYCLES'
        scene.render.tile_x = 512
        scene.render.tile_y = 512
        scene.cycles.device = 'GPU'
        scene.cycles.feature_set = 'EXPERIMENTAL'

    def area_setting(self):
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    override = bpy.context.copy()
                    override["window"] = bpy.context.window
                    override["screen"] = screen
                    override["area"] = area
                    bpy.ops.view3d.view_persportho(override)

                    for space in area.spaces:
                        space.use_occlude_geometry = False
                        space.lens = 50

if __name__ == "__main__":
    with LoggingToTextContext(logger):
        SettingPMX().execute()
