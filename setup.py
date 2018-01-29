# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()


def _read_requirements(filename):
    return open(filename).read().splitlines()


setup(
    name='python-miscs',
    version='0.1.0',
    description='Misc utilities of python',
    long_description=readme,
    author='Yusaku Mandai',
    author_email='mandai.yusaku@gmail.com',
    url='https://github.com/mandaiy/python-miscs',
    license='Apache 2.0',
    packages=find_packages(exclude=('tests')),
    install_requires=_read_requirements('requirements.txt'),
    test_suite='tests'
)

