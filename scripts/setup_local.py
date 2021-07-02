"""Setup local Ultimaker Cura repo

Usage:
  setup_local.py
  setup_local.py (-h | --help)
  setup_local.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.

"""
from docopt import docopt
import os
import subprocess

dep_walker = ["sip", "arcus", "charon", "savitar", "libnest2d", "pynest2d", "curaengine", "uranium", "cura"]

def setup_local(arguments):
    for recipe in dep_walker:
        recipe_path = os.path.join(os.getcwd(), "..", "recipes", recipe)
        if os.path.isdir(recipe_path):
            print(f"Setting up: {recipe}")
            os.chdir(recipe_path)
            process = subprocess.Popen(["conan", "create", ".", "ultimaker/testing", "--build=missing", "-pr=release_11"],
                     stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            print(stdout.decode())
            print(stderr.decode())


if __name__ == '__main__':
    arguments = docopt(__doc__, version='0.1')
    setup_local(arguments)
