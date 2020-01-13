#!/usr/bin/env bash

set -o errexit
set -o nounset

python3 scripts/get_station_coordinates.py
python3 scripts/assign_ids.py
python3 scripts/create_javascript.py
