#!/bin/bash

output_dir="/Volumes/CIRCUITPY/"

mkdir ${output_dir}/lib
mkdir ${output_dir}/fonts
mkdir ${output_dir}/colors
mkdir ${output_dir}/mlb_api

cp -rp fonts ${output_dir}
cp -rp colors ${output_dir}
cp -rp mlb_api/__init__.py ${output_dir}/mlb_api
cp -rp secrets.py ${output_dir}/secrets.py
cp -rp main.py ${output_dir}/main.py

pushd ${output_dir}
circup install --auto-file main.py

