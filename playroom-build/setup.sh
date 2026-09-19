#!/usr/bin/env bash
# Installs everything the pipeline needs. Python 3.11 required (bpy 4.2 is cp311).
set -e
python3 -c 'import sys; assert sys.version_info[:2]==(3,11), f"need Python 3.11, found {sys.version.split()[0]}"'
echo "Installing reportlab + numpy..."
pip3 install --quiet reportlab numpy
echo "Installing bpy 4.2 (Blender as a Python module, ~500 MB, this takes a while)..."
pip3 install --quiet bpy==4.2.0
python3 -c "import bpy, reportlab; print('OK - Blender', bpy.app.version_string)"
echo
echo "Now run:"
echo "  python3 blender/build_model.py"
echo "  python3 plans/generate_plans.py"
