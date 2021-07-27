import os
from conans import ConanFile, CMake, tools
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake


class ArvusTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def build_requirements(self):
        self.build_requires("cmake/[>=3.16.2]")
        if self.settings.os == "Windows":
            self.build_requires("mingw_installer/1.0@conan/stable")
            self.build_requires("mingw-w64/[>=8.1]")

    def requirements(self):
        self.requires(f"Arcus/modernize_build@ultimaker/testing")
        self.requires("protobuf/[>=3.15.5]")

    def generate(self):
        cmake = CMakeDeps(self)
        cmake.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def imports(self):
        self.copy("*.dll", dst="bin", src="bin")
        self.copy("*.dylib*", dst="bin", src="lib")
        self.copy('*.so*', dst='bin', src='lib')

    def test(self):
        if not tools.cross_building(self.settings):
            self.run(f".{os.sep}test")
