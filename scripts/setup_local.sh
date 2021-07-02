#!/bin/bash

dep_walker="sip arcus charon savitar libnest2d pynest2d curaengine uranium cura"
cd ../recipes
for dep in $dep_walker; do
  cd $dep
  conan create . ultimaker/testing --build=missing -pr=release_11
  cd ..
done
