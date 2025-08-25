#!/usr/bin/env python3
"""
Install script for Stata DTA file support in EDVAN DBF Commander
This script will attempt to install pyreadstat for Stata .dta file support
"""

import subprocess
import sys
import os

def install_pyreadstat():
    """Install pyreadstat library for Stata support"""
    print("=" * 60)
    print("EDVAN DBF Commander - Stata Support Installation")
    print("=" * 60)
    print()
    
    print("This script will install pyreadstat library for Stata .dta file support.")
    print("This may require C++ build tools to be installed on your system.")
    print()
    
    # Check if pyreadstat is already installed
    try:
        import pyreadstat
        print("✅ pyreadstat is already installed!")
        print(f"   Version: {pyreadstat.__version__ if hasattr(pyreadstat, '__version__') else 'Unknown'}")
        input("\nPress Enter to continue...")
        return True
    except ImportError:
        print("❌ pyreadstat is not installed.")
        print()
    
    # Ask user for confirmation
    response = input("Do you want to install pyreadstat? (y/N): ").lower().strip()
    if response not in ['y', 'yes']:
        print("Installation cancelled.")
        return False
    
    print("\n" + "─" * 60)
    print("Installing pyreadstat...")
    print("─" * 60)
    print()
    
    try:
        # Try to install pyreadstat
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "pyreadstat"
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ pyreadstat installed successfully!")
            print()
            
            # Test the installation
            try:
                import pyreadstat
                print("✅ Installation verified - pyreadstat can be imported.")
                return True
            except ImportError as e:
                print(f"❌ Installation verification failed: {e}")
                return False
        else:
            print("❌ Installation failed!")
            print(f"Error: {result.stderr}")
            print()
            show_manual_installation_help()
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Installation timed out (5 minutes)")
        print("This might be due to compilation taking too long.")
        show_manual_installation_help()
        return False
    except Exception as e:
        print(f"❌ Installation error: {e}")
        show_manual_installation_help()
        return False

def show_manual_installation_help():
    """Show manual installation instructions"""
    print("\n" + "=" * 60)
    print("MANUAL INSTALLATION INSTRUCTIONS")
    print("=" * 60)
    print()
    
    if os.name == 'nt':  # Windows
        print("For Windows:")
        print("1. Install Microsoft Visual C++ Build Tools:")
        print("   https://visualstudio.microsoft.com/visual-cpp-build-tools/")
        print()
        print("2. Or install Microsoft Visual Studio Community:")
        print("   https://visualstudio.microsoft.com/vs/community/")
        print()
        print("3. After installing build tools, run:")
        print("   pip install pyreadstat")
        print()
        
    elif os.name == 'posix':  # Linux/macOS
        if sys.platform == 'darwin':  # macOS
            print("For macOS:")
            print("1. Install Xcode Command Line Tools:")
            print("   xcode-select --install")
            print()
            print("2. Then run:")
            print("   pip install pyreadstat")
            print()
        else:  # Linux
            print("For Linux (Ubuntu/Debian):")
            print("1. Install build essentials:")
            print("   sudo apt-get install build-essential python3-dev")
            print()
            print("2. Then run:")
            print("   pip install pyreadstat")
            print()
            print("For Linux (CentOS/RHEL/Fedora):")
            print("1. Install build essentials:")
            print("   sudo yum install gcc python3-devel")
            print("   # or on newer systems:")
            print("   sudo dnf install gcc python3-devel")
            print()
            print("2. Then run:")
            print("   pip install pyreadstat")
            print()
    
    print("Alternative options:")
    print("- Use conda: conda install -c conda-forge pyreadstat")
    print("- Use pre-compiled wheels if available")
    print()
    print("Note: Without pyreadstat, you can still use all DBF features.")
    print("Only Stata .dta file support will be unavailable.")

def main():
    """Main function"""
    try:
        success = install_pyreadstat()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 Installation completed successfully!")
            print("You can now use Stata .dta file features in EDVAN DBF Commander.")
        else:
            print("⚠️  Installation was not completed.")
            print("EDVAN DBF Commander will work without Stata support.")
            print("You can try the manual installation steps above.")
        
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n❌ Installation cancelled by user.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
    
    print()
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
