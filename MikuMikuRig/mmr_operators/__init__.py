import bpy

from . import extra

Model_list = [extra]

def register():
    for Model in Model_list:
        for Class in Model.Class_list:
            bpy.utils.register_class(Class)

def unregister():
    for Model in Model_list:
        for Class in Model.Class_list:
            bpy.utils.unregister_class(Class)