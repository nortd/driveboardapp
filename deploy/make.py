import os

# os.system("python PyInstaller/pyinstaller.py --onefile app.spec")
# os.system("python PyInstaller/pyinstaller.py -w --clean --noconfirm app.spec")
os.system("python PyInstaller/pyinstaller.py --windowed --clean --noconfirm --hidden-import=pkg_resources ../backend/app.py")
