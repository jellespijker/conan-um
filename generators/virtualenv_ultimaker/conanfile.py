from conans.client.generators.virtualenv_python import VirtualEnvPythonGenerator
from conans import ConanFile
import os
import pathlib

class virtualenv_ultimaker(VirtualEnvPythonGenerator):
    venv_name = "ultimaker"
    
    def __init__(self, conanfile):
        super(virtualenv_ultimaker, self).__init__(conanfile)

    @property
    def content(self):
        result = super(virtualenv_ultimaker, self).content
        try:
            CURAENGINEPATH = os.path.join(self.conanfile.dependencies["CuraEngine"].package_folder, "bin", "CuraEngine")
        except:
            CURAENGINEPATH = ""
        with open(pathlib.Path(__file__).parent.resolve().joinpath("activate"), "r") as f:
            result["activate"] = f.read()
            result["activate"] = result["activate"].replace("BASEDIR=\"\"", f"BASEDIR=\"{self.conanfile.install_folder}\"")
            result["activate"] = result["activate"].replace("export CURAENGINEPATH=\"\"", f"export CURAENGINEPATH=\"{CURAENGINEPATH}\"")
        return result


class VirtualEnvUMGeneratorPackage(ConanFile):
    name = "virtualenv_ultimaker_gen"
    version = "0.1"
    url = "https://github.com/jellespijker/conan-um"
    license = "LGPL-3.0"
    exports = ["activate"]

    def package(self):
        self.copy("activate", ".", ".")
