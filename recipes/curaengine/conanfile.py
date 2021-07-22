#  Copyright (c) 2021 Jelle Spijker
#  Cura is released under the terms of the LGPLv3 or higher.
import os

from conans import ConanFile, tools, CMake, VisualStudioBuildEnvironment
# from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake

class libnest2dConan(ConanFile):
    name = "CuraEngine"
    version = "CURA-5990_cpp17"
    license = "AGPL-3.0"
    author = "Ultimaker B.V."
    url = "https://github.com/Ultimaker/CuraEngine"
    description = "Powerful, fast and robust engine for converting 3D models into g-code instructions for 3D printers. It is part of the larger open source project Cura."
    topics = ("conan", "cura", "protobuf", "gcode", "c++", "curaengine", "libarcus", "gcode-generation")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_find_package"
    options = {
        "enable_arcus": [True, False],
        "tests": [True, False],
        "extern_clipper": [True, False],
        "extern_rapidjson": [True, False]
    }
    default_options = {
        "enable_arcus": True,
        "tests": False,
        "extern_clipper": True,
        "extern_rapidjson": True
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
        if self.options.tests:
            self.build_requires("gtest/1.10.0")

    def requirements(self):
        if self.options.enable_arcus:
            self.requires(f"Arcus/master@ultimaker/testing")
            self.requires("protobuf/3.17.1")
        self.requires("stb/20200203")
        if self.options.extern_clipper:
            self.requires("clipper/6.4.2")
        if self.options.extern_rapidjson:
            self.requires("rapidjson/1.1.0")

    def source(self):
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "project(CuraEngine)", "project(CuraEngine)\nlist(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_BINARY_DIR})")
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "find_package(Stb REQUIRED)", "find_package(stb REQUIRED)")
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "include_directories(${Stb_INCLUDE_DIRS})", "include_directories(${stb_INCLUDE_DIRS})")
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "src", "infill", "ImageBasedDensityProvider.cpp"), "#include <stb/stb_image.h>", "#include <stb_image.h>")
        if self.options.enable_arcus:
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "target_link_libraries(_CuraEngine Arcus)", "target_link_libraries(_CuraEngine Arcus)\n\ttarget_link_libraries(_CuraEngine protobuf::protobuf)")

        if self.options.extern_clipper:
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "find_package(Polyclipping", "find_package(polyclipping")
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "include_directories(${Polyclipping_INCLUDE_DIRS}", "include_directories(${polyclipping_INCLUDE_DIRS}")
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "target_link_libraries(_CuraEngine ${Polyclipping_LIBRARIES})", "target_link_libraries(_CuraEngine ${polyclipping_LIBRARIES})")
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "src", "utils", "Coord_t.h"), "#include <clipper.hpp>", "#include <polyclipping/clipper.hpp>")
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "src", "raft.cpp"), "#include <clipper.hpp>", "#include <polyclipping/clipper.hpp>")
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "tests", "utils", "AABB3DTest.cpp"), "#include <clipper.hpp>", "#include <polyclipping/clipper.hpp>")
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "tests", "utils", "AABBTest.cpp"), "#include <clipper.hpp>", "#include <polyclipping/clipper.hpp>")
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "src", "utils", "IntPoint.h"), "#include <clipper.hpp>", "#include <polyclipping/clipper.hpp>")
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "src", "utils", "polygon.h"), "#include <clipper.hpp>", "#include <polyclipping/clipper.hpp>")
        if self.options.extern_rapidjson:
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "find_package(RapidJSON CONFIG REQUIRED)", "find_package(RapidJSON REQUIRED)")
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "${RAPIDJSON_INCLUDE_DIRS})", "${RapidJSON_INCLUDE_DIRS})")

    def configure(self):
        if self.settings.compiler == 'Visual Studio':
            del self.options.fPIC

    def _configure_cmake(self, visual_studio = False):
        if self._cmake:
            return self._cmake
        if visual_studio:
            self._cmake = CMake(self, make_program = "nmake", append_vcvars = True)
        else:
            self._cmake = CMake(self)
        self._cmake.definitions["USE_SYSTEM_LIBS"] = any((self.options.extern_clipper, self.options.extern_rapidjson))
        self._cmake.definitions["ENABLE_ARCUS"] = self.options.enable_arcus
        self._cmake.definitions["BUILD_TESTS"] = self.options.tests
        self._cmake.configure(source_folder = self._source_subfolder)
        return self._cmake

    def build(self):
        with tools.chdir(os.path.join(self.source_folder, self._source_subfolder)):
            if self.settings.compiler == "Visual Studio":
                env_build = VisualStudioBuildEnvironment(self)
                with tools.environment_append(env_build.vars):
                    vcvars = tools.vcvars_command(self.settings)
                    self._cmake = self._configure_cmake(visual_studio = True)
                    self._cmake.build()
                    self._cmake.install()
            else:
                self._cmake = self._configure_cmake()
                self._cmake.build()
                self._cmake.install()

    def package(self):
        self.copy("LICENSE", dst = "licenses", src = self._source_subfolder)
        self.copy("CuraEngine", src = os.path.join("package", "bin"), dst = "bin")

    def package_info(self):
        self.env_info.path.append(os.path.join(self.package_folder, "bin"))
