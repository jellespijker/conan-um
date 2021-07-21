#!/bin/bash

dep_walker="sip arcus charon savitar libnest2d pynest2d uranium curaengine cura"
cd ../recipes
for dep in $dep_walker; do
  cd $dep
  conan export . ultimaker/testing
  cd ..
done

gen_walker="pycharm_run virtualenv_ultimaker"
cd ../generators
for dep in gen_walker; do
  cd $dep
  conan export . ultimaker/testing
  cd ..
done
