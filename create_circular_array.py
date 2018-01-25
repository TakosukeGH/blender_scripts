import bpy
import io
import logging
import math
import numpy as np

logger = logging.getLogger("circular_array")

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

class CircularArray():
    selected_object = None
    selected_objects = None
    base_empty = None
    pivot_empty = None
    array_modifier = None

    index_axis_dict = {0: "x", 1: "y", 2: "z"}
    axis_index_dict = {v:k for k, v in index_axis_dict.items()}

    def __init__(self):
        logger.info("start")

        self.size = 0.01
        self.axis = "z"
        self.obj_axis = "x"
        self.rotation_axis = "x"
        self.angle = 60.0
        self.layers = self.create_layers(0)

        logger.info("end")

    def execute(self):
        logger.info("start")

        self.get_layers()
        self.get_selected_object()
        if not self.selected_object:
            return
        self.get_view_axis()
        self.get_axis()
        self.get_rotation_axis()
        self.set_lock()
        self.add_base_empty()
        self.add_handle_empty()
        self.add_object_empty()
        self.add_rotation_empty()
        self.add_pivot_empty()
        self.add_constratint()

        logger.info("end")

    def get_layers(self):
        active_layer_index = bpy.context.scene.active_layer

        layer_index = (active_layer_index + 10) % 20
        self.layers = self.create_layers(layer_index)

    def get_selected_object(self):
        logger.info("start")
        if not bpy.context.object:
            return
        self.selected_object = bpy.context.object
        self.selected_objects = bpy.context.selected_objects
        self.selected_object_location = self.selected_object.location.copy()

        logger.info("end")

    def get_view_axis(self):
        lock_location = self.selected_object.lock_location
        if lock_location[0] == True:
            self.axis = "x"
        elif lock_location[1] == True:
            self.axis = "y"
        else:
            self.axis = "z"

        logger.debug(self.axis)

    def get_axis(self):
        loc_array = [self.selected_object_location.x, self.selected_object_location.y, self.selected_object_location.z]
        max_index = np.argmax(loc_array)
        logger.debug(max_index)

        self.obj_axis = self.index_axis_dict[max_index]

    def get_rotation_axis(self):
        exclusion_list = [self.axis, self.obj_axis]

        if "x" not in exclusion_list:
            self.rotation_axis = "x"
        elif "y" not in exclusion_list:
            self.rotation_axis = "y"
        else:
            self.rotation_axis = "z"

    def set_lock(self):
        for selected_object in self.selected_objects:
            selected_object.lock_location = (True, True, True)
            selected_object.lock_rotation = (True, True, True)
            selected_object.lock_scale = (True, True, True)

    def add_base_empty(self):
        bpy.ops.object.empty_add(type='SPHERE', location=(0.0,0.0,0.0), radius=self.size, layers=self.layers)
        self.base_empty = bpy.context.object
        self.base_empty.name = "base_empty"
        self.base_empty.show_x_ray = True

    def add_handle_empty(self):
        rotation = self.get_rotation()

        bpy.ops.object.empty_add(type='CIRCLE', location=(0.0,0.0,0.0), radius=self.size*2, rotation=rotation, layers=self.layers)
        self.handle_empty = bpy.context.object
        self.handle_empty.name = "handle_empty"
        self.handle_empty.show_x_ray = True

        self.handle_empty.lock_location = (True, True, True)
        self.handle_empty.lock_rotation = self.get_lock_rotation()
        self.handle_empty.lock_scale = (True, True, True)

        # bpy.ops.object.constraint_add(type='CHILD_OF')
        # child_of_const = self.handle_empty.constraints.values()[0]
        child_of_const = self.handle_empty.constraints.new(type='CHILD_OF')
        child_of_const.target = self.base_empty

    def add_object_empty(self):
        bpy.ops.object.empty_add(type='SPHERE', radius=self.size, location=self.selected_object_location, layers=self.layers)
        self.object_empty = bpy.context.object
        self.object_empty.name = "object_empty"
        self.object_empty.show_x_ray = True

        self.object_empty.lock_location = self.get_lock_location()
        self.object_empty.lock_rotation = (True, True, True)
        self.object_empty.lock_scale = (True, True, True)

        # bpy.ops.object.constraint_add(type='CHILD_OF')
        # child_of_const = self.object_empty.constraints.values()[0]
        child_of_const = self.object_empty.constraints.new(type='CHILD_OF')
        child_of_const.target = self.base_empty

    def add_rotation_empty(self):
        bpy.ops.object.empty_add(type='CIRCLE', radius=self.size*2, location=(0.0,0.0,0.0), layers=self.layers)
        self.rotation_empty = bpy.context.object
        self.rotation_empty.name = "rotation_empty"
        self.rotation_empty.show_x_ray = True

        self.rotation_empty.lock_location = (True, True, True)
        self.rotation_empty.lock_rotation = self.get_lock(self.rotation_axis)
        self.rotation_empty.lock_scale = (True, True, True)

        # bpy.ops.object.constraint_add(type='CHILD_OF')
        # child_of_const = self.rotation_empty.constraints.values()[0]
        child_of_const = self.rotation_empty.constraints.new(type='CHILD_OF')
        child_of_const.target = self.object_empty

    def add_pivot_empty(self):
        bpy.ops.object.empty_add(type='PLAIN_AXES', radius=self.size, location=self.selected_object_location, layers=self.layers)
        self.pivot_empty = bpy.context.object
        self.pivot_empty.name = "pivot_empty"
        self.pivot_empty.show_x_ray = True
        # self.pivot_empty.hide_select = True

        self.pivot_empty.lock_location = (True, True, True)
        self.pivot_empty.lock_rotation = (True, True, True)
        self.pivot_empty.lock_scale = (True, True, True)

        # bpy.ops.object.constraint_add(type='CHILD_OF')
        # child_of_const = self.pivot_empty.constraints.values()[0]
        child_of_const = self.pivot_empty.constraints.new(type='CHILD_OF')
        child_of_const.target = self.handle_empty

        self.add_location_driver()
        self.add_rotation_driver()

    def add_location_driver(self):
        fcurve = self.pivot_empty.driver_add("location", self.get_location_index())
        driver = fcurve.driver
        driver_value = driver.variables.new()
        driver_target = driver_value.targets.values()[0]
        driver_target.id = self.object_empty
        driver_target.data_path = "location[" + str(self.get_location_index())  + "]"
        driver.expression = driver_value.name

    def add_rotation_driver(self):
        fcurve = self.pivot_empty.driver_add("rotation_euler", self.axis_index_dict[self.rotation_axis])
        driver = fcurve.driver
        driver_value = driver.variables.new()
        driver_target = driver_value.targets.values()[0]
        driver_target.id = self.rotation_empty
        driver_target.data_path = "rotation_euler[" + str(self.axis_index_dict[self.rotation_axis])  + "]"
        driver.expression = driver_value.name

    def add_constratint(self):
        # self.select_object(self.selected_object)

        for selected_object in self.selected_objects:
            selected_object.location = (0.0, 0.0, 0.0)

            # bpy.ops.object.constraint_add(type='CHILD_OF')
            # child_of_const = self.selected_object.constraints.values()[0]
            child_of_const = selected_object.constraints.new(type='CHILD_OF')
            child_of_const.target = self.rotation_empty

            array_modifier = selected_object.modifiers.new("Array", type='ARRAY')
            array_modifier.use_relative_offset = False
            array_modifier.relative_offset_displace = (0.0, 0.0, 0.0)
            array_modifier.use_object_offset = True
            array_modifier.offset_object = self.pivot_empty

            self.add_array_driver(selected_object, array_modifier)

    def add_array_driver(self, obj, array_modifier):
        fcurve = obj.driver_add("modifiers[\"" + array_modifier.name + "\"].count")
        driver = fcurve.driver
        driver_value = driver.variables.new()
        driver_target = driver_value.targets.values()[0]
        driver_target.id = self.handle_empty
        driver_target.data_path = "rotation_euler[" + str(self.get_axis_index())  + "]"
        # driver.expression = "2*pi/" + driver_value.name
        driver.expression = "round(2*pi/" + driver_value.name + ")"

    def create_layers(self, layer_number):
        layers = [False] * 20
        layers[layer_number] = True
        return layers

    def get_rotation(self):
        if self.axis == "x":
            return (math.radians(self.angle), 0.0, 0.0)
        elif self.axis == "y":
            return (0.0, math.radians(self.angle), 0.0)
        else:
            return (0.0, 0.0, math.radians(self.angle))

    def get_lock_rotation(self):
        if self.axis == "x":
            return (False, True, True)
        elif self.axis == "y":
            return (True, False, True)
        else:
            return (True, True, False)

    def get_lock_location(self):
        if self.obj_axis == "x":
            return (False, True, True)
        elif self.obj_axis == "y":
            return (True, False, True)
        else:
            return (True, True, False)

    def get_lock(self, axis):
        lock = [True, True, True]
        lock[self.axis_index_dict[axis]] = False
        return tuple(lock)

    def get_axis_index(self):
        if self.axis == "x":
            return 0
        elif self.axis == "y":
            return 1
        else:
            return 2

    def get_location_index(self):
        if self.obj_axis == "x":
            return 0
        elif self.obj_axis == "y":
            return 1
        else:
            return 2

    def select_object(self, obj):
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True
        bpy.context.scene.objects.active = obj

if __name__ == "__main__":
    with LoggingToTextContext(logger):
        CircularArray().execute()
