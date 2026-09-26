# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

added_files = [
    ('templates', 'templates'),
    ('static', 'static'),
    ('staticfiles', 'staticfiles'),
    ('media', 'media'),
    ('app_icon.ico', '.'),
]

hidden_imports = [
    'waitress',
    'webview',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.db.backends.sqlite3',
    'accounts',
    'dashboard',
    'products',
    'customers',
    'suppliers',
    'sales',
    'purchases',
    'expenses',
    'services',
    'reports',
    'settings_app',
    'reportlab',
    'reportlab.platypus',
    'reportlab.lib.colors',
    'reportlab.lib.pagesizes',
    'reportlab.lib.units',
    'reportlab.lib.styles',
]

a = Analysis(
    ['desktop_main.py'],
    pathex=['.'],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
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
    [],
    exclude_binaries=True,
    name='SirajUPS_Software',
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
    icon='app_icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SirajUPS_Software',
)
