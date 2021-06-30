#  Copyright (c) 2021 Jelle Spijker
#  Cura is released under the terms of the LGPLv3 or higher.
import os

from conans import ConanFile, tools, CMake, VisualStudioBuildEnvironment
# from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake

class CuraConan(ConanFile):
    name = "Cura"
    version = "master"
    license = "LGPL-3.0"
    author = "Ultimaker B.V."
    url = "https://github.com/Ultimaker/cura"
    description = "3D printer / slicing GUI built on top of the Uranium framework"
    topics = ("conan", "python", "pyqt5", "qt", "qml", "3d-printing", "slicer")
    settings = "os", "compiler", "build_type", "arch"
    generators = "virtualenv"
    options = {
        "python_version": "ANY"
    }
    default_options = {
        "python_version": "3.8"
    }
    _source_subfolder = "cura-src"

    scm = {
        "type": "git",
        "subfolder": _source_subfolder,
        "url": f"{url}.git",
        "revision": version
    }

    def configure(self):
        self.options["Arcus"].python_version = self.options.python_version
        self.options["Savitar"].python_version = self.options.python_version
        self.options["Uranium"].python_version = self.options.python_version
        self.options["pynest2d"].python_version = self.options.python_version

    def requirements(self):
        self.requires(f"Arcus/{self.version}@ultimaker/testing")
        self.requires(f"Charon/{self.version}@ultimaker/testing")
        self.requires(f"pynest2d/{self.version}@ultimaker/testing")
        self.requires(f"Savitar/{self.version}@ultimaker/testing")
        self.requires(f"Uranium/{self.version}@ultimaker/testing")
        self.requires(f"CuraEngine/{self.version}@ultimaker/testing")
