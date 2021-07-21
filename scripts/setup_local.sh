#!/bin/bash

dep_walker="sip arcus charon savitar libnest2d pynest2d uranium cura"
cd ../recipes
for dep in $dep_walker; do
  cd $dep
  conan create . ultimaker/testing --build=missing -pr=release_17
  cd ..
done
cd recipes
