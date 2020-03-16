# -*- mode: python -*-

block_cipher = None

added_files = [
    ('..\\src', 'src'),
    ('..\\Data', 'Data'),
    ('..\\save', 'save')
]

a = Analysis(['..\\src\\Execute.py'],
             pathex=['src'],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.datas,
          name='Game',
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
