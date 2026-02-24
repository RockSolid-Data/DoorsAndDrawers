"""
cx_Freeze build configuration for Doors and Drawers.

Usage (via build_installer.bat or directly):
    python setup_cx_freeze.py build_exe          # build standalone exe
    python setup_cx_freeze.py bdist_msi          # build MSI installer
"""

import sys
import os
from cx_Freeze import setup, Executable

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, 'VERSION')) as _vf:
    VERSION = _vf.read().strip()

# ---------------------------------------------------------------------------
# Data files that must ship alongside the exe
# (source_path, destination_path_relative_to_build_dir)
# ---------------------------------------------------------------------------
_py_base = sys.base_prefix
include_files = [
    (os.path.join(BASE_DIR, 'templates'),   'templates'),
    (os.path.join(BASE_DIR, 'staticfiles'), 'staticfiles'),
    (os.path.join(BASE_DIR, 'static'),      'static'),
    (os.path.join(BASE_DIR, 'VERSION'),     'VERSION'),
    (os.path.join(_py_base, 'vcruntime140.dll'),   'vcruntime140.dll'),
    (os.path.join(_py_base, 'vcruntime140_1.dll'), 'vcruntime140_1.dll'),
]

# ---------------------------------------------------------------------------
# Python packages to freeze – explicit list so cx_Freeze doesn't miss any
# dynamically-imported Django / third-party modules
# ---------------------------------------------------------------------------
packages = [
    # Django framework
    'django',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.db.backends.sqlite3',
    'django.template',
    'django.templatetags',
    'django.core.management',

    # Third-party Django apps
    'widget_tweaks',
    'django_htmx',

    # WSGI server & static-file serving
    'waitress',
    'whitenoise',

    # PDF generation (xhtml2pdf + deps)
    'xhtml2pdf',
    'reportlab',
    'reportlab.graphics.barcode',
    'html5lib',
    'cssselect2',
    'tinycss2',
    'tinyhtml5',
    'pyphen',
    'pydyf',

    # Standard library modules that Django / Waitress import dynamically
    'encodings',
    'email',
    'html',
    'http',
    'xml',
    'xml.etree',
    'logging',
    'sqlite3',
    'decimal',
    'json',
    'multiprocessing',
    'argparse',

    # Project packages
    'DoorsAndDrawers',
    'core',
    'core.models',
    'core.views',
    'core.forms',
    'core.urls',
    'core.services',
    'core.templatetags',
    'core.migrations',
    'core.management',
    'scripts',
]

# ---------------------------------------------------------------------------
# Packages to exclude (trim bloat)
# ---------------------------------------------------------------------------
excludes = [
    'tkinter',
    'test',
    'unittest',
    'pip',
    'setuptools',
    'distutils',
    'Faker',
    'pydoc_data',
    'pydoc',
    'doctest',
]

# ---------------------------------------------------------------------------
# build_exe options
# ---------------------------------------------------------------------------
build_exe_options = {
    'packages':      packages,
    'excludes':      excludes,
    'include_files': include_files,
    'include_msvcr': False,
}

# ---------------------------------------------------------------------------
# Executables
# ---------------------------------------------------------------------------

# GUI executable – no console window (for end users)
gui_exe = Executable(
    script='launcher.py',
    base='gui',
    target_name='DoorsAndDrawers.exe',
    icon=None,                       # Replace with 'icon.ico' if available
    shortcut_name='Doors and Drawers',
    shortcut_dir='DesktopFolder',
)

# Debug executable – shows a console for troubleshooting
debug_exe = Executable(
    script='launcher.py',
    base='console',
    target_name='DoorsAndDrawers_Debug.exe',
)

# ---------------------------------------------------------------------------
# bdist_msi options – Start Menu shortcut
# (Desktop shortcut is handled by gui_exe's shortcut_name / shortcut_dir)
# ---------------------------------------------------------------------------
# MSI Shortcut table columns:
#   Shortcut, Directory_, Name, Component_, Target,
#   Arguments, Description, Hotkey, Icon_, IconIndex, ShowCmd, WkDir
shortcut_table = [
    (
        'StartMenuShortcut',
        'ProgramMenuFolder',
        'Doors and Drawers',
        'TARGETDIR',
        '[TARGETDIR]DoorsAndDrawers.exe',
        None,
        'Doors and Drawers - Order Management',
        None,
        None,
        None,
        None,
        'TARGETDIR',
    ),
]

bdist_msi_options = {
    'upgrade_code': '{8A5F4E2B-3C71-4D9A-B6E8-1F0A2D3E4C5B}',
    'add_to_path': False,
    'initial_target_dir': r'[ProgramFiles64Folder]\DoorsAndDrawers',
    'data': {
        'Shortcut': shortcut_table,
    },
}

# ---------------------------------------------------------------------------
# setup()
# ---------------------------------------------------------------------------
setup(
    name='DoorsAndDrawers',
    version=VERSION,
    description='Doors and Drawers - Order Management Desktop Application',
    author='Doors and Drawers',
    options={
        'build_exe':  build_exe_options,
        'bdist_msi':  bdist_msi_options,
    },
    executables=[gui_exe, debug_exe],
)
