import os
import sys


if not sys.platform == "darwin":  # Linux Windows
    cmd = "python PyInstaller/pyinstaller.py --onefile --windowed --clean --noconfirm app.spec"
else:  # OSX
    cmd = "python PyInstaller/pyinstaller.py --onedir --windowed --clean --noconfirm app.spec"

print cmd
os.system(cmd)
