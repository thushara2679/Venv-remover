"""
Build script for creating Windows executable of Venv Remover GUI.
Creates an optimized single-file executable with minimal size.
"""
import os
import subprocess
import sys

def check_pyinstaller():
    """Check if PyInstaller is installed, install if not."""
    try:
        import PyInstaller
        print("✓ PyInstaller is already installed")
        return True
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed successfully")
        return True

def create_spec_file():
    """Create optimized PyInstaller spec file."""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['venv_remover_gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'setuptools',
        'distutils',
        'lib2to3',
        'email',
        'html',
        'http',
        'unittest',
        'xml',
        'xmlrpc',
        'pydoc',
        'doctest',
        'argparse',
        'asyncio',
        'concurrent',
        'multiprocessing',
        'pkg_resources',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VenvRemover',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
"""
    
    with open("venv_remover.spec", "w") as f:
        f.write(spec_content)
    
    print("✓ Created optimized spec file: venv_remover.spec")

def build_executable():
    """Build the executable using PyInstaller."""
    print("\nBuilding executable...")
    print("This may take a few minutes...\n")
    
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        "venv_remover.spec"
    ]
    
    subprocess.check_call(cmd)
    print("\n✓ Build completed successfully!")

def show_results():
    """Show build results and file size."""
    exe_path = os.path.join("dist", "VenvRemover.exe")
    
    if os.path.exists(exe_path):
        size_bytes = os.path.getsize(exe_path)
        size_mb = size_bytes / (1024 * 1024)
        
        print(f"\n{'='*60}")
        print(f"✓ Executable created successfully!")
        print(f"{'='*60}")
        print(f"Location: {os.path.abspath(exe_path)}")
        print(f"Size: {size_mb:.2f} MB ({size_bytes:,} bytes)")
        print(f"{'='*60}\n")
        print("You can now distribute VenvRemover.exe as a standalone application.")
        print("No Python installation required on target machines!")
    else:
        print("❌ Error: Executable not found in dist folder")

def main():
    """Main build process."""
    print("="*60)
    print("Venv Remover - Executable Builder")
    print("="*60)
    print()
    
    try:
        # Step 1: Check/Install PyInstaller
        if not check_pyinstaller():
            print("❌ Failed to install PyInstaller")
            return
        
        # Step 2: Create spec file
        create_spec_file()
        
        # Step 3: Build executable
        build_executable()
        
        # Step 4: Show results
        show_results()
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
