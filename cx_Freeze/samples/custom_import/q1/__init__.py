print("Hello from q1")

#from . import customFinder as cf
from . import customFinder as cf
import sys

sys.meta_path.append(cf.SpecialFinder())
