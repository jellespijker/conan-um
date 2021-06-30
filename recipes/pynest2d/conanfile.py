#  Copyright (c) 2021 Jelle Spijker
#  Cura is released under the terms of the LGPLv3 or higher.
import os

from conans import ConanFile, tools, CMake, VisualStudioBuildEnvironment
# from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake

class pynest2dConan(ConanFile):
    name = "pynest2d"
    version = "master"
    license = "LGPL-3.0"
    author = "Ultimaker B.V."
    url = "https://github.com/Ultimaker/pynest2d"
    description = "Python bindings for libnest2d"
    topics = ("conan", "cura", "prusaslicer", "nesting", "c++", "bin packaging", "python", "sip")
    settings = "os", "compiler", "build_type", "arch"
    generators = "virtualrunenv", "cmake_find_package"
    options = {
        "shared": [True, False],
        "python": [True, False],
        "examples": [True, False],
        "python_version": "ANY"
    }
    default_options = {
        "shared": True,
        "python": True,
        "examples": False,
        "python_version": "3.8"
    }
    _source_subfolder = "arcus-src"

    scm = {
        "type": "git",
        "subfolder": _source_subfolder,
        "url": f"{url}.git",
        "revision": version
    }

    _cmake = None

    def requirements(self):
        self.requires("SIP/4.19.25@ultimaker/testing")
        self.requires(f"libnest2d/{self.version}@ultimaker/testing")

    def source(self):
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "project(pynest2d)", """project(pynest2d)\nlist(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_BINARY_DIR})""")
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "find_package(Python3 3.5 REQUIRED COMPONENTS Interpreter Development)", f"""find_package(Python3 EXACT {self.options.python_version} REQUIRED COMPONENTS Interpreter Development)""")
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), """find_package(Clipper REQUIRED)  # Dependency of libnest2d.
find_package(NLopt REQUIRED)  # Dependency of libnest2d.
find_package(Boost REQUIRED)  # Dependency of libnest2d.
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DLIBNEST2D_GEOMETRIES_clipper -DLIBNEST2D_OPTIMIZERS_nlopt -DLIBNEST2D_THREADING_std")  # Tell libnest2d to use Clipper and NLopt, and standard threads.""", "")

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
        self._cmake.definitions["BUILD_PYTHON"] = self.options.python
        self._cmake.definitions["BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["BUILD_EXAMPLES"] = self.options.examples
        self._cmake.definitions["SIP_MODULE_SITE_PATH"] = os.path.join(self.build_folder, "site-packages")
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
        self.copy("pynest2d.so", src = "site-packages", dst = "site-packages")

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "site-packages"))
