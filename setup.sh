#!/bin/bash

_script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

pushd "${_script_dir}" > /dev/null

# Rename *.example files

_dirs=('data' 'modules')

for _dir in "${_dirs[@]}"; do
    pushd "${_dir}" > /dev/null

    for _file in *.example; do
        _new_name="${_file/%.example/}"

        mv "${_file}" "${_new_name}"
    done

    popd > /dev/null
done

# Declare variables

_user="$USER"
_group="${_user}"

_bot_name="daily-team-stuff-bot"

_runbotsh_name="run_bot.sh"
_runbotsh_path="${_script_dir}/${_runbotsh_name}"

_runrestartsh_name="run_restart.sh"
_runrestartsh_path="${_script_dir}/${_runrestartsh_name}"

_bot_service_name="${_bot_name}.service"
_bot_service_path="/etc/systemd/system/${_bot_service_name}"

_mainpy_path="${_script_dir}/main.py"

_cron_file_name="usercron"

# Create run_bot.sh

cat << EOF > "${_runbotsh_name}"
#!/bin/bash
python3 "${_mainpy_path}"

EOF

# Create run_restart.sh

cat << EOF > "${_runrestartsh_name}"
#!/bin/bash
sudo systemctl stop ${_bot_service_name}
sudo systemctl start ${_bot_service_name}

EOF

# Create, enable and start systemd service

sudo cat << EOF > "${_bot_service_path}"
[Unit]
Description=${_bot_name}
After=network.target

[Service]
User=${_user}
Group=${_group}
Type=simple
ExecStart=${_runbotsh_path}
Restart=always
RestartSec=10

[Install]
WantedBy=default.target

EOF

sudo systemctl daemon-reload

sudo systemctl enable ${_bot_service_name}

sudo systemctl start ${_bot_service_name}

# Schedule a cron job to restart bot daily

crontab -l > "${_cron_file_name}" # backup cron jobs to temp file

echo "45 6 * * * ${_runrestartsh_path}" >> "${_cron_file_name}"

crontab "${_cron_file_name}"

rm "${_cron_file_name}"

# Finalize

popd > /dev/null

echo "Done."
exit 0
