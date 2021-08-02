from conans import ConanFile
from conan.tools.env import Environment
from conans.model import Generator

import pathlib
from jinja2 import Template


def runenv_from_cpp_info(conanfile: ConanFile, cpp_info):
    """ return an Environment deducing the runtime information from a cpp_info
    """
    dyn_runenv = Environment(conanfile)
    if cpp_info is None:  # This happens when the dependency is a private one = BINARY_SKIP
        return dyn_runenv
    if cpp_info.bin_paths:  # cpp_info.exes is not defined yet
        dyn_runenv.prepend_path("PATH", cpp_info.bin_paths)
    # If it is a build_require this will be the build-os, otherwise it will be the host-os
    if cpp_info.lib_paths:
        dyn_runenv.prepend_path("LD_LIBRARY_PATH", cpp_info.lib_paths)
        dyn_runenv.prepend_path("DYLD_LIBRARY_PATH", cpp_info.lib_paths)
    if cpp_info.framework_paths:
        dyn_runenv.prepend_path("DYLD_FRAMEWORK_PATH", cpp_info.framework_paths)
    return dyn_runenv


class pycharm_run(Generator):
    """ captures the conanfile environment that is defined from its
    dependencies, and also from profiles
    """

    def __init__(self, conanfile: ConanFile):
        super(pycharm_run, self).__init__(conanfile)

    @property
    def filename(self):
        return "cura_app.run.xml"

    def environment(self):
        """ collects the runtime information from dependencies. For normal libraries should be
        very occasional
        """
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
        run_env = self.environment()
        kwargs = {}
        if run_env:
            for env, val in run_env.items():
                kwargs[env] = val

            with open(pathlib.Path(__file__).parent.resolve().joinpath("pycharm.run.jinja"), "r") as f:
                tm = Template(f.read())
                result = tm.render(**kwargs)
                self.conanfile.output.success(result)
                return result
        return ""


class PycharmRunEnvGeneratorPackage(ConanFile):
    name = "pycharm_run_gen"
    version = "0.1"
    url = "https://github.com/jellespijker/conan-um"
    license = "LGPL-3.0"
    exports = ["pycharm.run.jinja"]

    def package(self):
        self.copy("pycharm.run.jinja", ".", ".")
