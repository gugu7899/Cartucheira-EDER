# -*- mode: python ; coding: utf-8 -*-
a=Analysis(['main.py'],pathex=[],binaries=[],datas=[('assets','assets')],hiddenimports=['pygame','pygame._sdl2.audio','numpy'],hookspath=[],runtime_hooks=[],excludes=[],noarchive=False)
pyz=PYZ(a.pure)
exe=EXE(pyz,a.scripts,a.binaries,a.datas,[],name='Cartucheira MBS',debug=False,bootloader_ignore_signals=False,strip=False,upx=True,console=False,icon=['assets/icon.ico'])
