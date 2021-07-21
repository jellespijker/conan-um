#  Copyright (c) 2021 Jelle Spijker
#  Cura is released under the terms of the LGPLv3 or higher.
import os

from conans import ConanFile, tools, CMake, VisualStudioBuildEnvironment
# from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake

class UraniumConan(ConanFile):
    name = "Uranium"
    version = "master"
    license = "LGPL-3.0"
    author = "Ultimaker B.V."
    url = "https://github.com/Ultimaker/uranium"
    description = "A Python framework for building Desktop applications."
    topics = ("conan", "python", "pyqt5", "qt", "3d-graphics", "3d-models", "python-framework")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "python_version": "ANY"
    }
    default_options = {
        "python_version": "3.8"
    }
    _source_subfolder = "uranium-src"

    scm = {
        "type": "git",
        "subfolder": _source_subfolder,
        "url": f"{url}.git",
        "revision": version
    }

    _cmake = None

    def requirements(self):
        self.requires(f"Arcus/{self.version}@ultimaker/testing")

    def source(self):
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "project(uranium NONE)", "project(uranium NONE)\nlist(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_BINARY_DIR})")
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "find_package(PythonInterp 3 REQUIRED)", f"""find_package(Python3 EXACT {self.options.python_version} REQUIRED COMPONENTS Interpreter)""")
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "install(DIRECTORY UM DESTINATION lib${LIB_SUFFIX}/python${PYTHON_VERSION_MAJOR}.${PYTHON_VERSION_MINOR}/site-packages)", "install(DIRECTORY UM DESTINATION site-packages)")
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "cmake", "UraniumPluginInstall.cmake"), "find_package(Python3 REQUIRED COMPONENTS Interpreter)", "install(DIRECTORY UM DESTINATION site-packages)", f"find_package(Python3 EXACT {self.options.python_version} REQUIRED COMPONENTS Interpreter)")
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "cmake", "UraniumPluginInstall.cmake"), "DESTINATION lib${LIB_SUFFIX}/uranium/${_rel_plugin_parent_dir}", "DESTINATION site-packages/${_rel_plugin_parent_dir}")
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"), "install(DIRECTORY resources DESTINATION ${CMAKE_INSTALL_DATADIR}/uranium)", "install(DIRECTORY resources DESTINATION site-packages)")

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
        self.copy("*", src = os.path.join("package", "lib", "uranium"), dst = os.path.join("site-packages"))
        self.copy("*", src = os.path.join("package", "share"), dst = os.path.join("share"))

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "site-packages"))

    def package_id(self):
        self.info.header_only()
