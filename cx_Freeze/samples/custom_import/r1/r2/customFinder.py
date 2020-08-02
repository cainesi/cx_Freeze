from importlib.machinery import ModuleSpec
import os

# some informational resources
# https://python.readthedocs.io/en/stable/reference/import.html
# https://blog.quiltdata.com/import-almost-anything-in-python-an-intro-to-module-loaders-and-finders-f5e7b15cda47

dirName = os.path.dirname(__file__)
B_PATH = os.path.join(dirName, "r3b")
TARG_FILE = os.path.join(B_PATH, "r.py")

class SpecialImporter:

    @classmethod
    def create_module(cls, spec):
        return None  # tells Python to use the default module creator.

    @classmethod
    def exec_module(cls, module):
        """
        Module executor.
        """
        print("Custom exec_module for: {}".format(module.__name__))
        pieces = module.__name__.split('.')

        if module.__name__ == 'r1.r2.r3a':
            module.__path__ = B_PATH
            return module

        elif pieces[:4] == ["r1","r2","r3a", "r"]:
            module.__file__ = TARG_FILE
            with open(TARG_FILE, "r") as f:
                data = f.read()
                pass
            exec(data, module.__dict__)
            return module

        else:
            assert False

class SpecialFinder:

    @classmethod
    def find_spec(cls, fullname, path=None, target=None):
        print("Running custom find_spec for: {}".format(fullname))

        pieces = fullname.split('.')

        if pieces[:3] == ["r1", "r2", "r3a"] or pieces[:4] == ["r1", "r2", "r3a", "r"]:
            return ModuleSpec(fullname, SpecialImporter())
        else:
            return None

