"""Debian package builder with Jinja2 template support."""

import os
import shutil
import tarfile
from typing import Dict, Any

from ..cert_generator.generator import CertificateGenerator
from ..utils.ar_archive import create_ar_archive
from ..utils.template_renderer import TemplateRenderer


class DebianPackageBuilder:
    """Builds Debian packages with certificates and configuration."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize package builder.

        Args:
            config: Configuration dictionary containing package metadata
        """
        self.config = config
        self.package_name = config['package']['name']
        self.version = config['package']['version']
        self.architecture = config['package']['architecture']
        self.build_dir = "build"
        self.template_dir = config.get('template_dir', 'templates')

        # Initialize template renderer
        self.renderer = TemplateRenderer(self.template_dir)

    def build(self) -> str:
        """
        Build the Debian package.

        Returns:
            Path to the generated .deb file
        """
        print("="*60)
        print("Debian Package Builder")
        print("="*60)
        print()

        deb_file = f"{self.package_name}_{self.version}_{self.architecture}.deb"

        # Clean up previous builds
        self._cleanup()

        # Create directory structure
        self._create_directory_structure()

        # Generate certificates
        self._generate_certificates()

        # Create configuration file from template
        self._create_configuration()

        # Create DEBIAN control files from templates
        self._create_control_files()

        # Create package archives
        self._create_archives()

        # Assemble .deb package
        self._assemble_package(deb_file)

        # Final cleanup
        self._final_cleanup()

        print("\n" + "="*60)
        print("PACKAGE BUILD COMPLETE")
        print("="*60)
        print(f"Package: {deb_file}")
        print(f"Size: {os.path.getsize(deb_file)} bytes")
        print("\nInstall (Ubuntu):")
        print(f"  sudo dpkg -i {deb_file}")
        print("  # or")
        print(f"  sudo apt install ./{deb_file}")
        print("="*60)

        return deb_file

    def _cleanup(self):
        """Clean up previous build artifacts."""
        print("Cleaning up previous builds...")
        deb_file = f"{self.package_name}_{self.version}_{self.architecture}.deb"

        for item in [self.build_dir, deb_file, "debian-binary",
                     "control.tar.gz", "data.tar.gz"]:
            if os.path.exists(item):
                if os.path.isdir(item):
                    shutil.rmtree(item)
                else:
                    os.remove(item)

    def _create_directory_structure(self):
        """Create the package directory structure."""
        print("Creating package structure...")
        install_path = self.config['package']['install_path']

        certs_dir = os.path.join(self.build_dir, install_path.lstrip('/'), "certs")
        os.makedirs(certs_dir, exist_ok=True)

    def _generate_certificates(self):
        """Generate SSL certificates."""
        install_path = self.config['package']['install_path']
        certs_dir = os.path.join(self.build_dir, install_path.lstrip('/'), "certs")

        cert_gen = CertificateGenerator(certs_dir)
        cert_gen.generate_all()

    def _create_configuration(self):
        """Create configuration file from Jinja2 template."""
        print("Creating configuration file from template...")
        install_path = self.config['package']['install_path']
        config_dir = os.path.join(self.build_dir, install_path.lstrip('/'))
        config_file = os.path.join(config_dir, self.config['package']['config_name'])

        context = {
            'package_name': self.package_name,
            'description': self.config['package']['description'],
            'install_path': self.config['package']['install_path'],
            'config': self.config['config']
        }

        self.renderer.render_to_file('config.conf.j2', config_file, context)
        print(f"✓ Configuration file created")

    def _create_control_files(self):
        """Create DEBIAN control files from Jinja2 templates."""
        print("Creating control files from templates...")
        control_dir = os.path.join(self.build_dir, "DEBIAN")
        os.makedirs(control_dir, exist_ok=True)

        # Context for all control files
        context = {
            'package_name': self.package_name,
            'version': self.version,
            'architecture': self.architecture,
            'section': self.config['package']['section'],
            'priority': self.config['package']['priority'],
            'maintainer': self.config['package']['maintainer'],
            'description': self.config['package']['description'],
            'long_description': self.config['package']['long_description'],
            'install_path': self.config['package']['install_path'],
            'config_name': self.config['package']['config_name']
        }

        # Render control files
        control_files = ['control', 'preinst', 'postinst', 'postrm', 'triggers']

        for file_name in control_files:
            template_name = f"debian/{file_name}.j2"
            output_path = os.path.join(control_dir, file_name)
            self.renderer.render_to_file(template_name, output_path, context)

            # Make scripts executable
            if file_name in ['preinst', 'postinst', 'postrm']:
                os.chmod(output_path, 0o755)

        print("✓ Control files created")

    def _create_archives(self):
        """Create control.tar.gz and data.tar.gz."""
        print("Creating control.tar.gz...")
        with tarfile.open("control.tar.gz", "w:gz", format=tarfile.GNU_FORMAT) as tar:
            control_dir = os.path.join(self.build_dir, "DEBIAN")
            tar.add(control_dir, arcname=".")

        print("Creating data.tar.gz...")
        with tarfile.open("data.tar.gz", "w:gz", format=tarfile.GNU_FORMAT) as tar:
            for item in os.listdir(self.build_dir):
                if item != "DEBIAN":
                    item_path = os.path.join(self.build_dir, item)
                    tar.add(item_path, arcname=item)

        print("Creating debian-binary...")
        with open("debian-binary", "w") as f:
            f.write("2.0\n")

    def _assemble_package(self, deb_file: str):
        """Assemble the final .deb package."""
        print("Assembling .deb package...")
        create_ar_archive(deb_file, ["debian-binary", "control.tar.gz", "data.tar.gz"])
        print(f"✓ Package created: {deb_file}")

    def _final_cleanup(self):
        """Clean up temporary build files."""
        print("\nCleaning up temporary files...")
        shutil.rmtree(self.build_dir)
        os.remove("debian-binary")
        os.remove("control.tar.gz")
        os.remove("data.tar.gz")
        print("✓ Cleanup complete")
