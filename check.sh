#!/bin/bash
set -eux

paths=(
"vm/" "backup/" "events/" "app.py" "base.py" "config.py" "device_protocol.py" "devices.py" "exc.py" "features.py" "firewall.py" "label.py" "log.py" "spinner.py" "storage.py" "tags.py" "utils.py"
"tools/"{__init__,dochelpers,qubes_prefs,qvm_backup,qvm_backup_restore,qvm_clone,qvm_create,qvm_device,qvm_features,qvm_firewall,qvm_kill,qvm_ls,qvm_notes,qvm_pause,qvm_pool,qvm_prefs,qvm_remove}".py"
)

prefixed_paths=( "${paths[@]/#/qubesadmin/}" )

uv run ruff check "${prefixed_paths[@]}"
uv run ty check "${prefixed_paths[@]}"
