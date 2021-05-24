import os
from glob import glob
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize


def get_module(current_dir, file):
    module = os.path.join(current_dir, os.path.basename(file))
    module = module.replace('.py', '').replace('/', '.')
    return module


if __name__ == "__main__":
    # Get python files
    current_dir = os.path.relpath(os.path.dirname(__file__), os.getcwd())
    source_dir = os.path.join(current_dir, "src")
    files = sorted(glob(os.path.join(source_dir, '*.py')))
    print("Number of files in {}: {}".format(source_dir, len(files)))

    # Get modules
    ext_modules = [
        Extension(get_module(current_dir, file), [file]) for file in files]

    # build
    setup(
        cmdclass={'build_ext': build_ext},
        ext_modules=cythonize(ext_modules, language_level="3"),
    )
