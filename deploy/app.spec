#!/usr/bin/python
# -*- mode: python -*-

import os, sys

block_cipher = None

data_files = [
    ('../backend/*.gif', 'backend'),
    ('../frontend/*.html', 'frontend'),
    ('../frontend/*.js', 'frontend'),
    ('../frontend/css/*', 'frontend/css'),
    ('../frontend/fonts/*', 'frontend/fonts'),
    ('../frontend/img/*', 'frontend/img'),
    ('../frontend/js/*', 'frontend/js'),
    ('../firmware/*.hex', 'firmware'),
    ('../library/*', 'library')
]


### name of the executable
### depending on platform
target_location = os.path.join('dist', 'driveboardapp')
if sys.platform == "darwin":
    target_location = os.path.join('dist_osx', 'driveboardapp')
    data_files.append(('../firmware/tools_osx/*', 'firmware/tools_osx'))
elif sys.platform == "win32":
    target_location = os.path.join('dist_win', 'driveboardapp.exe')
    data_files.append(('../firmware/tools_win/*', 'firmware/tools_win'))
elif sys.platform == "linux" or sys.platform == "linux2":
    target_location = os.path.join('dist_linux', 'driveboardapp')
    data_files.append(('../firmware/tools_linux/*', 'firmware/tools_linux'))



if not sys.platform == "darwin":  # Linux Windows
    ### build TOC
    a = Analysis(['../backend/app.py'],
                 pathex=[os.path.abspath('__file__')],
                 binaries=None,
                 datas=data_files,
                 hiddenimports=['pkg_resources', 'encodings'],
                 hookspath=None,
                 runtime_hooks=[],
                 excludes=[],
                 win_no_prefer_redirects=False,
                 win_private_assemblies=False,
                 cipher=block_cipher)


    pyz = PYZ(a.pure,
              cipher=block_cipher)

    exe = EXE(pyz,
              a.scripts,
              a.binaries,
              a.zipfiles,
              a.datas,
              name=target_location,
              debug=False,
              strip=False,
              upx=False,
              console=False,
              icon="icon.ico" )

else:  # OSX
    a = Analysis(['../backend/app.py'],
                 pathex=[os.path.abspath('__file__')],
                 binaries=None,
                 datas=data_files,
                 hiddenimports=['pkg_resources', 'encodings'],
                 hookspath=None,
                 runtime_hooks=[],
                 excludes=[],
                 win_no_prefer_redirects=False,
                 win_private_assemblies=False,
                 cipher=block_cipher)


    pyz = PYZ(a.pure,
              a.zipped_data,
              cipher=block_cipher)

    exe = EXE(pyz,
              a.scripts,
              exclude_binaries=True,
              name=target_location,
            #   a.datas + resource_files,
              debug=False,
              strip=False,
              upx=False,
              console=False )

    coll = COLLECT(exe,
                   a.binaries,
                   a.zipfiles,
                   a.datas,
                   strip=False,
                   upx=False,
                   name=target_location )

    app = BUNDLE(coll,
                 name=target_location + '.app',
                 icon="icon.icns",
                 bundle_identifier=None)
