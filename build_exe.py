# build_exe.py - SIMPLE NO-ICON VERSION
import PyInstaller.__main__
import os
import shutil

print("Building DumpOrganizer.exe...")
print("This might take a minute...")

# PyInstaller arguments - NO ICON
args = [
    'main.py',
    '--name=DumpOrganizer',
    '--onefile',
    '--windowed',
    '--clean',
    '--distpath=dist'
]

print("Starting build process...")
PyInstaller.__main__.run(args)

print("\n✅ Build complete!")
print(f"EXE location: {os.path.abspath('dist/DumpOrganizer.exe')}")

# Clean up temp files (optional)
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('DumpOrganizer.spec'):
    os.remove('DumpOrganizer.spec')
    
print("\nTemp files cleaned up.")
