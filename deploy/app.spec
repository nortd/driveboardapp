#!/usr/bin/python
# -*- mode: python -*-

import os, sys
from glob import glob

block_cipher = None

resource_files = []
def add_resource_files(file_list):
    global resource_files
    for resfile in file_list:
        resource_files.append( (os.path.relpath(resfile,'../'), resfile, 'DATA') )

### files to pack into the executable
add_resource_files( glob('../backend/*.gif') )
add_resource_files( glob('../frontend/*.html') )
add_resource_files( glob('../frontend/*.js') )
add_resource_files( glob('../frontend/css/*') )
add_resource_files( glob('../frontend/fonts/*') )
add_resource_files( glob('../frontend/img/*') )
add_resource_files( glob('../frontend/js/*') )
add_resource_files( glob('../firmware/*.hex') )
add_resource_files( glob('../library/*') )

### name of the executable
### depending on platform
target_location = os.path.join('dist', 'driveboardapp')
if sys.platform == "darwin":
    target_location = os.path.join('dist_osx', 'driveboardapp')
    add_resource_files( glob('../firmware/tools_osx/*') )
elif sys.platform == "win32":
    target_location = os.path.join('dist_win', 'driveboardapp.exe')
    add_resource_files( glob('../firmware/tools_win/*') )
elif sys.platform == "linux" or sys.platform == "linux2":
    target_location = os.path.join('dist_linux', 'driveboardapp')
    add_resource_files( glob('../firmware/tools_linux/*') )


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

### build TOC
a = Analysis(['../backend/web.py'],
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
          upx=True,
          console=True )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name=target_location )

if sys.platform == "darwin":
    app = BUNDLE(coll,
                 name=target_location + '.app',
                 icon=None,
                 bundle_identifier=None)
