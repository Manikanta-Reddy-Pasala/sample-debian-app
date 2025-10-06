# Debian Package Generator

This project contains a Python script that generates a simple Debian package (`.deb`) file. The generated package, when installed, places a sample configuration file at `/etc/sampleapp/sample.conf`.

The script is designed to be cross-platform, but the primary goal is to package it as a standalone Windows executable (`.exe`).

## Prerequisites

- Python 3.6+
- `pip` for installing dependencies

## How to Use

### 1. Install Dependencies

First, install the required Python libraries. Although the script now uses the standard `ar` command, the `requirements.txt` file is kept for good practice.

```bash
pip install -r requirements.txt
```

### 2. Run the Script Directly

You can run the generator script directly from your terminal:

```bash
python deb_generator.py
```

This will create a file named `sample-config-pkg_1.0.0_all.deb` in the current directory.

## How to Build the Windows Executable (`.exe`)

To create a standalone `.exe` file that can be run on Windows without needing a Python installation, you can use **PyInstaller**.

### 1. Install PyInstaller

If you don't have PyInstaller, install it using `pip`:

```bash
pip install pyinstaller
```

### 2. Build the Executable

Navigate to the `deb_pkg_generator` directory in your terminal and run the following command:

```bash
pyinstaller --onefile deb_generator.py
```

- `--onefile`: This tells PyInstaller to bundle everything into a single executable file.

### 3. Locate the `.exe` File

PyInstaller will create a `dist` directory. Inside this directory, you will find `deb_generator.exe`. You can now distribute and run this file on any Windows machine.

**Note:** The `ar` command-line tool is required for the script to function. On Linux and macOS, it is typically pre-installed. For Windows, you may need to install it as part of a toolchain like **MinGW-w64** or **Cygwin**. Ensure that `ar.exe` is available in the system's PATH.