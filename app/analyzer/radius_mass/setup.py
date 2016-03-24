from distutils.core import setup, Extension


c_ext = Extension("radius_mass", ["radius_mass.c"])
setup(ext_modules=[c_ext])
# todo: Automation of building process
