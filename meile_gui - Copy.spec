# -*- mode: python ; coding: utf-8 -*-
import sys
#sys.setrecursionlimit(5000)
from PyInstaller.utils.hooks import collect_all
from kivy_deps import sdl2, glew

datas = [('src/fonts', '../fonts'), ('src/awoc/datum/', 'datum'), ('src/utils/fonts/', '../utils/fonts'), ('src/utils/coinimg/', '../utils/coinimg'), ('src/imgs/', '../imgs'), ('src/kv/', '../kv'), ('src/conf/config/', 'config'), ('src/bin/', '../bin')]
binaries = []
hiddenimports = []
tmp_ret = collect_all('stripe')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('kivy_garden')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


block_cipher = None


a = Analysis(
    ['src\\main\\meile_gui.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
	*[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    name='meile_gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.icns'],
)
