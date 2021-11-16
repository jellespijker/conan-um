#  Copyright (c) 2021 Jelle Spijker

import os

from jinja2 import Template

from conans import ConanFile, tools
from conan.tools.gnu import AutotoolsDeps, AutotoolsToolchain, Autotools
from conan.tools.env.virtualbuildenv import VirtualBuildEnv
from conan.tools.microsoft.subsystems import subsystem_path, deduce_subsystem
from conan.tools.files.packager import AutoPackager


required_conan_version = ">=1.42"

class AutoSIPtools(Autotools):
    # TODO: Check if there isn't an native solution for this, if not make FR at Conan
    def configure(self, buildTool = "", build_script_folder = None):
        if not self._conanfile.should_configure:
            return

        source = self._conanfile.source_folder
        if build_script_folder:
            source = os.path.join(self._conanfile.source_folder, build_script_folder)

        configure_cmd = f"{buildTool} {source}/configure.py"
        subsystem = deduce_subsystem(self._conanfile, scope="build")
        configure_cmd = subsystem_path(subsystem, configure_cmd)
        cmd = "{} {}".format(configure_cmd, self._configure_args)
        self._conanfile.output.info(f"Calling:\n > {cmd}")
        self._conanfile.run(cmd)


class SipConan(ConanFile):
    name = "sip"
    version = "4.19.25"
    description = "SIP Python binding for C/C++ (Used by PyQt)"
    topics = ("conan", "python", "binding", "sip")
    license = "GPL-3.0-only"
    homepage = "https://www.riverbankcomputing.com/software/sip/"
    url = f"https://www.riverbankcomputing.com/static/Downloads/sip"
    settings = "os", "compiler", "build_type", "arch"
    exports = ["LICENSE*", "cmake/SIPMacros.cmake.jinja"]
    exports_sources = ["cmake/SIPMacros.cmake.jinja"]
    build_policy = "missing"
    default_user = "riverbankcomputing"
    default_channel = "stable"
    build_requires = "Python/3.8.10@python/stable"
    requires = "Python/3.8.10@python/stable"
    options = {
        "shared": [True, False],
    }
    default_options = {
        "shared": True,
    }

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root = True)

    def layout(self):
        self.package_folder = self.folders.package

    def generate(self):
        bv = VirtualBuildEnv(self)  # Ensures that we use the Python executable from our own package
        bv.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

        tc = AutotoolsToolchain(self)
        if not self.options.shared:
            tc.configure_args.append("--static")
        if self.settings.build_type == "Debug":
            tc.configure_args.append("--debug")
        tc.configure_args.append(f"--bindir={os.path.join(self.package_folder, 'bin')}")
        tc.configure_args.append(f"--incdir={os.path.join(self.package_folder, 'include')}")
        tc.configure_args.append(f"--destdir={os.path.join(self.package_folder, 'site-packages')}")
        tc.configure_args.append(f"--pyidir={os.path.join(self.package_folder, 'site-packages')}")
        v = tools.Version(self.dependencies['Python'].ref.version)
        tc.configure_args.append(f"--target-py-version={v.major}.{v.minor}")
        tc.generate()

    def build(self):
        at = AutoSIPtools(self)
        at.configure("python3")
        at.make()
        at.install()

    def package(self):
        with open(os.path.join(self.source_folder, "cmake", "SIPMacros.cmake.jinja"), "r") as f:
            tm = Template(f.read())
            sip_executable = str(os.path.join(self.package_folder, "bin", "sip"))
            if self.settings.os == "Windows":
                sip_executable += ".exe"
            result = tm.render(sip_path = sip_executable)
            tools.save(os.path.join(self.package_folder, "share", "cmake", "SIPMacros.cmake"), result)
        packager = AutoPackager(self)
        packager.run()

    def package_info(self):
        self.runenv_info.append("PYTHONPATH", os.path.join(self.package_folder, "site-packages"))
        self.buildenv_info.append("PYTHONPATH", os.path.join(self.package_folder, "site-packages"))
        self.runenv_info.append("PATH", os.path.join(self.package_folder, "bin"))
        self.buildenv_info.append("PATH", os.path.join(self.package_folder, "bin"))
        sipmacros_path = os.path.join(self.package_folder, "share", "cmake", "SIPMacros.cmake")
        for build_module in ("cmake_find_package", "cmake_find_package_multi", "CMakeToolchain"):
            self.cpp_info.build_modules[build_module].append(sipmacros_path)
