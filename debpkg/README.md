# Debian Package Generator

Production-ready Debian package generator with SSL certificates and Jinja2 templates.

## Quick Start

```bash
cd debpkg
pip3 install -e .
debpkg-build
```

## Features

- ✅ **Pure Python AR Archive** - Creates .deb files without external tools
- ✅ **Jinja2 Templates** - All Debian control files and config templated
- ✅ **YAML Configuration** - Easy customization via config/package.yaml
- ✅ **Modular Architecture** - Clean, maintainable code structure
- ✅ **Certificate Generation** - CA, server, and client certs included

## Project Structure

```
debpkg/
├── config/
│   └── package.yaml          # Package configuration
├── src/debpkg/
│   ├── cert_generator/       # Certificate generation
│   ├── package_builder/      # Package builder
│   └── utils/                # AR archive & Jinja2
├── templates/
│   ├── debian/               # Control file templates
│   │   ├── control.j2
│   │   ├── preinst.j2
│   │   ├── postinst.j2
│   │   ├── postrm.j2
│   │   └── triggers.j2
│   └── config.conf.j2        # App config template
└── scripts/
    └── quick-start.sh
```

## Installation

```bash
pip3 install -e .
```

## Usage

### Build Package

```bash
debpkg-build
```

### Custom Configuration

```bash
debpkg-build --config /path/to/config.yaml --templates /path/to/templates
```

### Customize Package

Edit `config/package.yaml`:

```yaml
package:
  name: my-package
  version: 1.0.0
  maintainer: Your Name <you@example.com>
  install_path: /opt/myapp

config:
  settings:
    host: localhost
    port: 443
```

### Customize Templates

Edit files in `templates/` directory to change package behavior.

## Ubuntu Installation

### Install Package

```bash
sudo apt install ./sample-config-pkg_1.0.0_all.deb
```

### Verify Installation

```bash
ls -la /opt/config/certs/
cat /opt/config/test.conf
```

### Package Contents

The package installs:

- `/opt/config/certs/ca.crt` - CA certificate
- `/opt/config/certs/ca.key` - CA private key
- `/opt/config/certs/server.crt` - Server certificate
- `/opt/config/certs/server.key` - Server private key
- `/opt/config/certs/client.crt` - Client certificate
- `/opt/config/certs/client.key` - Client private key
- `/opt/config/test.conf` - Application configuration

### Uninstall

```bash
sudo apt remove sample-config-pkg
```

### Complete Removal (including config)

```bash
sudo apt purge sample-config-pkg
```

## Dependencies

Runtime:
- `cryptography>=41.0.0` - Certificate generation
- `jinja2>=3.1.0` - Template rendering
- `pyyaml>=6.0.0` - Configuration parsing

## How It Works

1. **Pure Python AR Archive** - Custom implementation creates valid .deb files (no ar/dpkg needed)
2. **Jinja2 Templating** - All Debian control files and configs rendered from templates
3. **Certificate Generation** - Uses cryptography library to create CA-signed certs
4. **Proper Permissions** - Sets correct file permissions (644 for certs, 600 for keys)

### Why Not stdeb?

This uses a custom pure Python AR archive implementation instead of stdeb because:
- Works cross-platform (macOS, Linux, Windows)
- No external dependencies on Debian tools
- Full control over package structure
- Simpler and more reliable

## Python API

```python
from debpkg import DebianPackageBuilder
import yaml

with open('config/package.yaml', 'r') as f:
    config = yaml.safe_load(f)

config['template_dir'] = 'templates'

builder = DebianPackageBuilder(config)
deb_file = builder.build()
print(f"Package created: {deb_file}")
```

## License

MIT License
