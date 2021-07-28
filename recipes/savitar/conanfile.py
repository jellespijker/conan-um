#  Copyright (c) 2021 Jelle Spijker
#  Cura is released under the terms of the LGPLv3 or higher.
import os

from conans import ConanFile, tools
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake

class SavitarConan(ConanFile):
    name = "Savitar"
    version = "master"
    license = "LGPL-3.0"
    author = "Ultimaker B.V."
    url = "https://github.com/Ultimaker/libSavitar"
    description = "libSavitar is a c++ implementation of 3mf loading with SIP python bindings"
    topics = ("conan", "python", "binding", "sip", "cura", "3mf", "c++")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_find_package"
    options = {
        "shared": [True, False],
        "python": [True, False],
        "tests": [True, False],
        "extern_pugixml": [True, False],
        "python_version": "ANY"
    }
    default_options = {
        "shared": False,
        "python": True,
        "tests": False,
        "extern_pugixml": True,
        "python_version": "3.8"
    }
    _source_subfolder = "savitar-src"

    scm = {
        "type": "git",
        "subfolder": _source_subfolder,
        "url": f"{url}.git",
        "revision": version
    }

    _cmake = None

    def build_requirements(self):
        self.build_requires("cmake/[>=3.16.2]")
        if self.options.tests:
            self.build_requires("gtest/[>=1.10.0]")

    def requirements(self):
        self.requires("SIP/[>=4.19.24]@ultimaker/testing")
        if self.options.extern_pugixml:
            self.requires("pugixml/[>=1.11]")

    def source(self):
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "project(savitar)", """project(savitar)\nlist(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_BINARY_DIR})""")
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "find_package(Python3 3.4 REQUIRED COMPONENTS Interpreter Development)", f"""find_package(Python3 EXACT {self.options.python_version} REQUIRED COMPONENTS Interpreter Development)""")
        if self.options.extern_pugixml:
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "add_subdirectory(pugixml)", "")

    def configure(self):
        self.options["SIP"].python_version = self.options.python_version
        if self.settings.compiler == 'Visual Studio':
            self.options.extern_pugixml = False  # FIXME: for Windows
            del self.options.fPIC

    def generate(self):
        cmake = CMakeDeps(self)
        cmake.generate()

        tc = CMakeToolchain(self)
        tc.variables["BUILD_PYTHON"] = self.options.python
        tc.variables["BUILD_STATIC"] = not self.options.shared
        tc.variables["BUILD_TESTS"] = self.options.tests
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
        self.copy("*", src = "site-packages", dst = "site-packages")
        self.copy("*", src = os.path.join("package", "include"), dst = "include")
        self.copy("*", src = os.path.join("package", "lib"), dst = "lib")

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "site-packages"))
        if self.settings.os == "Linux":
            self.cpp_info.libs = ["libSavitar.so"] if self.options.shared else ["libSavitar.a"]
        elif self.settings.os == "Windows":
            self.cpp_info.libs = ["Savitar.dll"] if self.options.shared else ["Savitar.lib"]
        elif self.settings.os == "Macos":
            self.cpp_info.libs = ["libSavitar.dylib"] if self.options.shared else ["libSavitar.a"]
