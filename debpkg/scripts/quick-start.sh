#!/bin/bash
# Quick start script for Debian Package Generator

set -e

echo "=============================================="
echo "Debian Package Generator - Quick Start"
echo "=============================================="
echo ""

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    echo "Error: Please run this script from the debpkg directory"
    exit 1
fi

# Install the package
echo "Step 1: Installing package..."
pip3 install -e . >/dev/null 2>&1 || {
    echo "Installing package..."
    pip3 install -e .
}
echo "✓ Package installed"
echo ""

# Run tests
echo "Step 2: Running tests..."
pytest -q 2>/dev/null || {
    echo "Installing test dependencies..."
    pip3 install pytest pytest-cov
    pytest -q
}
echo "✓ Tests passed"
echo ""

# Build the package
echo "Step 3: Building Debian package..."
debpkg-build
echo ""

echo "=============================================="
echo "Success! Your package is ready."
echo "=============================================="
echo ""
echo "Package created: sample-config-pkg_1.0.0_all.deb"
echo ""
echo "Next steps:"
echo "  - Customize: Edit config/package.yaml"
echo "  - Templates: Modify files in templates/"
echo "  - Rebuild: Run 'debpkg-build'"
echo ""
echo "For help: debpkg-build --help"
echo "Documentation: See README.md"
echo "=============================================="
