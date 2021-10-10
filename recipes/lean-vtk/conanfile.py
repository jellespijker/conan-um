#  Copyright (c) 2021 Jelle Spijker

import os

from conans import ConanFile, tools
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain

class LeanVTKConan(ConanFile):
    name = "LeanVTK"
    version = "1.0"
    description = "A minimal VTK file writer for triangle, quad, hex and tet meshes in 2D and 3D. Only C++ standard lib as dependencies"
    topics = ("conan", "vtk")
    license = "MIT"
    homepage = "https://github.com/mmorse1217/lean-vtk"
    url = "https://github.com/mmorse1217/lean-vtk"
    settings = "os", "compiler", "build_type", "arch"
    exports = "LICENSE*"
    options = {
        "build_testing": [True, False],
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "build_testing": False,
        "shared": True,
        "fPIC": False
    }
    scm = {
        "type": "git",
        "subfolder": ".",
        "url": f"{url}.git",
        "revision": "2e58a49"
    }

    def source(self):
        tools.replace_in_file(os.path.join(self.source_folder, "CMakeLists.txt"),
                                           "add_library(LeanVTK STATIC ${LeanVTK_SRC} ${LeanVTK_INC})",
                                           "add_library(LeanVTK ${LeanVTK_SRC} ${LeanVTK_INC})")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = self.options.build_testing
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("*", src = os.path.join(self.build_folder, "package"), dst = ".")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
