#!/usr/bin/python
# -*- mode: python -*-

import os, sys
from glob import glob

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


### build TOC
a = Analysis(['../backend/app.py'],
             pathex=[os.path.abspath('__file__')],
             hiddenimports=[],
             hookspath=None)


pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas + resource_files,
          name=target_location,
          debug=False,
          strip=None,
          upx=True,
          console=False )

# app = BUNDLE(exe,
#              name=target_location + '.app')
