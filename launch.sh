#!/bin/bash
# Conky Theme Manager - Launcher
DIR="$(dirname "$(readlink -f "$0")")"
python3 "$DIR/conky_manager.py" "$@"
