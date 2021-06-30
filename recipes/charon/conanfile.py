#  Copyright (c) 2021 Jelle Spijker
#  Cura is released under the terms of the LGPLv3 or higher.
import os

from conans import ConanFile, tools, CMake, VisualStudioBuildEnvironment
# from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake

class CharonConan(ConanFile):
    name = "Charon"
    version = "master"
    license = "LGPL-3.0"
    author = "Ultimaker B.V."
    url = "https://github.com/Ultimaker/libCharon"
    description = "File metadata and streaming library"
    topics = ("conan", "python", "cura", "ufp")
    settings = "os", "compiler", "build_type", "arch"
    generators = "virtualrunenv"
    options = {
        "python_version": "ANY"
    }
    default_options = {
        "python_version": "3.8"
    }
    _source_subfolder = "sharon-src"

    scm = {
        "type": "git",
        "subfolder": _source_subfolder,
        "url": f"{url}.git",
        "revision": version
    }

    _cmake = None

    def source(self):
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "set(CHARON_INSTALL_PATH lib${LIB_SUFFIX}/python${Python3_VERSION_MAJOR}.${Python3_VERSION_MINOR}/site-packages)", "set(CHARON_INSTALL_PATH site-packages)")

    def _configure_cmake(self, visual_studio = False):
        if self._cmake:
            return self._cmake
        if visual_studio:
            self._cmake = CMake(self, make_program = "nmake", append_vcvars = True)
        else:
            self._cmake = CMake(self)
        self._cmake.definitions["CURA_PYTHON_VERSION"] = self.options.python_version
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
        self.copy("*", src = os.path.join("package", "site-packages"), dst = "site-packages")

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "site-packages"))

    def package_id(self):
        self.info.header_only()

    def deploy(self):
        self.copy("LICENSE", dst = "licenses", src = self._source_subfolder)
