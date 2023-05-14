#!/bin/bash

_script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

pushd "${_script_dir}" > /dev/null

# Declare variables

_bot_name="daily-team-stuff-bot"

_bot_service_name="${_bot_name}.service"
_bot_service_path="/etc/systemd/system/${_bot_service_name}"

# Enable and start systemd service

sudo cp "${_bot_service_name}" "${_bot_service_path}"

sudo systemctl daemon-reload

sudo systemctl enable ${_bot_service_name}

sudo systemctl start ${_bot_service_name}

# Finalize

popd > /dev/null

echo "Done."
exit 0
