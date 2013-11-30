"""
setup.py for holmium.core


"""
__author__ = "Ali-Akber Saifee"
__email__ = "ali@indydevs.org.com"
__copyright__ = "Copyright 2013, Ali-Akber Saifee"

from setuptools import setup
import os
import sys
import hiro.version
this_dir = os.path.abspath(os.path.dirname(__file__))
REQUIREMENTS = filter(None, open(os.path.join(this_dir, 'requirements.txt')).read().splitlines())
extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True


setup(
    name='hiro',
    author = __author__,
    author_email = __email__,
    license = "MIT",
    url="https://hiro.readthedocs.org/en/latest/",
    zip_safe = False,
    version=hiro.version.__version__,
    include_package_data = True,
    install_requires = REQUIREMENTS,
    classifiers=[k for k in open('CLASSIFIERS').read().split('\n') if k],
    description='selenium page objects and other utilities for test creation',
    long_description=open('README.rst').read(),
    packages = ["hiro"],
    **extra
)

