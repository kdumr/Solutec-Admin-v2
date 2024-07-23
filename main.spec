# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# O nome do seu script
a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('assets/*', 'assets'),  # Inclua todos os arquivos da pasta 'assets'
        ('icon.ico', '.'),       # Inclua o ícone
        ('version.json', '.'),   # Inclua o arquivo de versão
        ('update.exe', '.')      # Inclua o executável de atualização
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='seu_arquivo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Use True se quiser um console
    windowed=True,  # Use False se não quiser uma janela
    icon='icon.ico'
)
