import bpy
import collections
import io
import json
import logging

logger = logging.getLogger("create_rgb_morph_file")

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
        self.handler.setLevel(logging.DEBUG)
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

class CreateRGBMorphFile():

    def __init__(self):
        logger.info("start")

        self.file_name = "morph_data_stick.json"

        logger.info("end")

    def execute(self):
        logger.info("start")

        data_list = []
        data_list.append(("cyan",2,0)) # name, panel, index
        data_list.append(("magenta",3,1))
        data_list.append(("yellow",1,2))

        morphs = collections.OrderedDict()
        for name, panel, index in data_list:
            logger.debug(name)
            morphs[name] = self.create_morph(panel, index)

        jsonstring = json.dumps(morphs, ensure_ascii=False, indent=2, sort_keys=False)

        if self.file_name in bpy.data.texts:
            bpy.data.texts.remove(bpy.data.texts[self.file_name], do_unlink=True)

        text = bpy.data.texts.new(self.file_name)
        text.from_string(jsonstring)

        logger.info("end")

    def create_morph(self, panel, index):
        morph = {}

        morph["panel"] = panel #1:眉(左下) 2:目(左上) 3:口(右上) 4:その他(右下)  | 0:システム予約
        morph["type"] = 8
        morph["offsets"] = self.create_offsets(index)

        return morph

    def create_offsets(self, index):
        offsets = []
        offset = {}
        offset["material_name"] = "head"
        offset["offset_type"] = 1
        offset["diffuse"] = [0,0,0,0]
        offset["specular"] = [0,0,0]
        offset["power"] = 0
        offset["ambient"] = [0,0,0]
        offset["edge_size"] = 0
        offset["edge_color"] = [0,0,0,0]
        offset["texture"] = [0,0,0,0]
        offset["sphere"] = [0,0,0,0]
        offset["toon"] = [0,0,0,0]

        # offset["texture"][index] = -1
        offset["diffuse"][index] = -1
        offset["ambient"][index] = -1

        offsets.append(offset)
        return offsets

if __name__ == "__main__":
    with LoggingToTextContext(logger):
        CreateRGBMorphFile().execute()
