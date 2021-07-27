@echo off
cd ../recipes
FOR %%d IN (
    sip
    arcus
    charon
    savitar
    libnest2d
    pynest2d
    uranium
    curaengine
    cura
    ) do (
    cd %%d
    conan export . ultimaker/testing
    cd ..
)

cd ../generators
for %%g in (
    pycharm_run
    virtualenv_ultimaker
    ) do (
    cd %%g
    conan export . ultimaker/testing
    cd ..
    )
cd ../scripts