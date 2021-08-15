#  Copyright (c) 2021 Jelle Spijker

import os

from conans import ConanFile, tools
from conan.tools.gnu import AutotoolsDeps, Autotools, AutotoolsToolchain
from conan.tools.microsoft import MSBuildDeps, MSBuildToolchain, MSBuild


class PythonConan(ConanFile):
    name = "Python"
    version = "3.8.10"
    description = "Python"
    topics = ("conan", "python", "interpreter")
    license = "PSF 2.0"
    homepage = "https://www.python.org/"
    url = "https://github.com/python/cpython"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
    }
    default_options = {
        "shared": True,
    }

    scm = {
        "type": "git",
        "subfolder": ".",
        "url": f"{url}.git",
        "revision": f"v{version}"
    }

    @property
    def _pip_name(self) -> str:
        pip = "pip"
        if self.settings.os == "Windows":
            pip += ".exe"
        else:
            v = tools.Version(self.version)
            pip += f"{v.major}.{v.minor}"
        return pip

    @property
    def _interp_name(self) -> str:
        interp = "python"
        if self.settings.os == "Windows":
            if self.settings.build_type == "Debug":
                interp += "_d"
            interp += ".exe"
        else:
            v = tools.Version(self.version)
            interp += f"{v.major}.{v.minor}"
            if self.settings.build_type == "Debug":
                interp += "d"
        return interp

    def requirements(self):
        self.requires("openblas/0.3.15")
        self.requires("geos/3.9.1")
        self.requires("openssl/1.1.1k")
        self.requires("sqlite3/3.36.0")
        self.requires("libffi/3.4.2")
        self.requires("xz_utils/5.2.5")
        self.requires("zlib/1.2.11")
        if self.settings.os == "Linux":
            self.requires("bzip2/1.0.8")

    def configure(self):
        self.options["openblas"].shared = self.options.shared
        self.options["geos"].shared = self.options.shared
        self.options["openssl"].shared = self.options.shared
        self.options["sqlite3"].shared = self.options.shared
        self.options["libffi"].shared = self.options.shared
        self.options["xz_utils"].shared = self.options.shared
        self.options["zlib"].shared = self.options.shared
        if self.settings.os == "Linux":
            self.options["bzip2"].shared = self.options.shared

    def generate(self):
        if self.settings.os == "Windows":
            # TODO: Windows is currently boilerplate
            deps = MSBuildDeps(self)
            deps.generate()

            tc = MSBuildToolchain(self)
            tc.generate()
        else:
            deps = AutotoolsDeps(self)
            deps.generate()

            tc = AutotoolsToolchain(self)
            tc.configure_args.append(f"--prefix={os.path.join(self.install_folder, 'package')}")
            tc.configure_args.append("--enable-ipv6")
            tc.configure_args.append("--without-pymalloc")
            tc.configure_args.append("--with-system-ffi")
            tc.configure_args.append("--with-doc-strings")
            tc.configure_args.append("--with-ensurepip")
            if self.settings.build_type == "Debug":
                tc.configure_args.append("--with-pydebug")
                tc.cflags.append("-DPy_DEBUG")
            else:
                tc.configure_args.append("--with-lto")
                tc.configure_args.append("--enable-optimizations")
            if self.options.shared:
                tc.configure_args.append("--enable-shared")
            tc.generate()

    def build(self):
        if self.settings.os == "Windows":
            # TODO: Windows is currently boilerplate
            msbuild = MSBuild(self)
            msbuild.build("PCBuild/pcbuild.sln")
        else:
            at = Autotools(self)
            at.configure()
            at.make(target = "clean")
            at.make()
            at.make(target = "clean")
            at.make(target = "altinstall")

    def package(self):
        self.copy("*", src = os.path.join(self.build_folder, "package"), dst = ".")

    def package_info(self):
        v = tools.Version(self.version)
        self.cpp_info.libs = tools.collect_libs(self)
        build_type = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.includedirs = [f"include/python{v.major}.{v.minor}{build_type}"]
        self.user_info.interp = str(os.path.join(self.package_folder, "bin", self._interp_name))
        self.user_info.pip = str(os.path.join(self.package_folder, "bin", self._pip_name))
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, f"python{v.major}.{v.minor}", "site-packages"))
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, f"python{v.major}.{v.minor}"))
