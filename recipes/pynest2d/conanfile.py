#  Copyright (c) 2021 Jelle Spijker
#  Cura is released under the terms of the LGPLv3 or higher.
import os

from conans import ConanFile, tools
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake


class pynest2dConan(ConanFile):
    name = "pynest2d"
    version = "modernize_build"
    license = "LGPL-3.0"
    author = "Ultimaker B.V."
    url = "https://github.com/Ultimaker/pynest2d"
    description = "Python bindings for libnest2d"
    topics = ("conan", "cura", "prusaslicer", "nesting", "c++", "bin packaging", "python", "sip")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "python_version": "ANY"
    }
    default_options = {
        "shared": False,
        "python_version": "3.8"
    }
    _source_subfolder = "pynest2d-src"

    scm = {
        "type": "git",
        "subfolder": _source_subfolder,
        "url": f"{url}.git",
        "revision": version
    }

    _cmake = None

    def build_requirements(self):
        self.build_requires("cmake/[>=3.16.2]")

    def requirements(self):
        self.requires("SIP/[>=4.19.24]@ultimaker/testing")
        self.requires(f"libnest2d/master@ultimaker/testing")

    def configure(self):
        self.options["SIP"].python_version = self.options.python_version
        if self.settings.compiler == 'Visual Studio':
            del self.options.fPIC

    def generate(self):
        cmake = CMakeDeps(self)
        cmake.generate()

        tc = CMakeToolchain(self)
        tc.variables["SIP_MODULE_SITE_PATH"] = "site-packages"
        tc.generate()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(source_folder = os.path.join(self.source_folder, self._source_subfolder))
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", dst = "licenses", src = self._source_subfolder)
        self.copy("pynest2d.*", src = "site-packages", dst = "site-packages")

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "site-packages"))
