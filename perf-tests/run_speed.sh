#!/bin/bash
# $1 the prefix to the report filenames
# $2 the report_date

function is_bash_function_declared {
    # checks if the function is declared
    # $1 : function name
    local function_name="${1}"
    declare -F "${function_name}" &>/dev/null && return 0 || return 1
}

function is_valid_command {
    #
    # $1 : any bash internal command, external command or function name
    local command
    command="${1}"

    if [[ "$(type -t "${command}")" == "builtin" ]]; then return 0; fi  # builtin command
    if is_bash_function_declared "${command}"; then return 0; fi        # declared function
    if [[ -n "$(type -p "${command}")" ]]; then return 0; fi            # external command
    return 1
}

function get_python_interpreter {
    # usually the python 3 interpreter is named "python3" on ubuntu
    # if not - fall back to "python"
    if is_valid_command "python3"; then
        echo "python3"
    else
        echo "python"
    fi
}


# set the date to the first parameter given, or, if nt, to the actual date
# this is to have the same date for all reports created with run_all_py3.sh
if [[ -z "${2+xxx}" ]]; then
    echo "date not set as parameter, using actual date"
    report_date=$(date '+%Y-%m-%d_%H:%M:%S')
else
    report_date="${2}"
fi

# shellcheck disable=SC2164  # no check if cd fails
own_dir="$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )"  # this gives the full path to myself, even for sourced scripts

# prepend the development directory to PYTHONPATH, otherwise arpeggio will not be found,
# or just the pip installed version is used - not practical during development
dev_dir="$(dirname "${own_dir}")"     # one level up
export PYTHONPATH="${dev_dir}":"${PYTHONPATH}"
python_interpreter=$(get_python_interpreter)

mkdir -p "${own_dir}/reports"

"${python_interpreter}" --version > "${own_dir}/reports/${1}_${report_date}_speed_report.txt" 2>&1
"${python_interpreter}" "${own_dir}/test_speed.py" >> "${own_dir}/reports/${1}_${report_date}_speed_report.txt"
