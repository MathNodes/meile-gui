from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': [], 'excludes': []}

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('.\\\\src\\\\main\\\\meile_gui.py', base=base, target_name = 'meile')
]

setup(name='Meile',
      version = '1.4.0',
      description = 'Meile dVPN Powered by the Sentinel Network',
      options = {'build_exe': build_options},
      executables = executables)
