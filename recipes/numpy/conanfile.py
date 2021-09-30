#  Copyright (c) 2021 Jelle Spijker

import os

from conans import ConanFile, tools
from conan.tools.env.virtualrunenv import VirtualRunEnv
from conan.tools.env.virtualbuildenv import VirtualBuildEnv

class NumpyConan(ConanFile):
    name = "numpy"
    version = "1.20.2"
    description = ""
    topics = ("conan", "python", "pypi", "pip")
    license = "BSD-3-Clause License"
    homepage = "https://www.python.org/"
    url = "https://github.com/numpy/numpy"
    settings = "os", "compiler", "build_type", "arch"
    python_requires = "PythonBuildTool/0.1@ultimaker/testing"
    scm = {
        "type": "git",
        "subfolder": ".",
        "url": f"{url}.git",
        "revision": f"v{version}"
    }


    def build_requirements(self):
        self.build_requires("gfortran/10.2")

    def requirements(self):
        self.requires("Python/3.8.10@python/testing")
        self.requires("cython/0.29.24@python/testing")
        self.requires("openblas/0.3.15")

    def generate(self):
        rv = VirtualRunEnv(self)
        rv.generate(auto_activate = True)

        bv = VirtualBuildEnv(self)
        bv.generate(auto_activate = True)

    def build(self):
        pb = self.python_requires["PythonBuildTool"].module.PythonBuildTool(self)
        pb.configure(self.deps_user_info["Python"].interp)
        pb.build(extra_args = "--fcompiler=gnu95")
        pb.install()

    def package(self):
        self.copy("*", src = os.path.join(self.build_folder, "package", "site-packages"), dst = "site-packages")

    def package_info(self):
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "site-packages"))
