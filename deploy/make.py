import os
import sys

if sys.platform == "darwin":
    icon_opt = "--icon='icon.icns'"
elif sys.platform == "win32":
    icon_opt = "--icon='icon.ico'"
else:
    icon_opt = ""

if not sys.platform == "darwin":  # Linux Windows
    cmd = "python PyInstaller/pyinstaller.py --onefile --windowed %s --clean --noconfirm app.spec" % icon_opt
else:  # OSX
    cmd = "python PyInstaller/pyinstaller.py --onedir --windowed %s --clean --noconfirm app.spec" % icon_opt

os.system(cmd)
