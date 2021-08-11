#  Copyright (c) 2021 Jelle Spijker
#  Cura is released under the terms of the LGPLv3 or higher.

import os

from conans import ConanFile, tools


class SipConan(ConanFile):
    name = "SIP"
    version = "4.19.25"
    description = "SIP Python binding for C/C++ (Used by PyQt)"
    topics = ("conan", "python", "binding", "sip")
    license = "GPL-3.0-only"
    homepage = "https://www.riverbankcomputing.com/software/sip/"
    url = f"https://www.riverbankcomputing.com/static/Downloads/sip"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "python_version": "ANY"
    }
    default_options = {
        "shared": True,
        "python_version": "3.8"
    }
    exports_sources = ["SIPMacros.cmake"]
    _source_subfolder = "sip-src"

    @property
    def python_interp(self):
        interp = "\"{}\"".format(tools.get_env("CONAN_PYTHON_INTERP", f"python"))
        interp += str(self.options.python_version) if self.settings.os != "Windows" else ""
        return interp

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("sip-{}".format(self.version), self._source_subfolder)

    def build(self):
        static_arg = "--static " if not self.options.shared else ""
        bindir = os.path.join(self.build_folder, "bin")
        destdir = os.path.join(self.build_folder, "site-packages")
        incdir = os.path.join(self.build_folder, "include")
        pyidir = os.path.join(self.build_folder, "site-packages")
        if self.settings.compiler == "Visual Studio":
            with tools.chdir(os.path.join(self.source_folder, self._source_subfolder)):
                with tools.vcvars(self):
                    self.run(f"{self.python_interp} configure.py {static_arg} --bindir={bindir} --destdir={destdir} --incdir={incdir} --pyidir={pyidir} --target-py-version {self.options.python_version}")
                    self.run(f"nmake")
                    self.run(f"nmake install")
        else:
            with tools.chdir(os.path.join(self.source_folder, self._source_subfolder)):
                self.run(f"{self.python_interp} configure.py {static_arg}--bindir={bindir} --destdir={destdir} --incdir={incdir} --pyidir={pyidir}")
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
        sip_executable = str(os.path.join(self.package_folder, "bin", "sip"))
        if self.settings.os == "Windows":
            sip_executable += ".exe"
            sip_executable = sip_executable.replace("\\", "\\\\")
        tools.replace_in_file(os.path.join(self.package_folder, "SIPMacros.cmake"), "SET(SIP_EXECUTABLE \"\")", f"SET(SIP_EXECUTABLE \"{sip_executable}\")")

    def package_info(self):
        self.env_info.path.append(os.path.join(self.package_folder, "bin"))
        self.env_info.CONAN_PYTHON_INTERP = self.python_interp
        self.runenv_info.append("PYTHONPATH", os.path.join(self.package_folder, "site-packages"))
        self.cpp_info.build_modules["cmake_find_package"].append("SIPMacros.cmake")
        self.cpp_info.build_modules["CMakeToolchain"].append("SIPMacros.cmake")
