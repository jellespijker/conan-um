#  Copyright (c) 2021 Jelle Spijker

import os

from conans import ConanFile, tools
from conan.tools.gnu import AutotoolsDeps, Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.microsoft import MSBuildDeps, MSBuildToolchain, MSBuild
from conan.tools.files.packager import AutoPackager


required_conan_version = ">=1.42"


class PythonConan(ConanFile):
    name = "Python"
    version = "3.8.10"
    description = "The Python programming language"
    topics = ("conan", "python", "interpreter")
    license = "PSF 2.0"
    homepage = "https://www.python.org/"
    url = "https://github.com/python/cpython"
    settings = "os", "compiler", "build_type", "arch"
    build_policy = "missing"
    default_user = "python"
    default_channel = "stable"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }
    scm = {
        "type": "git",
        "subfolder": ".",
        "url": f"{url}.git",
        "revision": f"v{version}"
    }

    def requirements(self):
        self.requires("openssl/1.1.1l")
        self.requires("sqlite3/3.36.0")
        self.requires("libffi/3.4.2")
        self.requires("xz_utils/5.2.5")
        self.requires("zlib/1.2.11")
        if self.settings.os != "Windows":
            self.requires("openblas/0.3.15")
            self.requires("geos/3.9.1")

    def configure(self):
        self.options["openssl"].shared = self.options.shared
        self.options["sqlite3"].shared = self.options.shared
        self.options["libffi"].shared = self.options.shared
        self.options["xz_utils"].shared = self.options.shared
        self.options["zlib"].shared = self.options.shared
        if self.settings.os != "Windows":
            self.options["openblas"].shared = self.options.shared
            self.options["geos"].shared = self.options.shared
            self.options["bzip2"].shared = self.options.shared

    def layout(self):
        # FIXME: Why is the package folder empty at generation?
        self.package_folder = self.folders.package

    def generate(self):
        if self.settings.os == "Windows":
            # TODO: Windows is currently boilerplate
            deps = MSBuildDeps(self)
            deps.generate()

            tc = MSBuildToolchain(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.default_configure_install_args = True
            if self.settings.os == "Linux":
                tc.ldflags.append(f"-Wl,-rpath={os.path.join(self.package_folder, 'lib')}")
            else:
                tc.ldflags.append("-Wl")
            tc.configure_args.append("--enable-ipv6")
            tc.configure_args.append("--with-doc-strings")
            tc.configure_args.append("--with-ensurepip")
            tc.configure_args.append(f"--with-openssl={self.deps_cpp_info['openssl'].rootpath}")
            if self.settings.build_type == "Debug":
                tc.configure_args.append("--with-pydebug")
            else:
                tc.configure_args.append("--with-lto=full")
                tc.configure_args.append("--enable-optimizations")
            if self.options.shared:
                tc.configure_args.append("--enable-shared")
            tc.generate()

            deps = AutotoolsDeps(self)
            deps.generate()

    def build(self):
        if self.settings.os == "Windows":
            # TODO: Windows is currently boilerplate
            msbuild = MSBuild(self)
            msbuild.build("PCBuild/pcbuild.sln")
        else:
            at = Autotools(self)
            at.configure()
            at.make()
            at.make(target = "clean")
            at.install()

    def package(self):
        packager = AutoPackager(self)
        packager.run()

    def package_info(self):
        v = tools.Version(self.version)
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "lib", f"python{v.major}.{v.minor}"))
        self.runenv_info.prepend_path("PATH", os.path.join(self.package_folder, "bin"))
        self.buildenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "lib", f"python{v.major}.{v.minor}"))
        self.buildenv_info.prepend_path("PATH", os.path.join(self.package_folder, "bin"))
        build_type = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.includedirs = [f"include/python{v.major}.{v.minor}{build_type}"]

        # FIXME: Bug in Conan (https://github.com/conan-io/conan/issues/10009) once fixed this should be removed
        self.cpp_info.version = self.version
