"""
setup.py for hiro

"""
__author__ = "Ali-Akber Saifee"
__email__ = "ali@indydevs.org.com"
__copyright__ = "Copyright 2023, Ali-Akber Saifee"

from setuptools import setup
import os

import versioneer

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
REQUIREMENTS = [
    k for k in open(
        os.path.join(THIS_DIR, 'requirements', 'main.txt')
    ).read().splitlines() if k.strip()
]

extra = {}

setup(
    name='hiro',
    author=__author__,
    author_email=__email__,
    license="MIT",
    url="http://hiro.readthedocs.org",
    zip_safe=False,
    include_package_data=True,
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    install_requires=list(REQUIREMENTS),
    classifiers=[k for k in open('CLASSIFIERS').read().split('\n') if k],
    description='time manipulation utilities for testing in python',
    long_description=open('README.rst').read() + open('HISTORY.rst').read(),
    packages=["hiro"]
)
