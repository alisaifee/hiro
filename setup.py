"""
setup.py for hiro

"""
__author__ = "Ali-Akber Saifee"
__email__ = "ali@indydevs.org.com"
__copyright__ = "Copyright 2013, Ali-Akber Saifee"

from setuptools import setup
import os
import sys
import re

this_dir = os.path.abspath(os.path.dirname(__file__))
REQUIREMENTS = filter(None, open(os.path.join(this_dir, 'requirements.txt')).read().splitlines())
extra = {}
version = re.compile("__version__\s*=\s*\"(.*?)\"").findall(open("hiro/version.py").read())[0]



setup(
    name='hiro',
    author = __author__,
    author_email = __email__,
    license = open("LICENSE").read(),
    url="http://hiro.readthedocs.org",
    zip_safe = False,
    include_package_data = True,
    version = version,
    install_requires = REQUIREMENTS,
    classifiers=[k for k in open('CLASSIFIERS').read().split('\n') if k],
    description='time manipulation utilities for python',
    long_description=open('README.rst').read(),
    packages = ["hiro"]
)

