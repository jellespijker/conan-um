#  Copyright (c) 2021 Jelle Spijker
#  Cura is released under the terms of the LGPLv3 or higher.
import os

from conans import ConanFile, tools
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake

class CharonConan(ConanFile):
    name = "Charon"
    version = "master"
    license = "LGPL-3.0"
    author = "Ultimaker B.V."
    url = "https://github.com/Ultimaker/libCharon"
    description = "File metadata and streaming library"
    topics = ("conan", "python", "cura", "ufp")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "python_version": "ANY"
    }
    default_options = {
        "python_version": "3.8"
    }
    _source_subfolder = "charon-src"

    scm = {
        "type": "git",
        "subfolder": _source_subfolder,
        "url": f"{url}.git",
        "revision": version
    }

    _cmake = None

    def build_requirements(self):
        self.build_requires("cmake/[>=3.16.2]")

    def source(self):
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "set(CHARON_INSTALL_PATH lib${LIB_SUFFIX}/python${Python3_VERSION_MAJOR}.${Python3_VERSION_MINOR}/site-packages)", "set(CHARON_INSTALL_PATH site-packages)")

    def generate(self):
        cmake = CMakeDeps(self)
        cmake.generate()

        tc = CMakeToolchain(self)
        tc.variables["CURA_PYTHON_VERSION"] = self.options.python_version
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
        self.copy("*", src = os.path.join("package", "site-packages"), dst = "site-packages")

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "site-packages"))

    def package_id(self):
        self.info.header_only()
