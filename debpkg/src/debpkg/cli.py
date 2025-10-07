#!/usr/bin/env python3
"""Command-line interface for Debian package builder."""

import sys
import argparse
import yaml
from pathlib import Path
from .package_builder.builder import DebianPackageBuilder


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='Debian Package Generator - Build .deb packages with certificates and configuration'
    )
    parser.add_argument(
        '-c', '--config',
        default='config/package.yaml',
        help='Path to package configuration file (default: config/package.yaml)'
    )
    parser.add_argument(
        '-t', '--templates',
        default='templates',
        help='Path to templates directory (default: templates)'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    args = parser.parse_args()

    try:
        # Load configuration
        config = load_config(args.config)
        config['template_dir'] = args.templates

        # Build package
        builder = DebianPackageBuilder(config)
        deb_file = builder.build()

        print(f"\n✓ Success! Package created: {deb_file}")
        return 0

    except FileNotFoundError as e:
        print(f"Error: Configuration file not found: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
