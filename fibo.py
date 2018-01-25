import bpy
import bmesh
import math

n = 500 # number of points
# c = 0.01 # scale factor

scale = 0.01
r_min = 0.0
r_max = 0.8

mesh = bpy.data.meshes.new(name="Spiral")
bm = bmesh.new()

for i in range(0, n):
    theta = i * math.radians(137.5)
    r = (r_min + r_max * i / n) * scale
    bm.verts.new((math.cos(theta) * r, math.sin(theta) * r, 0.0))

bm.to_mesh(mesh)
mesh.update()

from bpy_extras import object_utils
object_utils.object_data_add(bpy.context, mesh)

