#  Copyright (c) 2021 Jelle Spijker

import os
from copy import deepcopy
from jinja2 import Template

from conans import ConanFile
from conans.tools import save
from conan.tools.env.virtualrunenv import runenv_from_cpp_info, VirtualRunEnv

class PyCharmRunEnvironment(VirtualRunEnv):
    """
    Creates a Pycharm.run.xml file based on the jinja template in .conan_gen where all environment variables are set,
    defined in the dependencies and in the current conanfile.

    The conan file needs to have a list called pycharm_targets with dicts (with the following struct::

        pycharm_targets = [
            {
                "jinja_path": str(os.path.join(pathlib.Path(__file__).parent.absolute(), ".conan_gen", "<TemplateFile>.run.xml.jinja")),
                "name": "<Name of the run file>",
                "entry_point": "<target it needs to run>",
                "arguments": "<extra command line arguments>"
            }
        ]


    Make sure you add CuraVersion.py with the following content to the folder cura::

        import os

        CuraAppDisplayName = os.getenv("CURA_APP_DISPLAY_NAME", "Cura")
        CuraVersion = os.getenv("CURA_VERSION", "master")
        CuraBuildType = os.getenv("CURA_BUILD_TYPE", "")
        CuraDebugMode = True
        CuraCloudAPIRoot = os.getenv("CURA_CLOUD_API_ROOT", "https://api.ultimaker.com")
        CuraCloudAccountAPIRoot = os.getenv("CURA_CLOUD_ACCOUNT_API_ROOT", "https://account.ultimaker.com")
        CuraDigitalFactoryURL = os.getenv("CURA_DIGITAL_FACTORY_URL", "https://digitalfactory.ultimaker.com")

    """

    def environment(self):
        runenv = self._conanfile.runenv_info
        host_req = self._conanfile.dependencies.host
        test_req = self._conanfile.dependencies.test
        for _, dep in list(host_req.items()) + list(test_req.items()):
            if dep.runenv_info:
                runenv.compose_env(dep.runenv_info)
            runenv.compose_env(runenv_from_cpp_info(self._conanfile, dep.cpp_info))

        return runenv

    def generate(self, auto_activate = False):
        run_env = self.environment()
        if run_env:
            if not hasattr(self._conanfile, "pycharm_targets"):
                self._conanfile.output.error("pycharm_targets not set in conanfile.py")
                return
            for ref_target in getattr(self._conanfile, "pycharm_targets"):
                target = deepcopy(ref_target)
                jinja_path = target.pop("jinja_path")
                with open(jinja_path, "r") as f:
                    tm = Template(f.read())
                    result = tm.render(env_vars = run_env, **target)
                    file_name = f"{target['name']}.run.xml"
                    path = os.path.join(target['run_path'], file_name)
                    save(path, result)
                    self._conanfile.output.info(f"PyCharm run file created: {path}")



class Pkg(ConanFile):
    name = "PyCharmRunEnvironment"
    version = "0.1"
