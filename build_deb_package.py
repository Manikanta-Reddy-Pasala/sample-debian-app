#!/usr/bin/env python3
"""
Pure Python Debian Package Generator
Creates .deb package with CA cert, server cert, client cert under /opt/config/
"""

import os
import tarfile
import shutil
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


def generate_certificates(cert_dir):
    """
    Generate CA certificate, server certificate, and client certificate
    """
    print("Generating certificates...")

    # Step 1: Generate CA private key and certificate
    print("  - Generating CA certificate...")
    ca_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    ca_subject = ca_issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "State"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "City"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Organization"),
        x509.NameAttribute(NameOID.COMMON_NAME, "CA"),
    ])

    ca_cert = x509.CertificateBuilder().subject_name(
        ca_subject
    ).issuer_name(
        ca_issuer
    ).public_key(
        ca_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=3650)  # 10 years
    ).add_extension(
        x509.BasicConstraints(ca=True, path_length=None),
        critical=True,
    ).sign(ca_key, hashes.SHA256(), default_backend())

    # Write CA certificate
    with open(os.path.join(cert_dir, "ca.crt"), "wb") as f:
        f.write(ca_cert.public_bytes(serialization.Encoding.PEM))

    with open(os.path.join(cert_dir, "ca.key"), "wb") as f:
        f.write(ca_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Step 2: Generate server private key and certificate (signed by CA)
    print("  - Generating server certificate...")
    server_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    server_subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "State"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "City"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Organization"),
        x509.NameAttribute(NameOID.COMMON_NAME, "server.local"),
    ])

    server_cert = x509.CertificateBuilder().subject_name(
        server_subject
    ).issuer_name(
        ca_cert.subject
    ).public_key(
        server_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("server.local"),
            x509.DNSName("localhost"),
        ]),
        critical=False,
    ).sign(ca_key, hashes.SHA256(), default_backend())

    # Write server certificate and key
    with open(os.path.join(cert_dir, "server.crt"), "wb") as f:
        f.write(server_cert.public_bytes(serialization.Encoding.PEM))

    with open(os.path.join(cert_dir, "server.key"), "wb") as f:
        f.write(server_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Step 3: Generate client private key and certificate (signed by CA)
    print("  - Generating client certificate...")
    client_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    client_subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "State"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "City"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Organization"),
        x509.NameAttribute(NameOID.COMMON_NAME, "client.local"),
    ])

    client_cert = x509.CertificateBuilder().subject_name(
        client_subject
    ).issuer_name(
        ca_cert.subject
    ).public_key(
        client_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("client.local"),
        ]),
        critical=False,
    ).sign(ca_key, hashes.SHA256(), default_backend())

    # Write client certificate and key
    with open(os.path.join(cert_dir, "client.crt"), "wb") as f:
        f.write(client_cert.public_bytes(serialization.Encoding.PEM))

    with open(os.path.join(cert_dir, "client.key"), "wb") as f:
        f.write(client_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    print("✓ Certificates generated successfully")


def create_ar_archive(output_file, files):
    """
    Create an AR archive using pure Python
    """
    print(f"Creating AR archive: {output_file}")

    with open(output_file, 'wb') as ar_file:
        ar_file.write(b'!<arch>\n')

        for file_path in files:
            stat = os.stat(file_path)
            file_size = stat.st_size
            file_name = os.path.basename(file_path)

            header = bytearray(60)

            # File name (16 bytes)
            name_bytes = file_name.encode('ascii')[:16]
            header[0:len(name_bytes)] = name_bytes
            for i in range(len(name_bytes), 16):
                header[i] = ord(' ')

            # Modification time (12 bytes)
            mtime = str(int(stat.st_mtime)).encode('ascii')
            header[16:16+len(mtime)] = mtime
            for i in range(16+len(mtime), 28):
                header[i] = ord(' ')

            # Owner ID (6 bytes)
            header[28:30] = b'0 '
            for i in range(30, 34):
                header[i] = ord(' ')

            # Group ID (6 bytes)
            header[34:36] = b'0 '
            for i in range(36, 40):
                header[i] = ord(' ')

            # File mode (8 bytes, octal)
            mode = b'100644'
            header[40:40+len(mode)] = mode
            for i in range(40+len(mode), 48):
                header[i] = ord(' ')

            # File size (10 bytes)
            size_bytes = str(file_size).encode('ascii')
            header[48:48+len(size_bytes)] = size_bytes
            for i in range(48+len(size_bytes), 58):
                header[i] = ord(' ')

            # End marker
            header[58:60] = b'`\n'

            ar_file.write(header)

            with open(file_path, 'rb') as f:
                ar_file.write(f.read())

            if file_size % 2 != 0:
                ar_file.write(b'\n')

    print("✓ AR archive created")


def set_permissions(file_path, mode):
    """Set file permissions"""
    try:
        os.chmod(file_path, mode)
    except Exception:
        pass


def create_deb_package():
    """
    Create Debian package with certificates and config in /opt/config/
    """

    package_name = "sample-config-pkg"
    version = "1.0.0"
    architecture = "all"
    maintainer = "Admin <admin@example.com>"
    description = "Sample package with certificates and configuration"

    package_dir = f"{package_name}_{version}_{architecture}"
    deb_file = f"{package_dir}.deb"
    build_dir = "build"

    # Clean up
    print("Cleaning up previous builds...")
    for item in [build_dir, deb_file, "debian-binary", "control.tar.gz", "data.tar.gz"]:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.rmtree(item)
            else:
                os.remove(item)

    # Create directory structure
    print("Creating package structure...")
    certs_dir = os.path.join(build_dir, "opt", "config", "certs")
    config_dir = os.path.join(build_dir, "opt", "config")
    os.makedirs(certs_dir, exist_ok=True)

    # Generate certificates
    generate_certificates(certs_dir)

    # Set permissions
    for cert_file in ["ca.crt", "server.crt", "client.crt"]:
        set_permissions(os.path.join(certs_dir, cert_file), 0o644)
    for key_file in ["ca.key", "server.key", "client.key"]:
        set_permissions(os.path.join(certs_dir, key_file), 0o600)

    # Create test.conf
    print("Creating test.conf...")
    test_conf_content = """\
# Sample Configuration File
# Generated by sample-config-pkg

[settings]
host=localhost
port=443
ssl_enabled=true

[certificates]
ca_cert=/opt/config/certs/ca.crt
server_cert=/opt/config/certs/server.crt
server_key=/opt/config/certs/server.key
client_cert=/opt/config/certs/client.crt
client_key=/opt/config/certs/client.key

[logging]
log_level=info
log_file=/var/log/sample-app.log
"""

    with open(os.path.join(config_dir, "test.conf"), "w") as f:
        f.write(test_conf_content)

    # Create DEBIAN control directory
    print("Creating control files...")
    control_dir = os.path.join(build_dir, "DEBIAN")
    os.makedirs(control_dir, exist_ok=True)

    # Control file
    control_content = f"""\
Package: {package_name}
Version: {version}
Section: utils
Priority: optional
Architecture: {architecture}
Maintainer: {maintainer}
Description: {description}
 This package installs certificates (CA, server, client) and configuration.
 Files are placed under /opt/config/.
"""

    with open(os.path.join(control_dir, "control"), "w") as f:
        f.write(control_content)

    # Triggers file
    triggers_content = """\
interest-noawait /opt/config/certs
interest-noawait /opt/config/test.conf
"""

    with open(os.path.join(control_dir, "triggers"), "w") as f:
        f.write(triggers_content)

    # Pre-install script
    preinst_content = """\
#!/bin/bash
set -e

echo "Pre-installation: Preparing to install sample-config-pkg"

# Backup existing config if present
if [ -f /opt/config/test.conf ]; then
    echo "Backing up existing test.conf"
    cp /opt/config/test.conf /opt/config/test.conf.bak
fi

# Create directories
mkdir -p /opt/config/certs

echo "Pre-installation completed"
exit 0
"""

    preinst_path = os.path.join(control_dir, "preinst")
    with open(preinst_path, "w") as f:
        f.write(preinst_content)
    set_permissions(preinst_path, 0o755)

    # Post-install script
    postinst_content = """\
#!/bin/bash
set -e

echo "Post-installation: Configuring sample-config-pkg"

# Set proper permissions
if [ -d /opt/config/certs ]; then
    chmod 755 /opt/config/certs
    chmod 644 /opt/config/certs/*.crt 2>/dev/null || true
    chmod 600 /opt/config/certs/*.key 2>/dev/null || true
    echo "Certificate permissions set"
fi

if [ -f /opt/config/test.conf ]; then
    chmod 644 /opt/config/test.conf
    echo "Configuration permissions set"
fi

echo ""
echo "=========================================="
echo "Installation complete!"
echo "=========================================="
echo "Installed files:"
echo "  - CA Certificate: /opt/config/certs/ca.crt"
echo "  - Server Certificate: /opt/config/certs/server.crt"
echo "  - Server Key: /opt/config/certs/server.key"
echo "  - Client Certificate: /opt/config/certs/client.crt"
echo "  - Client Key: /opt/config/certs/client.key"
echo "  - Configuration: /opt/config/test.conf"
echo "=========================================="

exit 0
"""

    postinst_path = os.path.join(control_dir, "postinst")
    with open(postinst_path, "w") as f:
        f.write(postinst_content)
    set_permissions(postinst_path, 0o755)

    # Post-removal script
    postrm_content = """\
#!/bin/bash
set -e

if [ "$1" = "purge" ]; then
    echo "Removing configuration files..."
    rm -f /opt/config/test.conf
    rm -f /opt/config/test.conf.bak
    echo "Cleanup completed"
fi

exit 0
"""

    postrm_path = os.path.join(control_dir, "postrm")
    with open(postrm_path, "w") as f:
        f.write(postrm_content)
    set_permissions(postrm_path, 0o755)

    # Create control.tar.gz
    print("Creating control.tar.gz...")
    with tarfile.open("control.tar.gz", "w:gz", format=tarfile.GNU_FORMAT) as tar:
        tar.add(control_dir, arcname=".")

    # Create data.tar.gz
    print("Creating data.tar.gz...")
    with tarfile.open("data.tar.gz", "w:gz", format=tarfile.GNU_FORMAT) as tar:
        for item in os.listdir(build_dir):
            if item != "DEBIAN":
                item_path = os.path.join(build_dir, item)
                tar.add(item_path, arcname=item)

    # Create debian-binary
    print("Creating debian-binary...")
    with open("debian-binary", "w") as f:
        f.write("2.0\n")

    # Assemble .deb package
    print("Assembling .deb package...")
    create_ar_archive(deb_file, ["debian-binary", "control.tar.gz", "data.tar.gz"])

    print(f"\n✓ Package created: {deb_file}")
    print(f"✓ Package size: {os.path.getsize(deb_file)} bytes")

    # Cleanup
    print("\nCleaning up...")
    shutil.rmtree(build_dir)
    os.remove("debian-binary")
    os.remove("control.tar.gz")
    os.remove("data.tar.gz")

    print("\n" + "="*60)
    print("PACKAGE BUILD COMPLETE")
    print("="*60)
    print(f"Package: {deb_file}")
    print("\nVerify (macOS):")
    print(f"  ar -x {deb_file}")
    print("\nInstall (Ubuntu):")
    print(f"  sudo apt install ./{deb_file}")
    print("="*60)


if __name__ == "__main__":
    try:
        print("="*60)
        print("Debian Package Generator")
        print("="*60)
        print()
        create_deb_package()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
