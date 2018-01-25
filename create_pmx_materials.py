import bpy
import io
import logging
import math
import numpy as np

logger = logging.getLogger("pmx_materials")

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

class CreatePMXMaterials():
    def __init__(self):
        logger.info("start")

        self.arm = None
        self.objects = []
        self.materials = []
        self.pmx_materials = None

        logger.info("end")

    def execute(self):
        logger.info("start")

        self.get_armature()
        self.get_objects()
        self.get_materials()
        self.create_object()
        self.set_materials()

        logger.info("end")

    def get_armature(self):
        self.arm = bpy.context.object.data
        if self.arm is None:
            logger.error("arm is None")
        else:
            logger.info("end")

    def get_objects(self):
        for obj in bpy.data.objects:
            if obj.find_armature() is None:
                continue

            if obj.find_armature().name == self.arm.name:
                self.objects.append(obj)

    def get_materials(self):
        for obj in self.objects:
            for material in obj.data.materials:
                if material not in self.materials:
                    self.materials.append(material)

    def create_object(self):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, size=0.2, location=(2.0, 0.0, 0.0))
        bpy.ops.object.shade_smooth()
        self.pmx_materials = bpy.context.object

        self.pmx_materials.name = "pmx_materials"
        self.pmx_materials.lock_rotation = (True, True, True)
        self.pmx_materials.lock_scale = (True, True, True)
        self.pmx_materials.lock_location[1] = True
        self.pmx_materials.lock_location[2] = True

    def set_materials(self):
        for material in self.materials:
            self.pmx_materials.data.materials.append(material)

if __name__ == "__main__":
    with LoggingToTextContext(logger):
        CreatePMXMaterials().execute()
