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

import os
import sys
import importlib
import bpy
from bpy.types import Addon


def test_python_installed():
    '''Verify Blender’s internal Python interpreter works correctly.'''
    print('\nPython[Blender] version:', sys.version)
    assert sys.version_info >= (3, 10), 'Expected Python 3.10+'


def test_bpy_available():
    '''Ensure bpy API is loaded and functional.'''
    print('\nBlender bpy version:', bpy.app.version_string)
    assert hasattr(bpy.app, 'version')
    assert isinstance(bpy.app.version, tuple)
    assert bpy.app.version >= (4, 2, 0), 'Expected bpy 4.2+'
    assert bpy.app.version_cycle == 'release', 'Expected Blender release build'


def test_extension_working():
    '''Check that the extension is installed, importable, and operational.'''
    extension_name = 'io_scene_jsbsim'
    extension_internal_id = f'bl_ext.user_default.{extension_name}'

    # Verify that something is loaded
    addons = bpy.context.preferences.addons
    assert addons is not None, 'No extensions found in Blender context'

    # Locate the installed extension
    addon = addons.get(extension_internal_id)
    assert addon is not None, \
        f'Extension {extension_name} not installed or not enabled'
    assert isinstance(addon, Addon), f'Expected Addon instance, got {type(addon)}'
    assert isinstance(addon.module, str), 'Expected addon.module to be a string'

    # Dynamically import the extension module
    mod = importlib.import_module(addon.module)
    print('\nModule imported:', mod)
    print(f'Addon file path: {mod.__file__}')
    assert hasattr(mod, '__file__') and os.path.exists(mod.__file__), \
        'Addon file missing or invalid'

    # JSBSim class check as it must exist
    assert hasattr(mod, 'JSBSim'), 'JSBSim class is required but missing'

    # Run a simple XML import test
    settings = {
        'plot_scale': 0.25,
        'plot_names': False,
        'plot_axes': False,
        'thrs_auto_parent': True,
        'include_metrics': True,
        'include_mass_balance': True,
        'include_ground_reactions': True,
        'include_external_reactions': True,
        'include_propulsion': True,
    }

    xml_path = './tests/c172p.xml'
    assert os.path.exists(xml_path), f'Test XML not found: {xml_path}'

    print('Testing JSBSim XML import...')
    jsbsim = mod.JSBSim(xml_path, **settings)
    assert hasattr(jsbsim, 'import_ok'), 'JSBSim instance missing import_ok attribute'
    assert jsbsim.import_ok is True, 'JSBSim failed to import XML correctly'
