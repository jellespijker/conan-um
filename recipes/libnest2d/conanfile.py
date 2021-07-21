#  Copyright (c) 2021 Jelle Spijker
#  Cura is released under the terms of the LGPLv3 or higher.
import os

from conans import ConanFile, tools, CMake, VisualStudioBuildEnvironment

class libnest2dConan(ConanFile):
    name = "libnest2d"
    version = "master"
    license = "LGPL-3.0"
    author = "Ultimaker B.V."
    url = "https://github.com/Ultimaker/libnest2d"
    description = "2D irregular bin packaging and nesting library written in modern C++"
    topics = ("conan", "cura", "prusaslicer", "nesting", "c++", "bin packaging")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_find_package"
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
        if self.options.tests:
            self.build_requires("catch2/2.13.6")

    def requirements(self):
        if self.options.extern_clipper and self.options.geometries == "clipper":
            self.requires("clipper/6.4.2")
        if self.options.extern_boost:
            self.requires("boost/1.70.0")
        if self.options.extern_nlopt and self.options.optimizer == "nlopt":
            self.requires("nlopt/2.7.0")

    def source(self):
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "project(Libnest2D)", """project(Libnest2D)\nlist(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_BINARY_DIR})""")
        if self.options.extern_clipper and self.options.geometries == "clipper":
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "include", "libnest2d", "backends", "clipper", "CMakeLists.txt"), "require_package(Clipper", "require_package(polyclipping")
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "include", "libnest2d", "backends", "clipper", "CMakeLists.txt"), "target_link_libraries(clipperBackend INTERFACE Clipper::Clipper)", "target_link_libraries(clipperBackend INTERFACE polyclipping::polyclipping)")
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "include", "libnest2d", "backends", "clipper", "clipper_polygon.hpp"), "#include <clipper.hpp>", "#include <polyclipping/clipper.hpp>")

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            del self.options.fPIC

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        if self.settings.compiler == "Visual Studio":
            self._cmake = CMake(self, make_program = "nmake", append_vcvars = True)
        else:
            self._cmake = CMake(self)
        self._cmake.definitions["LIBNEST2D_HEADER_ONLY"] = self.options.header_only
        if self.options.header_only:
            self._cmake.definitions["BUILD_SHARED_LIBS"] = False
        else:
            self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        self._cmake.definitions["LIBNEST2D_BUILD_UNITTESTS"] = self.options.tests
        self._cmake.definitions["LIBNEST2D_GEOMETRIES"] = self.options.geometries
        self._cmake.definitions["LIBNEST2D_OPTIMIZER"] = self.options.optimizer
        self._cmake.definitions["LIBNEST2D_THREADING"] = self.options.threading
        self._cmake.configure(source_folder = self._source_subfolder)
        return self._cmake

    def build(self):
        with tools.chdir(os.path.join(self.source_folder, self._source_subfolder)):
            if self.settings.compiler == "Visual Studio":
                env_build = VisualStudioBuildEnvironment(self)
                with tools.environment_append(env_build.vars):
                    vcvars = tools.vcvars_command(self.settings)
                    self._cmake = self._configure_cmake()
                    self._cmake.build()
                    if self.options.tests:
                        self._cmake.test()
                    self._cmake.install()
            else:
                self._cmake = self._configure_cmake()
                self._cmake.build()
                if self.options.tests:
                    self._cmake.test()
                self._cmake.install()

    def package(self):
        self.copy("LICENSE", dst = "licenses", src = self._source_subfolder)
        self.copy("*", src = os.path.join("package", "include"), dst = "include")
        self.copy("libnest2d_*.*", src = os.path.join("package", "lib"), dst = "lib")

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
