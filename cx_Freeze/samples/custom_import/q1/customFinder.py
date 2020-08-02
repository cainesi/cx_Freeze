from importlib.machinery import ModuleSpec
import os


dirName = os.path.dirname(__file__)
REAL_PATH = os.path.join(dirName, "q2b")
TARG_FILE = os.path.join(REAL_PATH, "q.py")

class SpecialImporter:

    @classmethod
    def create_module(cls, spec):

        return None  # tells Python to use the default module creator.

    @classmethod
    def exec_module(cls, module):
        print("Custom exec_module for: {}".format(module.__name__))
        pieces = module.__name__.split('.')

        if module.__name__ == "q1.q2a" or module.__name__ == "q1.q4":
            # __path__ must be set even if the package is virtual, but can be set to [].
            module.__path__ = REAL_PATH
            return module

        elif pieces[:3] == ["q1","q2a","q"] or pieces[:3] == ["q1","q4","q"]:
            module.__file__ = TARG_FILE
            with open(TARG_FILE, "r") as f:
                data = f.read()
                pass
            exec(data, module.__dict__)
            return module

        else:
            assert False

class SpecialFinder:
    """An object of this class gets inserted into sys.meta_path."""

    @classmethod
    def find_spec(cls, fullname, path=None, target=None):
        print("Custom find_spec for: {}".format(fullname))

        pieces = fullname.split('.')

        if len(pieces) < 2:
            return None
        if pieces[0] != "q1":
            return None
        if pieces[1] not in ["q2a", "q4"]:
            return None
        if len(pieces) > 2 and pieces[2] != "q":
            return None
        if len(pieces) > 3:
            return None

        return ModuleSpec(fullname, SpecialImporter())


