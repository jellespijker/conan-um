import os

from conans import ConanFile
from copy import deepcopy
from conans.model import Generator
from conan.tools.env import Environment
from conan.tools.env.virtualrunenv import runenv_from_cpp_info
from jinja2 import Template


class PyCharmRunEnv(Generator):
    """ captures the conanfile environment that is defined from its
    dependencies, and also from profiles
    """

    @property
    def filename(self):
        pass

    def environment(self):
        """ collects the runtime information from dependencies. For normal libraries should be
        very occasional
        """
        self.conanfile.output.info("PyCharmRunEnv environment")
        runenv = Environment(self.conanfile)
        host_req = self.conanfile.dependencies.host
        test_req = self.conanfile.dependencies.test
        for _, dep in list(host_req.items()) + list(test_req.items()):
            if dep.runenv_info:
                runenv.compose(dep.runenv_info)
            runenv.compose(runenv_from_cpp_info(self.conanfile, dep.cpp_info))

        return runenv

    @property
    def content(self):
        self.conanfile.output.info("PyCharmRunEnv generate")
        run_env = self.environment()
        files = {}
        if run_env:
            self.conanfile.output.info("PyCharmRunEnv run_env")
            if not hasattr(self.conanfile, "pycharm_targets"):
                self.conanfile.output.error("pycharm_targets not set in conanfile.py")
                return
            for ref_target in getattr(self.conanfile, "pycharm_targets"):
                target = deepcopy(ref_target)
                jinja_path = target.pop("jinja_path")
                self.conanfile.output.info(f"jinja_path: {jinja_path}")
                with open(jinja_path, "r") as f:
                    tm = Template(f.read())
                    result = tm.render(env_vars = run_env, **target)
                    self.conanfile.output.success(f"result {result}")
                    file_name = f"{target['name']}.run.xml"
                    files[file_name] = result
        return files


class PyCharmRunEnvPackage(ConanFile):
    name = "PyCharmRunEnvGen"
    version = "0.1"
    url = "https://github.com/jellespijker/conan-um"
    license = "MIT"
