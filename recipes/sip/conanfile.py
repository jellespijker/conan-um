#  Copyright (c) 2021 Jelle Spijker

import os

from conans import ConanFile, tools
from conan.tools.gnu import AutotoolsDeps, AutotoolsToolchain, Autotools
from conan.tools.env.virtualrunenv import VirtualRunEnv
from conan.tools.microsoft.subsystems import subsystem_path, deduce_subsystem

class AutoSIPtools(Autotools):
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
    name = "SIP"
    version = "4.19.25"
    description = "SIP Python binding for C/C++ (Used by PyQt)"
    topics = ("conan", "python", "binding", "sip")
    license = "GPL-3.0-only"
    homepage = "https://www.riverbankcomputing.com/software/sip/"
    url = f"https://www.riverbankcomputing.com/static/Downloads/sip"
    settings = "os", "compiler", "build_type", "arch"
    exports = "LICENSE*", "SIPMacros.cmake"
    options = {
        "shared": [True, False],
    }
    default_options = {
        "shared": True,
    }
    exports_sources = ["SIPMacros.cmake"]

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root = True)

    def requirements(self):
        self.requires("Python/3.8.10@python/testing")

    def generate(self):
        ms = VirtualRunEnv(self)
        ms.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

        tc = AutotoolsToolchain(self)
        if not self.options.shared:
            tc.configure_args.append("--static")
        if self.settings.build_type == "Debug":
            tc.configure_args.append("--debug")
        tc.configure_args.append(f"--bindir={os.path.join(self.install_folder, 'package', 'bin')}")
        tc.configure_args.append(f"--incdir={os.path.join(self.install_folder, 'package', 'include')}")
        tc.configure_args.append(f"--destdir={os.path.join(self.install_folder, 'package', 'site-packages')}")
        tc.configure_args.append(f"--pyidir={os.path.join(self.install_folder, 'package', 'site-packages')}")
        tc.configure_args.append(f"--target-py-version={self.deps_cpp_info['Python'].version}")
        tc.generate()

    def build(self):
        at = AutoSIPtools(self)
        at.configure(self.deps_user_info["Python"].interp)
        at.make()
        at.make(target = "clean")
        at.install()

    def package(self):
        self.copy("*", src = os.path.join(self.build_folder, "package"), dst = ".")
        self.copy("SIPMacros.cmake", ".", ".")
        sip_executable = str(os.path.join(self.package_folder, "bin", "sip"))
        if self.settings.os == "Windows":
            sip_executable += ".exe"
            sip_executable = sip_executable.replace("\\", "\\\\")
        tools.replace_in_file(os.path.join(self.package_folder, "SIPMacros.cmake"), "SET(SIP_EXECUTABLE \"\")", f"SET(SIP_EXECUTABLE \"{sip_executable}\")")

    def package_info(self):
        self.runenv_info.append("PYTHONPATH", os.path.join(self.package_folder, "site-packages"))
        self.cpp_info.build_modules["cmake_find_package"].append("SIPMacros.cmake")
        self.cpp_info.build_modules["CMakeToolchain"].append("SIPMacros.cmake")
