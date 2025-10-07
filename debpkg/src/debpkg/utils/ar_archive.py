"""AR archive creation utilities - Pure Python implementation."""

import os


def create_ar_archive(output_file: str, files: list):
    """
    Create an AR archive using pure Python.

    This creates a valid Debian .deb package without needing ar or dpkg tools.

    Args:
        output_file: Path to the output AR archive
        files: List of file paths to include in the archive
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
