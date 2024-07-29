# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all, collect_submodules, copy_metadata
from kivy_deps import sdl2, glew

#('C:\\Users\\freqn\\AppData\\Local\\Programs\\Python\\Python39\\Lib\\site-packages\\coincurve\\*', 'coincurve'),
datas = [('src\\kv', 'kv'), ('src\\imgs','imgs'), ('src\\awoc\\datum', 'datum'), ('src\\bin', 'bin'), ('src\\conf\\config', 'config'), ('src\\utils\\coinimg', 'utils\coinimg'), ('src\\utils\\fonts' , 'utils\\fonts'), ('src\\fonts', 'fonts')]
binaries = []
hiddenimports = []
tmp_ret = collect_all('bip_utils')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('mospy_wallet')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('sentinel_protobuf')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('sentinel_sdk')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('stripe')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('kivy_garden')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('coincurve')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
#tmp_ret = collect_all('cosmpy.protos.google')
#datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_submodules('cosmpy')
hiddenimports += tmp_ret
tmp_ret = collect_submodules('google')
hiddenimports += tmp_ret
#tmp_ret = copy_metadata('google')
#datas += tmp_ret
tmp_ret = copy_metadata('protobuf')
datas += tmp_ret

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
    noarchive=True,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    name='Meile',
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
    icon='C:\\Users\\freqn\\Projects\\Meile\\meile.ico',
)
