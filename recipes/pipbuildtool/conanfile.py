#  Copyright (c) 2021 Jelle Spijker

import os

from conans import ConanFile, tools

class PipBuildTool(object):
    def __init__(self, conanfile: ConanFile, parallel=True):
        # Store a reference to useful data
        self._conanfile = conanfile
        self._parallel = parallel

    def configure(self, build_tool):
        # TODO: environment?
        if not self._conanfile.should_configure:
            return

        self._build_tool = build_tool

    def build(self, build_type=None, target = None):
        if not self._conanfile.should_build:
            return

        cmd = f"{self._build_tool} -m pip install --no-deps --prefix {os.path.join(self._conanfile.folders.build_folder, 'package')} {self._conanfile.name}=={self._conanfile.version}"
        self._conanfile.run(cmd)

    def install(self, build_type = None):
        if not self._conanfile.should_install:
            return


class Pkg(ConanFile):
    name = "PipBuildTool"
    version = "0.1"
