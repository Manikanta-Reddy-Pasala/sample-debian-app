import os
import shutil
import subprocess
import tempfile

def run_command(command, cwd=None):
    """Executes a command and raises an exception on failure."""
    print(f"Running command: {' '.join(command)}")
    result = subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

def create_deb_package():
    """
    Manually generates a Debian package (.deb) containing a sample
    configuration file using standard command-line tools.
    """
    package_name = "sample-config-pkg"
    version = "1.0.0"
    architecture = "all"
    maintainer = "Jules <jules@example.com>"
    description = "A sample Debian package that installs a config file."

    # --- 1. Setup Project Structure ---
    package_dir = f"{package_name}_{version}_{architecture}"
    deb_file = f"{package_dir}.deb"

    # Use a temporary directory for all build artifacts
    build_root = tempfile.mkdtemp()

    try:
        # This is the root of the package content
        pkg_build_dir = os.path.join(build_root, "pkg")
        os.makedirs(pkg_build_dir, exist_ok=True)

        # --- 2. Create Package Contents ---
        config_install_dir = os.path.join(pkg_build_dir, "etc", "sampleapp")
        os.makedirs(config_install_dir, exist_ok=True)

        with open(os.path.join(config_install_dir, "sample.conf"), "w") as f:
            f.write("KEY1=VALUE1\n")
            f.write("KEY2=VALUE2\n")
            f.write("GENERATED_BY=manual_script\n")

        # --- 3. Create DEBIAN Control Information ---
        control_dir = os.path.join(build_root, "control")
        os.makedirs(control_dir, exist_ok=True)

        control_content = f"""\
Package: {package_name}
Version: {version}
Architecture: {architecture}
Maintainer: {maintainer}
Description: {description}
"""
        with open(os.path.join(control_dir, "control"), "w") as f:
            f.write(control_content)

        # --- 4. Create Tarballs ---
        control_tar_path = os.path.join(build_root, "control.tar.gz")
        data_tar_path = os.path.join(build_root, "data.tar.gz")

        # Create control.tar.gz
        run_command(["tar", "-czf", control_tar_path, "."], cwd=control_dir)

        # Create data.tar.gz
        run_command(["tar", "-czf", data_tar_path, "."], cwd=pkg_build_dir)

        # --- 5. Create debian-binary file ---
        debian_binary_path = os.path.join(build_root, "debian-binary")
        with open(debian_binary_path, "w") as f:
            f.write("2.0\n")

        # --- 6. Assemble the .deb package using 'ar' ---
        # Note: Using 'rc' not 'rcs' to avoid creating a symbol table,
        # which caused issues for some 'ar' versions.
        final_deb_path = os.path.abspath(deb_file) # Place it in the current dir
        run_command([
            "ar", "rc", final_deb_path,
            debian_binary_path, control_tar_path, data_tar_path
        ])

        print(f"\nSuccessfully created Debian package: {final_deb_path}")

    finally:
        # --- 7. Cleanup ---
        print("Cleaning up temporary build directory...")
        shutil.rmtree(build_root)

if __name__ == "__main__":
    create_deb_package()