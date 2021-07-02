"""Setup Ultimaker Cura

Usage:
  cura_conan.py PATH PYTHON_VERSION
  cura_conan.py (-h | --help)
  cura_conan.py --version

Options:
  -u --upgrade  upgrade an existing virtual environment. [default: True]
  -h --help     Show this screen.
  --version     Show version.

"""
from docopt import docopt
import os
import json
import shutil
import re

def copytree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                shutil.copy2(s, d)

def setup_cura(args):
    python_version = args["PYTHON_VERSION"]
    venv_path = args["PATH"]
    site_package_path = os.path.join(venv_path, "lib", f"python{python_version}", "site-packages")
    conan_path = os.path.join(venv_path, "conan")
    with open(os.path.join(conan_path, "conanbuildinfo.json"), "r") as f:
        conanbuildinfo = json.loads(f.read())

    site_packages = conanbuildinfo["deps_env_info"]["PYTHONPATH"]
    pythonpath = ":".join(site_packages)
    # for site_package in site_packages:
    #     print(f"Copying: {site_package} into: {site_package_path}")
    #     copytree(site_package, site_package_path)

    paths = []
    for dep in conanbuildinfo["dependencies"]:
        print(f"Adding {dep['name']} paths to venv PATH")
        for lib_path in dep["lib_paths"]:
            paths.append(lib_path)
        for bin_path in dep["bin_paths"]:
            paths.append(bin_path)

    conan_paths = ":".join(paths)
    with open(os.path.join(venv_path, "bin", "activate"), "r") as f:
        content = f.read()
    if "CONAN_PATH" in content:
        conent = content.splitlines()[2:]
    content_new = f"CONAN_PATH={conan_paths}\n"
    content_new += f"export PYTHONPATH={pythonpath}\n"
    content_new += content.replace(r"VIRTUAL_ENV/bin:$PATH", r"VIRTUAL_ENV/bin:\$PATH:$CONAN_PATH")
    with open(os.path.join(venv_path, "bin", "activate"), "w") as f:
        f.write(content_new)

if __name__ == '__main__':
    arguments = docopt(__doc__, version='0.1')
    setup_cura(arguments)
