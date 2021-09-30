#  Copyright (c) 2021 Jelle Spijker

import os

from conans import ConanFile, tools

class PythonBuildTool(object):
    def __init__(self, conanfile: ConanFile, parallel=True):
        # Store a reference to useful data
        self._conanfile = conanfile
        self._parallel = parallel

    def configure(self, build_tool):
        # TODO: environment?
        if not self._conanfile.should_configure:
            return

        self._build_tool = build_tool

    def build(self, build_type=None, target = None, extra_args = ""):
        if not self._conanfile.should_build:
            return

        args = "--debug" if self._conanfile.settings.build_type == "Debug" else ""
        setup_path = os.path.join(self._conanfile.folders.source_folder, "setup.py")
        build_path = os.path.join(self._conanfile.folders.build_folder, "package")
        site_packages_path = os.path.join(build_path, "site-packages")
        cmd = f"{self._build_tool} {setup_path} build -j {tools.cpu_count()} --build-base {build_path} --build-lib {site_packages_path} {args} {extra_args}"
        with tools.chdir(self._conanfile.folders.source_folder):
            self._conanfile.run(cmd)

    def install(self, build_type = None):
        if not self._conanfile.should_install:
            return


class Pkg(ConanFile):
    name = "PythonBuildTool"
    version = "0.1"
