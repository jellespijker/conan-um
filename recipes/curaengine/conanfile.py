#  Copyright (c) 2021 Jelle Spijker
#  Cura is released under the terms of the LGPLv3 or higher.
import os

from conans import ConanFile, tools
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake

class libnest2dConan(ConanFile):
    name = "CuraEngine"
    version = "master"
    license = "AGPL-3.0"
    author = "Ultimaker B.V."
    url = "https://github.com/Ultimaker/CuraEngine"
    description = "Powerful, fast and robust engine for converting 3D models into g-code instructions for 3D printers. It is part of the larger open source project Cura."
    topics = ("conan", "cura", "protobuf", "gcode", "c++", "curaengine", "libarcus", "gcode-generation")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "enable_arcus": [True, False],
        "enable_openmp": [True, False],
        "tests": [True, False],
        "extern_clipper": [True, False],
        "extern_rapidjson": [True, False],
        "python_version": "ANY"
    }
    default_options = {
        "enable_arcus": True,
        "enable_openmp": True,
        "tests": False,
        "extern_clipper": True,
        "extern_rapidjson": True,
        "python_version": "3.8"
    }
    _source_subfolder = "curaengine-src"

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
        self.requires("stb/20200203")
        if self.options.enable_arcus:
            self.requires(f"Arcus/modernize_build@ultimaker/testing")
            self.requires("protobuf/[>=3.15.5]")
        if self.options.extern_clipper:
            self.requires("clipper/[>=6.4.2]")
        if self.options.extern_rapidjson:
            self.requires("rapidjson/[>=1.1.0]")

    def source(self):
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "project(CuraEngine)", "project(CuraEngine)\nlist(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_BINARY_DIR})")
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "find_package(Stb REQUIRED)", "find_package(stb REQUIRED)")
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "target_link_libraries(_CuraEngine pthread)", "target_link_libraries(_CuraEngine PUBLIC pthread)")
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "include_directories(${Stb_INCLUDE_DIRS})", "include_directories(${stb_INCLUDE_DIRS_RELEASE})")
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "src", "infill", "ImageBasedDensityProvider.cpp"), "#include <stb/stb_image.h>", "#include <stb_image.h>")
        if self.options.enable_arcus:
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "target_link_libraries(_CuraEngine Arcus)", "target_link_libraries(_CuraEngine PUBLIC Arcus::Arcus)\n\ttarget_link_libraries(_CuraEngine PUBLIC protobuf::protobuf)")
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "add_definitions(-DARCUS)", "")

        if self.options.extern_clipper:
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "find_package(Polyclipping", "find_package(polyclipping")
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "include_directories(${Polyclipping_INCLUDE_DIRS}", "include_directories(${polyclipping_INCLUDE_DIRS_RELEASE}")
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "target_link_libraries(_CuraEngine ${Polyclipping_LIBRARIES})", "target_link_libraries(_CuraEngine PUBLIC polyclipping::polyclipping)")
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "target_link_libraries(_CuraEngine clipper)", "target_link_libraries(_CuraEngine PUBLIC polyclipping::polyclipping)")
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "src", "utils", "Coord_t.h"), "#include <clipper.hpp>", "#include <polyclipping/clipper.hpp>")
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "src", "raft.cpp"), "#include <clipper.hpp>", "#include <polyclipping/clipper.hpp>")
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "tests", "utils", "AABB3DTest.cpp"), "#include <clipper.hpp>", "#include <polyclipping/clipper.hpp>")
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "tests", "utils", "AABBTest.cpp"), "#include <clipper.hpp>", "#include <polyclipping/clipper.hpp>")
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "src", "utils", "IntPoint.h"), "#include <clipper.hpp>", "#include <polyclipping/clipper.hpp>")
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "src", "utils", "polygon.h"), "#include <clipper.hpp>", "#include <polyclipping/clipper.hpp>")
        if self.options.extern_rapidjson:
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "${RAPIDJSON_INCLUDE_DIRS})", "${rapidjson_INCLUDE_DIRS_RELEASE})")

    def configure(self):
        if self.settings.os == "Windows" and self.options.enable_arcus:
            self.options["Arcus"].python = False
        else:
            self.options["Arcus"].python_version = self.options.python_version
        self.options["protobuf"].shared = True
        if self.settings.compiler == 'Visual Studio':
            del self.options.fPIC

    def generate(self):
        cmake = CMakeDeps(self)
        cmake.generate()

        tc = CMakeToolchain(self)
        tc.variables["USE_SYSTEM_LIBS"] = any((self.options.extern_clipper, self.options.extern_rapidjson))
        tc.variables["ENABLE_ARCUS"] = self.options.enable_arcus
        tc.variables["BUILD_TESTS"] = self.options.tests
        tc.variables["ENABLE_OPENMP"] = self.options.enable_openmp
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
        self.copy("CuraEngine", src = os.path.join("package", "bin"), dst = "bin")

    def package_info(self):
        self.env_info.path.append(os.path.join(self.package_folder, "bin"))
