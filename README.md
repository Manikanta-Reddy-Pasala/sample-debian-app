# Python Debian Package Generator

This project provides a Python script, `build_deb.py`, that manually generates a simple Debian package (`.deb`) file. The script demonstrates how to construct a package from scratch using standard command-line tools, making it a robust and transparent solution.

The generated package, when installed, places a sample configuration file at `/etc/sampleapp/sample.conf`.

## How to Use

The script is designed to be run from a Debian-based environment (like Ubuntu or inside a Docker container) where the necessary packaging tools are available.

### 1. System Prerequisites

Before running the script, you must have the standard Debian packaging toolchain installed. These are typically pre-installed on most Debian-based systems.

- `dpkg-deb` (part of the `dpkg` package)
- `ar` (part of the `binutils` package)
- `tar`

You can ensure they are installed by running:
```bash
sudo apt-get update
sudo apt-get install -y dpkg-dev binutils
```

### 2. Run the Build Script

To generate the Debian package, simply execute the Python script:

```bash
python3 build_deb.py
```

This will create a file named `sample-config-pkg_1.0.0_all.deb` in the current directory.

## How to Build the Windows Executable (`.exe`)

While the script generates a Debian package, the script itself can be compiled into a standalone Windows executable (`.exe`) using **PyInstaller**. This allows you to run the generator on a Windows machine.

### 1. Install PyInstaller

If you don't have PyInstaller, install it using `pip` on your Windows machine:

```bash
pip install pyinstaller
```

### 2. Build the Executable

Navigate to the project directory in your Windows terminal and run the following command:

```bash
pyinstaller --onefile build_deb.py
```

- `--onefile`: This bundles everything into a single executable file.

### 3. Locate the `.exe` File

PyInstaller will create a `dist` directory. Inside this directory, you will find `build_deb.exe`.

**Important Note for Windows Users:**
For the generated `.exe` to function correctly on Windows, it needs access to the `ar.exe` and `tar.exe` command-line tools. These are not standard Windows tools. You must install them as part of a toolchain like **MinGW-w64** or **Git for Windows** (which includes a basic set of Unix-like tools) and ensure that their containing `bin` directory is added to your system's `PATH` environment variable.