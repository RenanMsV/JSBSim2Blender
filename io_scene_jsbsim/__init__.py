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

from bpy.utils import register_class, unregister_class
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator, TOPBAR_MT_file_import
from bpy.props import StringProperty, FloatProperty, BoolProperty

from .jsbsim import JSBSim


class ImportJSBSim(Operator, ImportHelper):
    bl_idname = 'import_scene.jsbsim'
    bl_label = 'Import JSBSim'
    bl_description = 'Import and visualize JSBSim FDM aircraft XML metrics in Blender'
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    filename_ext = '.xml'
    filter_glob: StringProperty(
        default='*.xml',        # noqa: F722
        options={'HIDDEN'}      # noqa: F821
    )  # type: ignore

    # Per import settings
    plot_scale: FloatProperty(
        name='Scale factor',                                    # noqa: F722
        description='Controls the size of plotted objects',     # noqa: F722
        default=0.25,
        min=0.01,
        max=10.0
    )  # type: ignore

    plot_names: BoolProperty(
        name='Show names',                                              # noqa: F722
        description='Display plotted object names in the viewport',     # noqa: F722
        default=False
    )  # type: ignore

    plot_axes: BoolProperty(
        name='Show axes',                                               # noqa: F722
        description='Display axes of plotted objects in the viewport',  # noqa: F722
        default=False
    )  # type: ignore

    thrs_auto_parent: BoolProperty(
        name='Thrusters',                                               # noqa: F821
        description='Automatically parent Thrusters to their Engines',  # noqa: F722
        default=True
    )  # type: ignore

    include_metrics: BoolProperty(
        name='Metrics',                                          # noqa: F821
        description='Select this to include it when importing',  # noqa: F722
        default=True
    )  # type: ignore

    include_mass_balance: BoolProperty(
        name='Mass Balance',                                     # noqa: F722
        description='Select this to include it when importing',  # noqa: F722
        default=True
    )  # type: ignore

    include_ground_reactions: BoolProperty(
        name='Ground Reactions',                                 # noqa: F722
        description='Select this to include it when importing',  # noqa: F722
        default=True
    )  # type: ignore

    include_external_reactions: BoolProperty(
        name='External Reactions',                               # noqa: F722
        description='Select this to include it when importing',  # noqa: F722
        default=True
    )  # type: ignore

    include_propulsion: BoolProperty(
        name='Propulsion',                                       # noqa: F821
        description='Select this to include it when importing',  # noqa: F722
        default=True
    )  # type: ignore

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        def draw_props_panel(panel_id, label_text, props):
            '''Draw a collapsible settings panel for operator properties.'''
            header, body = layout.panel(panel_id, default_closed=False)
            header.label(text=label_text)
            if body:
                for prop in props:
                    body.prop(self, prop)

        panels = [
            (
                'JSBSim_FDM_import_include',
                'Include',
                [
                    'include_metrics',
                    'include_mass_balance',
                    'include_ground_reactions',
                    'include_external_reactions',
                    'include_propulsion'
                ]
            ),
            (
                'JSBSim_FDM_import_plot_objects',
                'Plotted Objects',
                [
                    'plot_scale',
                    'plot_names',
                    'plot_axes'
                ]
            ),
            (
                'JSBSim_FDM_import_parenting',
                'Parenting',
                ['thrs_auto_parent']
            )
        ]

        for panel_id, label, props in panels:
            draw_props_panel(panel_id, label, props)

    def execute(self, context):
        if not self.filepath or not self.filepath.lower().endswith('.xml'):
            self.report({'ERROR'}, 'Please select a valid XML file')
            return {'CANCELLED'}
        settings = {
            'plot_scale': self.plot_scale,
            'plot_names': self.plot_names,
            'plot_axes': self.plot_axes,
            'thrs_auto_parent': self.thrs_auto_parent,
            'include_metrics': self.include_metrics,
            'include_mass_balance': self.include_mass_balance,
            'include_ground_reactions': self.include_ground_reactions,
            'include_external_reactions': self.include_external_reactions,
            'include_propulsion': self.include_propulsion
        }
        self.jsbInstance = JSBSim(self.filepath, **settings)  # init import operator
        return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(
        ImportJSBSim.bl_idname,
        text='JSBSim Flight Dynamics Model (.xml)'
    )


def register():
    register_class(ImportJSBSim)
    TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    unregister_class(ImportJSBSim)
    TOPBAR_MT_file_import.remove(menu_func_import)
