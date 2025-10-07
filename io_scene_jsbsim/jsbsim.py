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

from os import path
import time
import xml.etree.ElementTree as ET
import bpy


class JSBSim:
    def __init__(
        self,
        filepath,
        plot_scale,
        plot_names,
        plot_axes,
        thrs_auto_parent,
        include_metrics,
        include_mass_balance,
        include_ground_reactions,
        include_external_reactions,
        include_propulsion
    ):
        self.filepath = filepath
        self.filename = path.basename(filepath).split('.xml')[0]
        # Collect import operator settings
        self.plot_scale = plot_scale
        self.plot_names = plot_names
        self.plot_axes = plot_axes
        self.thrs_auto_parent = thrs_auto_parent
        self.include_metrics = include_metrics
        self.include_mass_balance = include_mass_balance
        self.include_ground_reactions = include_ground_reactions
        self.include_external_reactions = include_external_reactions
        self.include_propulsion = include_propulsion
        # Parse, display and benchmark
        self.root = ET.parse(filepath).getroot()
        self.unique_id, self.collection = self.get_root_collection_and_id()
        (
            self.unit_system,
            self.unit_scale_length,
            self.unit_rotation_mode,
        ) = self.get_unit_system()
        self.elapsed_start_import = time.perf_counter()
        self.begin_parsing()
        self.elapsed_finish_import = time.perf_counter()
        self.elapsed_import_ms = (
            self.elapsed_finish_import - self.elapsed_start_import
        ) * 1000
        print(
            f'Imported JSBSim FDM from file: {filepath} '
            f'in {self.elapsed_import_ms:.3f} ms'
        )
        self.import_ok = True

    def plot(self, name, position, collection_name, mesh_type='SPHERE'):
        bpy.ops.object.empty_add(type=mesh_type, location=position)
        active_object = bpy.context.active_object
        active_object.name = f'{name} - {self.unique_id}'
        active_object.scale = (self.plot_scale, self.plot_scale, self.plot_scale)
        active_object.show_name = self.plot_names
        active_object.show_axis = self.plot_axes
        # cone must be pointing forward. later it could point to the
        # actual orientation of the engine
        if mesh_type == 'CONE':
            active_object.rotation_euler = (0, 0, 1.5707963267948966)
        active_object.users_collection[0].objects.unlink(active_object)
        collection = self.get_collection(collection_name)
        collection.objects.link(active_object)
        return active_object

    def get_unit_system(self):
        scene = bpy.context.scene
        unit_settings = scene.unit_settings
        return (
            unit_settings.system,
            unit_settings.scale_length,
            unit_settings.system_rotation
        )

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
            name = f'JSBSim - [{self.filename} ({index})]'
            if find_children(name, children):
                continue
            target_collection_name = name
            unique_id = f'[{self.filename} ({index})]'
            break
        new_collection = bpy.data.collections.new(target_collection_name)
        scene_collection.children.link(new_collection)
        return unique_id, new_collection

    def get_collection(self, name):
        target_collection_name = f'{name} - {self.unique_id}'
        target_collection = None
        for collection in self.collection.children:
            if collection.name == target_collection_name:
                target_collection = collection
                break
        if target_collection is not None:
            return target_collection
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
            result[f'{name} ({str(index)})'] = {
                'name': name,
                'unit': unit,
                'xyz': (x, y, z)
            }
            index += 1
        return result

    def convert_unit(self, value, unit_from):
        scales = {
            'IN': 0.0254,
            'FT': 0.3048,
            'M': 1.0,
        }
        if unit_from not in scales:
            raise ValueError(f'Unsupported unit: {unit_from}')
        scale = scales[unit_from]
        # Convert to meters, then into Blender scene units
        return (value * scale) / self.unit_scale_length

    def get_tag_if_exists(self, tag_name, collection_name):
        self.get_collection(collection_name)
        tag = self.root.find(tag_name)
        if tag is None:
            print('JSBSim warning: Missing tag [', tag_name, ']')
        return tag

    def set_object_parent(self, obj, parent_obj, keep_global_transform=False):
        obj.parent = parent_obj
        if keep_global_transform:
            obj.matrix_parent_inverse = parent_obj.matrix_world.inverted()

    def begin_parsing(self):
        if self.include_metrics:
            self.parse_metrics()
        if self.include_mass_balance:
            self.parse_mass_balance()
        if self.include_ground_reactions:
            self.parse_ground_reactions()
        if self.include_external_reactions:
            self.parse_external_reactions()
        if self.include_propulsion:
            self.parse_propulsion()

    def parse_metrics(self):
        metrics = self.get_tag_if_exists('metrics', 'Metrics')
        if metrics is None:
            return
        locations = self.get_locations(metrics)
        for _, location in locations.items():
            self.plot(location['name'], location['xyz'], 'Metrics')

    def parse_mass_balance(self):
        mass_balances = self.get_tag_if_exists('mass_balance', 'Mass Balance')
        if mass_balances is None:
            return
        for _, location in self.get_locations(mass_balances).items():
            self.plot(
                location['name'],
                location['xyz'],
                'Mass Balance'
            )  # get and plot CG
        for pointmass in mass_balances.findall('pointmass'):
            pointmass_name = pointmass.get('name')
            weight_unit = pointmass.find('weight').get('unit')
            weight = pointmass.find('weight').text.strip()
            locations = self.get_locations(pointmass)
            for _, location in locations.items():
                self.plot(
                    f"{pointmass_name} ({location['name']} - {weight} {weight_unit})",
                    location['xyz'],
                    'Mass Balance'
                )

    def parse_ground_reactions(self):
        ground_reactions = self.get_tag_if_exists(
            'ground_reactions',
            'Ground Reactions'
        )
        if ground_reactions is None:
            return
        for contact in ground_reactions.findall('contact'):
            contact_name = contact.get('name')
            contact_type = contact.get('type')
            locations = self.get_locations(contact)
            for _, location in locations.items():
                self.plot(
                    f'{contact_name} ({contact_type})',
                    location['xyz'],
                    'Ground Reactions'
                )

    def parse_external_reactions(self):
        external_reactions = self.get_tag_if_exists(
            'external_reactions', 'External Reactions'
        )
        if external_reactions is None:
            return
        for force in external_reactions.findall('force'):
            force_name = force.get('name')
            force_frame = force.get('frame')
            locations = self.get_locations(force)
            for _, location in locations.items():
                self.plot(
                    f'{force_name} ({force_frame})',
                    location['xyz'],
                    'External Reactions'
                )

    def parse_propulsion(self):
        propulsions = self.get_tag_if_exists('propulsion', 'Propulsion')
        if propulsions is None:
            return
        # Draw engines
        for engine in propulsions.findall('engine'):
            engine_file = engine.get('file')
            locations = self.get_locations(engine)
            engine_object = None
            if len(locations):
                for _, location in locations.items():
                    engine_object = self.plot(
                        f'ENGINE - {engine_file}',
                        location['xyz'],
                        'Propulsion',
                        'CONE'
                    )
            else:
                engine_object = self.plot(
                    f'ENGINE - {engine_file} (missing location)',
                    (0, 0, 0),
                    'Propulsion',
                    'CONE'
                )
            # Draw engine thrusters
            thruster = engine.find('thruster')
            thruster_file = thruster.get('file')
            locations = self.get_locations(thruster)
            for _, location in locations.items():
                thruster_object = self.plot(
                    f'THRUSTER - {thruster_file}',
                    location['xyz'],
                    'Propulsion'
                )
                if self.thrs_auto_parent:
                    self.set_object_parent(
                        obj=thruster_object,
                        parent_obj=engine_object,
                        keep_global_transform=True
                    )
        # Draw fuel tanks
        for tank in propulsions.findall('tank'):
            tank_type = tank.get('type')
            tank_number = tank.get('number')
            locations = self.get_locations(tank)
            capacity_unit = tank.find('capacity').get('unit')
            capacity = tank.find('capacity').text.strip()
            for _, location in locations.items():
                self.plot(
                    f'TANK ({tank_number} - {tank_type} - {capacity} {capacity_unit})',
                    location['xyz'],
                    'Propulsion',
                    'CUBE'
                )
