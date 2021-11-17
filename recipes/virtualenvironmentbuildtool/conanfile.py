#  Copyright (c) 2021 Jelle Spijker

import os

from conans import ConanFile, tools

class VirtualEnvironmentBuildTool(object):
    def __init__(self, conanfile: ConanFile, parallel=True):
        # Store a reference to useful data
        self._conanfile = conanfile
        self._parallel = parallel

    def configure(self, build_tool):
        # TODO: environment?
        if not self._conanfile.should_configure:
            return

        self._build_tool = build_tool

    def generate(self, pip_deps = ""):
        if not self._conanfile.should_build:
            return

        cmd = f"{self._build_tool} -m venv {self._conanfile.generators_folder}"
        self._conanfile.run(cmd)

        if pip_deps != "":
            # FIXME: for windows
            pip_cmd = f"source {self._conanfile.generators_folder}/bin/activate && python -m pip install {pip_deps}"
            self._conanfile.run(pip_cmd)

    def install(self, build_type = None):
        if not self._conanfile.should_install:
            return


class Pkg(ConanFile):
    name = "VirtualEnvironmentBuildTool"
    version = "0.1"
    default_user = "ultimaker"
    default_channel = "testing"
