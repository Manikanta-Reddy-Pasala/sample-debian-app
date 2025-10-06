import os
import tarfile
import shutil
import subprocess

def create_deb_package():
    """
    Generates a Debian package (.deb) containing a sample configuration file.
    """
    package_name = "sample-config-pkg"
    version = "1.0.0"
    architecture = "all"
    maintainer = "Jules <jules@example.com>"
    description = "A sample Debian package with a config file."

    # Define package structure and file names
    package_dir = f"{package_name}_{version}_{architecture}"
    deb_file = f"{package_dir}.deb"
    build_dir = "build"

    # Clean up previous build artifacts
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    if os.path.exists(deb_file):
        os.remove(deb_file)

    # --- 1. Create package file structure ---
    config_install_path = os.path.join(build_dir, "etc", "sampleapp")
    os.makedirs(config_install_path, exist_ok=True)

    # Create the sample config file
    with open(os.path.join(config_install_path, "sample.conf"), "w") as f:
        f.write("KEY1=VALUE1\n")
        f.write("KEY2=VALUE2\n")

    # --- 2. Create control information ---
    control_dir = os.path.join(build_dir, "DEBIAN")
    os.makedirs(control_dir, exist_ok=True)

    # Create the control file
    control_content = f"""\
Package: {package_name}
Version: {version}
Architecture: {architecture}
Maintainer: {maintainer}
Description: {description}
"""
    with open(os.path.join(control_dir, "control"), "w") as f:
        f.write(control_content)

    # --- 3. Create tarballs ---
    # Create control.tar.gz
    with tarfile.open("control.tar.gz", "w:gz") as tar:
        tar.add(control_dir, arcname=".")

    # Create data.tar.gz
    with tarfile.open("data.tar.gz", "w:gz") as tar:
        # Add all files and directories from build_dir, excluding DEBIAN
        for item in os.listdir(build_dir):
            if item != "DEBIAN":
                tar.add(os.path.join(build_dir, item), arcname=item)

    # --- 4. Create debian-binary file ---
    with open("debian-binary", "w") as f:
        f.write("2.0\n")

    # --- 5. Assemble the .deb package using 'ar' ---
    subprocess.run(["ar", "rcs", deb_file, "debian-binary", "control.tar.gz", "data.tar.gz"], check=True)

    print(f"Successfully created Debian package: {deb_file}")

    # --- 6. Cleanup ---
    shutil.rmtree(build_dir)
    os.remove("debian-binary")
    os.remove("control.tar.gz")
    os.remove("data.tar.gz")

if __name__ == "__main__":
    create_deb_package()