#!/bin/bash

echo "Installing ..."

build_dir="build/output"

# Will want this as optionial input argument
install_dir="/Volumes/CIRCUITPY"

if [[ ! -d ${build_dir} ]]; then
    echo "Run build.sh before install.sh"
fi

if [[ ! $(which circup) ]]; then
    python3 -m pip install circup
fi 

cp -rp ${build_dir} ${install_dir}

pushd ${install_dir}
circup install --auto-file main.py
popd
