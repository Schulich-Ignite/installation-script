# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['install.py'],
             pathex=['C:\\Users\\Kieran\\Desktop\\development\\personal\\installation-script'],
             binaries=[],
             datas=[('ignite.ico', 'ignite.ico'), ('ignite.ipynb', 'ignite.ipynb'), ('spark', 'spark')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=True)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [('v', None, 'OPTION')],
          name='install',
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True , uac_admin=True, icon='ignite.ico')
