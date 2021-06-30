#  Copyright (c) 2021 Jelle Spijker
#  Cura is released under the terms of the LGPLv3 or higher.

import os

from conans import ConanFile, tools, VisualStudioBuildEnvironment


class SipConan(ConanFile):
    name = "SIP"
    version = "4.19.25"
    description = "SIP Python binding for C/C++ (Used by PyQt)"
    topics = ("conan", "python", "binding", "sip")
    license = "GPL-3.0-only"
    homepage = "https://www.riverbankcomputing.com/software/sip/"
    url = f"https://www.riverbankcomputing.com/static/Downloads/sip"
    settings = "os", "compiler", "build_type", "arch"
    options = {'shared': [True, False]}
    default_options = {"shared": False}
    generators = "txt"
    exports_sources = ["SIPMacros.cmake"]
    _source_subfolder = "sip-src"

    _autotools = None

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("sip-{}".format(self.version), self._source_subfolder)
        tools.remove_files_by_mask

    def build(self):
        static_arg = "--static" if not self.options.shared else ""
        bindir = os.path.join(self.build_folder, "bin")
        destdir = os.path.join(self.build_folder, "site-packages")
        incdir = os.path.join(self.build_folder, "include")
        sipdir = os.path.join(self.build_folder, "sip")
        pyidir = os.path.join(self.build_folder, "site-packages", "PyQt5")
        if self.settings.compiler == "Visual Studio":
            env_build = VisualStudioBuildEnvironment(self)
            with tools.chdir(os.path.join(self.source_folder, self._source_subfolder)):
                with tools.environment_append(env_build.vars):
                    vcvars = tools.vcvars_command(self.settings)
                    self.run(f"{vcvars} && python configure.py --sip-module=PyQt5.sip {static_arg} --bindir={bindir} --destdir={destdir} --incdir={incdir} --bindir={bindir} --destdir={destdir} --incdir={incdir} --sipdir={sipdir} --pyidir={pyidir}")
                    self.run(f"{vcvars} && nmake")
                    self.run(f"{vcvars} && nmake install")
        else:
            with tools.chdir(os.path.join(self.source_folder, self._source_subfolder)):
                self.run(f"python configure.py --sip-module=PyQt5.sip {static_arg} --bindir={bindir} --destdir={destdir} --incdir={incdir} --bindir={bindir} --destdir={destdir} --incdir={incdir} --sipdir={sipdir} --pyidir={pyidir}")
                self.run(f"make")
                self.run(f"make install")

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("LICENSE-GPL2", dst="licenses", src=self._source_subfolder)
        self.copy("LICENSE-GPL3", dst="licenses", src=self._source_subfolder)
        self.copy("*", src="bin", dst="bin")
        self.copy("*", "lib", "lib")
        self.copy("*", src="site-packages", dst="site-packages")
        self.copy("*.h", src="include", dst="include")
        self.copy("SIPMacros.cmake", ".", ".")

    def package_info(self):
        self.env_info.path.append(os.path.join(self.package_folder, "bin"))
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "site-packages"))
        self.cpp_info.build_modules["cmake_find_package"].append("SIPMacros.cmake")
        self.cpp_info.build_modules["CMakeToolchain"].append("SIPMacros.cmake")
