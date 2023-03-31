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

bl_info = {
    "name": "JSBSim to Blender",
    "author": "RenanMsV",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "File > Import",
    "description": "Load and visualize aircraft FDM metrics from JSBSim XML files inside Blender",
    "category": "Import-Export",
    "doc_url": ("http://wiki.flightgear.org/"),
    "tracker_url": "https://github.com/RenanMsV/JSBSim2Blender/issues"
}


import bpy
import xml.etree.ElementTree as ET
from os import path

from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator

class JSBSim:
    def __init__(self, filepath):
        print("Importing JSBSim FDM from file:", filepath)
        self.filepath = filepath
        self.filename = path.basename(filepath).split('.xml')[0]
        self.root = ET.parse(filepath).getroot()
        self.unique_id, self.collection = self.get_root_collection_and_id()
        self.unit_system, self.unit_scale_length, self.unit_rotation_mode = self.get_unit_system()
        self.begin_parsing()

    def plot(self, name, position, collection_name, mesh_type = "SPHERE"):
        bpy.ops.object.empty_add(type = mesh_type, location = position)
        active_object = bpy.context.active_object
        active_object.name = f"{name} - {self.unique_id}"
        active_object.scale = (0.25, 0.25, 0.25)
        # cone must be pointing forward. later it could point to the actual orientation of the engine
        if mesh_type == "CONE":
            active_object.rotation_euler = (0, 0, 1.5707963267948966)
        active_object.users_collection[0].objects.unlink(active_object)
        collection = self.get_collection(collection_name)
        collection.objects.link(active_object)
        return active_object

    def get_unit_system(self):
        scene = bpy.context.scene
        unit_settings = scene.unit_settings
        return unit_settings.system, unit_settings.scale_length, unit_settings.system_rotation

    def get_root_collection_and_id(self):
        scene_collection = bpy.context.scene.collection
        children = scene_collection.children
        target_collection_name = None
        unique_id = None
        def find_children(name, children):
            for child in children:
                if child.name == name:
                    return child
            return None
        for index in range(999):
            name = f"JSBSim - [{self.filename} ({index})]"
            if find_children(name, children):
                continue
            else:
                target_collection_name = name
                unique_id = f"[{self.filename} ({index})]"
                break
        new_collection = bpy.data.collections.new(target_collection_name)
        scene_collection.children.link(new_collection)
        return unique_id, new_collection

    def get_collection(self, name):
        target_collection_name = f"{name} - {self.unique_id}"
        target_collection = None
        for collection in self.collection.children:
            if collection.name == target_collection_name:
                target_collection = collection
                break
        if target_collection is not None:
            return target_collection
        else:
            new_collection = bpy.data.collections.new(target_collection_name)
            self.collection.children.link(new_collection)
            return new_collection

    def get_xyz(self, element):
        x = float(element.find('x').text.strip())
        y = float(element.find('y').text.strip())
        z = float(element.find('z').text.strip())
        return x, y, z

    def get_locations(self, element):
        result = {}
        index = 0
        for location in element.findall('location'):
            name = location.get('name')
            unit = location.get('unit')
            x, y, z = self.get_xyz(location)
            x = self.convert_unit(x, unit)
            y = self.convert_unit(y, unit)
            z = self.convert_unit(z, unit)
            result[f"{name} ({str(index)})"] = {"name": name, "unit": unit, "xyz": (x, y, z)}
            index += 1
        return result
    
    def convert_unit(self, value, unit_from):
        scale = 1
        if unit_from == "IN":
            scale = 0.0254
        elif unit_from == "FT":
            scale = 0.3048
        elif unit_from == "M":
            pass
        if self.unit_scale_length == scale:
            return value
        else:
            return value * scale

    def begin_parsing(self):
        self.parse_metrics()
        self.parse_mass_balance()
        self.parse_ground_reactions()
        self.parse_external_reactions()
        self.parse_propulsion()

    def parse_metrics(self):
        metrics = self.root.find("metrics")
        locations = self.get_locations(metrics)
        for _, location in locations.items():
            self.plot(location["name"], location["xyz"], "Metrics")

    def parse_mass_balance(self):
        mass_balances = self.root.find("mass_balance")
        for _, location in self.get_locations(mass_balances).items(): 
            self.plot(location["name"], location["xyz"], "Mass Balance") # get and plot CG
        for pointmass in mass_balances.findall("pointmass"):
            pointmass_name = pointmass.get("name")
            weight_unit = pointmass.find("weight").get("unit")
            weight = pointmass.find("weight").text.strip()
            locations = self.get_locations(pointmass)
            for _, location in locations.items():
                self.plot(f"{pointmass_name} ({location['name']} - {weight} {weight_unit})", location["xyz"], "Mass Balance")

    def parse_ground_reactions(self):
        ground_reactions = self.root.find("ground_reactions")
        for contact in ground_reactions.findall("contact"):
            contact_name = contact.get("name")
            contact_type = contact.get("type")
            locations = self.get_locations(contact)
            for _, location in locations.items():
                self.plot(f"{contact_name} ({contact_type})", location["xyz"], "Ground Reactions")

    def parse_external_reactions(self):
        external_reactions = self.root.find("external_reactions")
        for force in external_reactions.findall("force"):
            force_name = force.get("name")
            force_frame = force.get("frame")
            locations = self.get_locations(force)
            for _, location in locations.items():
                self.plot(f"{force_name} ({force_frame})", location["xyz"], "External Reactions")

    def parse_propulsion(self):
        propulsions = self.root.find("propulsion")
        for engine in propulsions.findall("engine"):
            engine_file = engine.get("file")
            locations = self.get_locations(engine)
            engine_object = None
            for _, location in locations.items():
                engine_object = self.plot(f"ENGINE - {engine_file}", location["xyz"], "Propulsion", "CONE")
                thruster = engine.find("thruster")
                thruster_file = thruster.get("file")
                locations = self.get_locations(thruster)
                for _, location in locations.items():
                    thruster_object = self.plot(f"THRUSTER - {thruster_file}", location["xyz"], "Propulsion")
                    thruster_object.parent = engine_object
        for tank in propulsions.findall("tank"):
            tank_type = tank.get("type")
            tank_number = tank.get("number")
            locations = self.get_locations(tank)
            capacity_unit = tank.find("capacity").get("unit")
            capacity = tank.find("capacity").text.strip()
            for _, location in locations.items():
                self.plot(f"TANK ({tank_number} - {tank_type} - {capacity} {capacity_unit})", location["xyz"], "Propulsion", "CUBE")

class ImportJSBSim(Operator, ImportHelper):
    bl_idname = "import_scene.jsbsim"
    bl_label = "Import JSBSim"
    bl_description = "Load and visualize aircraft FDM metrics from JSBSim XML files inside Blender"

    filename_ext = ".xml"

    def execute(self, context):
        jsbInstance = JSBSim(self.filepath)
        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator(ImportJSBSim.bl_idname, text="JSBSim Flight Dynamics Model (.xml)")

def register():
    bpy.utils.register_class(ImportJSBSim)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(ImportJSBSim)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
