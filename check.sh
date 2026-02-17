#!/bin/bash
set -eux

paths=(
"vm/" "backup/" "events/" "app.py" "base.py" "config.py" "device_protocol.py" "devices.py" "exc.py" "features.py" "firewall.py" "label.py" "log.py" "spinner.py" "storage.py" "tags.py" "utils.py"
"tools/"
)

prefixed_paths=( "${paths[@]/#/qubesadmin/}" )

uv run ruff check "${prefixed_paths[@]}"
uv run ty check "${prefixed_paths[@]}"
