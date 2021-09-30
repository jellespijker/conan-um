#  Copyright (c) 2021 Jelle Spijker

import os

from conans import ConanFile, tools
from conan.tools.env.virtualrunenv import VirtualRunEnv

class NumpyConan(ConanFile):
    name = "cython"
    version = "0.29.24"
    description = ""
    topics = ("conan", "python")
    license = "Apache-2.0"
    homepage = "https://cython.org/"
    url = "https://github.com/cython/cython"
    settings = "os", "compiler", "build_type", "arch"
    python_requires = "PipBuildTool/0.1@ultimaker/testing"

    def requirements(self):
        self.requires("Python/3.8.10@python/testing")

    def generate(self):
        rv = VirtualRunEnv(self)
        rv.generate(auto_activate = True)

    def build(self):
        pb = self.python_requires["PipBuildTool"].module.PipBuildTool(self)
        pb.configure(self.deps_user_info["Python"].interp)
        pb.build()
        pb.install()

    def package(self):
        v = tools.Version(self.deps_cpp_info["Python"].version)
        self.copy("*", src = os.path.join(self.build_folder, "package", "lib", f"python{v.major}.{v.minor}", "site-packages"), dst = "site-packages")
        self.copy("*", src = os.path.join(self.build_folder, "package", "bin"), dst = "bin")

    def package_info(self):
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "site-packages"))
