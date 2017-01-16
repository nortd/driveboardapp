import os
import sys

if not sys.platform == "darwin":  # Linux Windows
    os.system("python PyInstaller/pyinstaller.py --onefile --windowed --clean --noconfirm app.spec")
else:  # OSX
    os.system("python PyInstaller/pyinstaller.py --onedir --windowed --clean --noconfirm app.spec")

# os.system("python PyInstaller/pyinstaller.py --onefile app.spec")
# os.system("python PyInstaller/pyinstaller.py -w --clean --noconfirm app.spec")
# os.system("python PyInstaller/pyinstaller.py --windowed --clean --noconfirm --hidden-import=pkg_resources ../backend/app.py")
