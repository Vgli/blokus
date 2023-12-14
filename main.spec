# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['pygame_menu']
hiddenimports += collect_submodules('src.bot')
hiddenimports += collect_submodules('src.controllers')
hiddenimports += collect_submodules('src.events')
hiddenimports += collect_submodules('src.views')
hiddenimports += collect_submodules('src.reward')
hiddenimports += collect_submodules('src.menu')
hiddenimports += collect_submodules('src.objects')


a = Analysis(
    ['C:/Users/Admin/Documents/GitHub/blokus/main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:/Users/Admin/Documents/GitHub/blokus/src', 'src/'), ('C:/Users/Admin/Documents/GitHub/blokus/sprites', 'sprites/'), ('C:/Users/Admin/Documents/GitHub/blokus/data', 'data/')],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
