from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [Extension("ssm_logic", ["ssm_logic.py"])]

setup(
    name="ssm_logic_lib",
    version="1.0",
    ext_modules=cythonize(extensions, compiler_directives={'language_level': "3"}),
    zip_safe=False,
)