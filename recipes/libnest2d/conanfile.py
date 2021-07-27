#  Copyright (c) 2021 Jelle Spijker
#  Cura is released under the terms of the LGPLv3 or higher.
import os

from conans import ConanFile, tools
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake

class libnest2dConan(ConanFile):
    name = "libnest2d"
    version = "master"
    license = "LGPL-3.0"
    author = "Ultimaker B.V."
    url = "https://github.com/Ultimaker/libnest2d"
    description = "2D irregular bin packaging and nesting library written in modern C++"
    topics = ("conan", "cura", "prusaslicer", "nesting", "c++", "bin packaging")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "tests": [True, False],
        "header_only": [True, False],
        "extern_clipper": [True, False],
        "extern_boost": [True, False],
        "extern_nlopt": [True, False],
        "extern_gtest": [True, False],
        "geometries": ["clipper", "boost", "eigen"],
        "optimizer": ["nlopt", "optimlib"],
        "threading": ["std", "tbb", "omp", "none"]
    }
    default_options = {
        "shared": True,
        "tests": True,
        "header_only": False,
        "extern_clipper": True,
        "extern_boost": True,
        "extern_nlopt": True,
        "extern_gtest": True,
        "geometries": "clipper",
        "optimizer": "nlopt",
        "threading": "std"
    }
    _source_subfolder = "libnest2d-src"

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
            self.build_requires("catch2/[>=2.13.6]")

    def requirements(self):
        if self.options.extern_clipper and self.options.geometries == "clipper":
            self.requires("clipper/[>=6.4.2]")
        if self.options.extern_boost:
            self.requires("boost/1.70.0")
        if self.options.extern_nlopt and self.options.optimizer == "nlopt":
            self.requires("nlopt/[>=2.7.0]")

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            del self.options.fPIC

    def source(self):
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "project(Libnest2D)", """project(Libnest2D)\nlist(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_BINARY_DIR})""")
        if self.options.extern_clipper and self.options.geometries == "clipper":
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "include", "libnest2d", "backends", "clipper", "CMakeLists.txt"), "require_package(Clipper", "require_package(polyclipping")
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "include", "libnest2d", "backends", "clipper", "CMakeLists.txt"), "target_link_libraries(clipperBackend INTERFACE Clipper::Clipper)", "target_link_libraries(clipperBackend INTERFACE polyclipping::polyclipping)")
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "include", "libnest2d", "backends", "clipper", "clipper_polygon.hpp"), "#include <clipper.hpp>", "#include <polyclipping/clipper.hpp>")

    def generate(self):
        cmake = CMakeDeps(self)
        cmake.generate()

        tc = CMakeToolchain(self)
        tc.variables["LIBNEST2D_HEADER_ONLY"] = self.options.header_only
        if self.options.header_only:
            tc.variables["BUILD_SHARED_LIBS"] = False
        else:
            tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["LIBNEST2D_BUILD_UNITTESTS"] = self.options.tests
        tc.variables["LIBNEST2D_GEOMETRIES"] = self.options.geometries
        tc.variables["LIBNEST2D_OPTIMIZER"] = self.options.optimizer
        tc.variables["LIBNEST2D_THREADING"] = self.options.threading
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
        self.copy("*", src = "include", dst = "include")
        self.copy("*", src = os.path.join("package", "bin"), dst = "bin")
        self.copy("*", src = os.path.join("package", "lib"), dst = "lib")

    def package_info(self):
        libname = f"nest2d_{self.options.geometries}_{self.options.optimizer}"
        if not self.settings.os == "Windows":
            self.cpp_info.libs = [f"lib{libname}.so"] if self.options.shared else [f"lib{libname}.a"]
        else:
            self.cpp_info.libs = [f"{libname}.dll"]
