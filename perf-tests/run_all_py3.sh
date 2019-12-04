#!/bin/bash

report_date=$(date '+%Y-%m-%d_%H:%M:%S')
# shellcheck disable=SC2164  # no check if cd fails
own_dir="$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )"  # this gives the full path to myself, even for sourced scripts

# so this is working even if the script is called from another directory
"${own_dir}/run_memory.sh" py3 "${report_date}"
"${own_dir}/run_speed.sh" py3 "${report_date}"
