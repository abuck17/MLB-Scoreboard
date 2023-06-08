#!/bin/bash

usage() { echo "Usage: $0 [-m (Convert to MicroPython)]" 1>&2; exit 1; }

micropython="false"

while getopts ":m" o; do
    case "${o}" in
        m)
            micropython="true"
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

echo "Building ..."

build_dir="build"

output_dir="${build_dir}/output"

if [[ -d ${output_dir} ]]; then
    rm -Rf ${output_dir}
fi

mkdir -p ${output_dir}

mkdir -p ${output_dir}/fonts
mkdir -p ${output_dir}/colors
mkdir -p ${output_dir}/display
mkdir -p ${output_dir}/mlb_api

cp -rp fonts ${output_dir}
cp -rp colors ${output_dir}
cp -rp display ${output_dir}
cp -rp mlb_api/__init__.py ${output_dir}/mlb_api
cp -rp main.py ${output_dir}/main.py

if [[ -f "secrets.py" ]]; then
    cp -rp secrets.py ${output_dir}/secrets.py
fi

circuit_dir="${build_dir}/circuitpython"

if ${micropython}; then
    if [[ ! -d ${circuit_dir} ]]; then
        git clone https://github.com/adafruit/circuitpython.git ${circuit_dir}
        pushd ${circuit_dir}
        make fetch-submodules
        cd mpy-cross
        make
        popd
    fi
    for pyfile in $(find build/output/ -name "*.py" | grep -v "main.py\|secrets.py"); do
        ./${circuit_dir}/mpy-cross/mpy-cross ${pyfile}
        rm ${pyfile}
    done
fi


