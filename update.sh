#!/bin/bash

echo "Updating ..."

# Will want this as optionial input argument
output_dir="/Volumes/CIRCUITPY"

cp -rp ${output_dir}/fonts ${PWD}
cp -rp ${output_dir}/colors ${PWD}
cp -rp ${output_dir}/display ${PWD}
cp -rp ${output_dir}/mlb_api/__init__.py ${PWD}/mlb_api
cp -rp ${output_dir}/main.py ${PWD}/main.py
