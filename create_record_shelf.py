import bpy
import logging
import io
import math
import random

logger = logging.getLogger("record_shelf")

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

class CreateRecordShelf():

    def __init__(self):
        logger.info("start")

        self.record_data = None

        logger.info("end")

    def execute(self):
        logger.info("start")

        self.record_data = Record().create_data()

        shelf = Shelf()
        shelf.create(self.record_data)

        logger.info("end")

class Shelf():
    def __init__(self):
        self.scale = Record.scale
        self.x = 0.0
        self.y = 0.0
        self.size = 0.315
        self.obj = None

    def create(self, record_data):
        bpy.ops.object.empty_add(type='IMAGE', radius=self.size / self.scale)
        self.obj = bpy.context.object

        self.create_records(record_data)

    def create_records(self, record_data):
        location = 0.0
        location_def = 0.0
        for i in range(random.randint(10,20)):
            record = Record()

            location += random.uniform(Record.thickness,Record.thickness + 2.0 / self.scale)
            record.create(record_data, (location / self.scale, 0.0, 0.0))

            child_of_const = record.obj.constraints.new(type='CHILD_OF')
            child_of_const.target = self.obj


class Record():
    scale = bpy.context.scene.unit_settings.scale_length
    size = 0.315
    thickness = 0.004

    def __init__(self):
        self.obj = None

    def create_data(self):
        bpy.ops.mesh.make_wplane()
        obj = bpy.context.object

        data = obj.data
        data.name = "record"
        data.WPlane.size[0] = self.size / self.scale
        data.WPlane.size[1] = self.size / self.scale
        data.WPlane.centered = False

        bpy.data.objects.remove(obj, True)

        return data

    def create(self, data, location):
        self.obj = bpy.data.objects.new("record", data)
        bpy.context.scene.objects.link(self.obj)

        self.obj.location = location
        self.obj.rotation_euler[1] = math.radians(-90)

        solidify_modifier = self.obj.modifiers.new("Solidify", type='SOLIDIFY')
        solidify_modifier.thickness = self.thickness / self.scale




if __name__ == "__main__":
    with LoggingToTextContext(logger):
        CreateRecordShelf().execute()
