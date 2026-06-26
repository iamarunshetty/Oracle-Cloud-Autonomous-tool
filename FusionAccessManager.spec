# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Oracle Fusion Access Manager
# Build: pyinstaller FusionAccessManager.spec

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all PySide6 plugins (needed for Windows packaging)
hiddenimports = collect_submodules("PySide6") + [
    "openpyxl",
    "pandas",
    "reportlab",
    "dotenv",
    "app",
    "app.config",
    "app.models",
    "app.services",
    "app.storage",
    "app.ui",
    "app.security",
]

datas = [
    ("templates", "templates"),
    (".env.example", "."),
]
datas += collect_data_files("PySide6")
datas += collect_data_files("reportlab")

a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=[],
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
    [],
    name="FusionAccessManager",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,   # windowed application – no console window
    onefile=True,
    icon=None,       # replace with path to .ico file when available
)
