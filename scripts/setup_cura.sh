#!/bin/bash

python$2 -m venv $1
source $1/bin/activate
python -m pip install wheel
python -m pip install -r cura_requirements.txt
deactivate
conan install ../recipes/cura -if $1/conan --build=missing -o python_version=$2 -pr ../profiles/linux/release_17
