"""Certificate generator for CA, server, and client certificates."""

import os
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


class CertificateGenerator:
    """Generates CA, server, and client certificates."""

    def __init__(self, cert_dir: str):
        """
        Initialize certificate generator.

        Args:
            cert_dir: Directory where certificates will be saved
        """
        self.cert_dir = cert_dir
        os.makedirs(cert_dir, exist_ok=True)

    def generate_all(self):
        """Generate all certificates (CA, server, client)."""
        print("Generating certificates...")
        ca_key, ca_cert = self._generate_ca_certificate()
        self._generate_server_certificate(ca_key, ca_cert)
        self._generate_client_certificate(ca_key, ca_cert)
        print("✓ Certificates generated successfully")

    def _generate_ca_certificate(self):
        """Generate CA private key and certificate."""
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

        # Write CA certificate and key
        self._write_certificate(ca_cert, "ca.crt")
        self._write_private_key(ca_key, "ca.key")

        return ca_key, ca_cert

    def _generate_server_certificate(self, ca_key, ca_cert):
        """Generate server private key and certificate signed by CA."""
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
        self._write_certificate(server_cert, "server.crt")
        self._write_private_key(server_key, "server.key")

    def _generate_client_certificate(self, ca_key, ca_cert):
        """Generate client private key and certificate signed by CA."""
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
        self._write_certificate(client_cert, "client.crt")
        self._write_private_key(client_key, "client.key")

    def _write_certificate(self, cert, filename: str):
        """Write certificate to file."""
        cert_path = os.path.join(self.cert_dir, filename)
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        os.chmod(cert_path, 0o644)

    def _write_private_key(self, key, filename: str):
        """Write private key to file."""
        key_path = os.path.join(self.cert_dir, filename)
        with open(key_path, "wb") as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        os.chmod(key_path, 0o600)
