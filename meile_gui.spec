# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['src/main/meile_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('src/awoc/data/', 'data'), ('src/utils/fonts/', '../utils/fonts'), ('src/utils/coinimg/', '../utils/coinimg'), ('src/imgs/', '../imgs'), ('src/kv/', '../kv'), ('src/conf/config/', 'config'), ('src/bin/', '../bin')],
    hiddenimports=[],
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
    [],
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
)
