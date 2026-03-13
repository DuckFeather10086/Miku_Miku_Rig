# MikuMikuRig base: shared utilities and panel base
import bpy


def alert_error(title, message):
    """Show error popup; use print in headless to avoid crash."""
    is_headless = bpy.app.background or not bpy.context.area
    if is_headless:
        print(f"[{title}] {message}")
    else:
        try:
            def draw(self, context):
                self.layout.label(text=str(message))
            if bpy.context.window_manager:
                bpy.context.window_manager.popup_menu(draw, title=title, icon='ERROR')
            else:
                print(f"[{title}] {message}")
        except Exception:
            print(f"[{title}] {message}")


class Mmr_Panel_Base(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MMR"
    bl_context = "objectmode"


def register():
    pass


def unregister():
    pass
