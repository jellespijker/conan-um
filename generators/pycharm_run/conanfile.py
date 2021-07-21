from conans.client.generators.virtualenv_python import VirtualEnvPythonGenerator
from conans import ConanFile
import pathlib

class pycharm_run(VirtualEnvPythonGenerator):
    venv_name = "ultimaker"
    
    def __init__(self, conanfile):
        super(pycharm_run, self).__init__(conanfile)

    @property
    def content(self):
        result = super(pycharm_run, self).content
        DYLD_LIBRARY_PATH = ":".join(self.env['DYLD_LIBRARY_PATH'])
        LD_LIBRARY_PATH = ":".join(self.env['LD_LIBRARY_PATH'])
        PATH = ":".join(self.env['PATH'])
        PYTHONPATH = ":".join(self.env['PYTHONPATH'])
        run_name = f"{self.conanfile.name}.run.xml"
        with open(pathlib.Path(__file__).parent.resolve().joinpath("cura_app.run.xml"), "r") as f:
            result[run_name] = f.read()
            result[run_name] = result[run_name].replace("<env name=\"DYLD_LIBRARY_PATH\" value=\"\" />", f"<env name=\"DYLD_LIBRARY_PATH\" value=\"{DYLD_LIBRARY_PATH}\" />")
            result[run_name] = result[run_name].replace("<env name=\"LD_LIBRARY_PATH\" value=\"\" />", f"<env name=\"LD_LIBRARY_PATH\" value=\"{LD_LIBRARY_PATH}\" />")
            result[run_name] = result[run_name].replace("<env name=\"PATH\" value=\"\" />", f"<env name=\"PATH\" value=\"{PATH}\" />")
            result[run_name] = result[run_name].replace("<env name=\"PYTHONPATH\" value=\"\" />", f"<env name=\"PYTHONPATH\" value=\"{PYTHONPATH}\" />")
        return result


class VirtualEnvUMGeneratorPackage(ConanFile):
    name = "pycharm_run_gen"
    version = "0.1"
    url = "https://github.com/jellespijker/conan-um"
    license = "LGPL-3.0"
    exports = ["cura_app.run.xml"]

    def package(self):
        self.copy("cura_app.run.xml", ".", ".")
