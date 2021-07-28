#  Copyright (c) 2021 Jelle Spijker
#  Cura is released under the terms of the LGPLv3 or higher.
import os

from conans import ConanFile, tools
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake

class ArcusConan(ConanFile):
    name = "Arcus"
    version = "modernize_build"
    license = "LGPL-3.0"
    author = "Ultimaker B.V."
    url = "https://github.com/Ultimaker/libArcus"
    description = "Communication library between internal components for Ultimaker software"
    topics = ("conan", "python", "binding", "sip", "cura", "protobuf", "c++")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "python": [True, False],
        "examples": [True, False],
        "python_version": "ANY"
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "python": True,
        "examples": True,
        "python_version": "3.8"
    }
    _source_subfolder = "arcus-src"

    scm = {
        "type": "git",
        "subfolder": _source_subfolder,
        "url": f"{url}.git",
        "revision": version
    }
    site_packages_folder = "site-packages"
    _cmake = None

    def build_requirements(self):
        self.build_requires("cmake/[>=3.16.2]")

    def requirements(self):
        if self.settings.os == "Windows" and  self.settings.compiler == "gcc":
            self.options.python = False
        if self.options.python:
            self.requires("SIP/[>=4.19.24]@ultimaker/testing")
        self.requires("protobuf/[>=3.15.5]")

    def configure(self):
        if self.options.python:
            self.options["SIP"].python_version = self.options.python_version
        self.options["protobuf"].shared = not self.settings.os == "Macos"
        if self.settings.compiler == "Visual Studio":
            del self.options.fPIC

    def generate(self):
        cmake = CMakeDeps(self)
        cmake.generate()

        tc = CMakeToolchain(self)
        tc.variables["BUILD_PYTHON"] = self.options.python
        tc.variables["BUILD_STATIC"] = not self.options.shared
        tc.variables["BUILD_EXAMPLES"] = self.options.examples
        tc.variables["Python_VERSION"] = self.options.python_version
        tc.variables["SIP_MODULE_SITE_PATH"] = self.site_packages_folder
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
        self.copy("LICENSE", dst = "licenses")
        self.copy("*", src = "site-packages", dst = self.site_packages_folder)
        self.copy("*", src = os.path.join("package", "include"), dst = "include")
        self.copy("*", src = os.path.join("package", "lib"), dst = "lib")
        self.copy("*", src = os.path.join("package", "bin"), dst = "bin")
        if self.options.examples:
            self.copy("example", src = "examples", dst = "bin")
            self.copy("example_py.sh", src = "examples", dst = "bin")
            self.copy("example_pb2.py", src = "examples", dst = "bin")

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, self.site_packages_folder))
        self.cpp_info.defines.append("ARCUS")
        if not self.settings.os == "Windows":
            self.cpp_info.libs = ["libArcus.so"] if self.options.shared else ["libArcus.a"]
        else:
            self.cpp_info.libs = ["Arcus.dll"]
