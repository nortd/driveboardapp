import os
import sys

if sys.platform == "darwin":
    icon_opt = "--icon=icon.icns"
elif sys.platform == "win32":
    icon_opt = "--icon=icon.ico"
else:
    icon_opt = ""

if not sys.platform == "darwin":  # Linux Windows
    os.system("python PyInstaller/pyinstaller.py --onefile --windowed --clean --noconfirm %s app.spec" % icon_opt)
else:  # OSX
    os.system("python PyInstaller/pyinstaller.py --onedir --windowed --clean --noconfirm %s app.spec" % icon_opt)

# os.system("python PyInstaller/pyinstaller.py --onefile app.spec")
# os.system("python PyInstaller/pyinstaller.py -w --clean --noconfirm app.spec")
# os.system("python PyInstaller/pyinstaller.py --windowed --clean --noconfirm --hidden-import=pkg_resources ../backend/app.py")
