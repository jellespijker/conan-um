# Cura Conan recipes

WIP

# Run Cura from source

## Linux

**Requirements**
1. Python 3.8 or higher (we're currently using 3.8.10)
2. Conan https://docs.conan.io/en/latest/installation.html
3. GCC with support for C++17 (only tested with GCC 11.1.0 for now)

**Steps**
0. Prepare Cura
    ```bash
    mkdir -p dev && cd dev
    git clone https://github.com/Ultimaker/Cura.git
    git clone https://github.com/Ultimaker/fdm_materials.git
    mkdir -p Cura/resources/materials
    ln -s fdm_materials Cura/resources/materials/fdm_materials
    ```
1. Clone this repo
    ```bash
       git clone https://github.com/jellespijker/conan-um.git
       cd conan-um
    ```
2. Copy Conan profiles to `cp profiles/linux/* .conan/profiles/`
3. Export the recipes in this repo to the local cache, so they can be used
    ```bash
    cd scripts
    chmod +x setup_local.sh
    ./setup_locah.sh
    ```
4. Setup a virtual python Environment for Cura. *The Python version is optional, if not specified it will use the systems Python version*.
This script will create a virtual environment, it will install the normal Python dependencies. and it will then build all C++/SIP/Python repositories and their required dependencies. If the dependencies aren't in the local cache it should download them and build them if there aren't any binaries available online. **The first run will probably take a while**.
    ```bash
    chmod +x setup_cura.sh
    ./setup_local.sh <path_to_your_new_venv> <major_python_version.minor_python_version>
    ```
5. Start up Cura
   1. From bash
    ```bash
    cd ../../Cura
    source <path_to_your_new_venv>/bin/activate
    ln -s $CURAENGINEPATH CuraEngine
    python cura_app.py
    ```
    2. From PyCharm
    ```bash
    cd ../../Cura
    mkdir -p .run
    ln -s <path_to_your_new_venv>/bin/Cura.app.xml Cura/.run/Cura.app.xml
    ln -s $CURAENGINEPATH CuraEngine
    ```
   Open the Cura folder in PyCharm and run the **Cura** configuration

> **NOTE:**  
> The symbolic link solution is a temporary fix 
