from distutils.core import setup, Extension
from os.path import dirname


c_ext = Extension("radius_mass", [dirname(__file__) + "/radius_mass.c"])
setup(ext_modules=[c_ext])
