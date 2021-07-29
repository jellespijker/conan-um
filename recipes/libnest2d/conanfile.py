#  Copyright (c) 2021 Jelle Spijker
#  Cura is released under the terms of the LGPLv3 or higher.
import os
import pathlib

from conans import ConanFile, tools
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conan.tools.layout import LayoutPackager
from conan.tools.files import apply_conandata_patches

class libnest2dConan(ConanFile):
    name = "libnest2d"
    version = "4.10.0"
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
        "geometries": ["clipper", "boost", "eigen"],
        "optimizer": ["nlopt", "optimlib"],
        "threading": ["std", "tbb", "omp", "none"]
    }
    default_options = {
        "shared": False,
        "tests": True,
        "header_only": False,
        "geometries": "clipper",
        "optimizer": "nlopt",
        "threading": "std"
    }
    exports = "0001-cst17.patch", "0002-link_to_polyclipping.patch", "0003-find_polyclipping.patch", "0004-header_polyclipping.patch"
    scm = {
        "type": "git",
        "subfolder": ".",
        "url": "https://github.com/Ultimaker/libnest2d.git",
        "revision": "031e4e61218edd092fbc54fbc6df145287b628ba"
    }

    def build_requirements(self):
        self.build_requires("cmake/[>=3.16.2]")
        if self.options.tests:
            self.build_requires("catch2/[>=2.13.6]", force_host_context=True)

    def requirements(self):
        if self.options.geometries == "clipper":
            self.requires("clipper/[>=6.4.2]")
            self.requires("boost/1.70.0")
        elif self.options.geometries == "eigen":
            self.requires("eigen/[>=3.3.7]")
        if self.options.optimizer == "nlopt":
            self.requires("nlopt/[>=2.7.0]")

    def source(self):
        self.scm = self.conan_data["sources"][self.version]
        apply_conandata_patches(self)

    def layout(self):
        # The sources can be found in the root dir
        self.folders.source = "."

        # The build folder is created with the CLion way
        # TODO: Take into account different compilers
        self.folders.build = f"cmake-build-{self.settings.build_type}".lower()

        # In case we use "conan package" we declare an output directory
        self.folders.package = f"package-{self.settings.build_type}".lower()
        self.folders.imports = self.folders.build

        # INFOS
        self.cpp.source.includedirs = ["include"]
        self.cpp.build.libdirs = ["."]
        self.cpp.build.libs = [f"libnest2d_{self.options.geometries}_{self.options.optimizer}"]
        self.cpp.package.libs = [f"libnest2d_{self.options.geometries}_{self.options.optimizer}"]

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            del self.options.fPIC

    def generate(self):
        cmake = CMakeDeps(self)
        cmake.generate()

        tc = CMakeToolchain(self)
        tc.blocks["generic_system"].values["generator_platform"] = None
        tc.blocks["generic_system"].values["toolset"] = None
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

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        LayoutPackager(self).package()
