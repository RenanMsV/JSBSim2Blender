# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator

from .jsbsim import JSBSim

class ImportJSBSim(Operator, ImportHelper):
    bl_idname = 'import_scene.jsbsim'
    bl_label = 'Import JSBSim'
    bl_description = 'Import and visualize JSBSim FDM aircraft XML metrics in Blender'
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = '.xml'
    filter_glob: bpy.props.StringProperty(default="*.xml", options={'HIDDEN'}) # type: ignore

    def execute(self, context):
        if not self.filepath or not self.filepath.lower().endswith(".xml"):
            self.report({'ERROR'}, "Please select a valid XML file")
            return {'CANCELLED'}
        self.jsbInstance = JSBSim(self.filepath)  # store in operator instance
        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator(ImportJSBSim.bl_idname, text='JSBSim Flight Dynamics Model (.xml)')

def register():
    bpy.utils.register_class(ImportJSBSim)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(ImportJSBSim)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
