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

for dir_path in $(find ${install_dir} -type d -mindepth 1 -maxdepth 1); do
    rm -Rf ${dir_path}
done
cp -rp ${build_dir}/* ${install_dir}

pushd ${install_dir}
circup install --auto-file main.py
popd
