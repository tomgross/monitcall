#!/usr/bin/env python

from setuptools import setup, find_packages

long_description = '\n\n'.join([
   open('README').read().strip(),
   open('CHANGES').read().strip()])

setup(
    name="monitcall",
    license="ZPL 2.1",
    version="0.3",
    description="Call and monitor executables",
    author="Tom Gross",
    author_email="itconsense@gmail.com",
    url="http://github.com/tomgross/monitcall",
    packages=find_packages(),
    long_description=long_description,
    zip_safe=True,
    install_requires=['psutil', 'argparse'],
    test_suite = 'monitcall.tests.test_suite',
    entry_points={
        'console_scripts': [
            'monitcall = monitcall.monitcall:main']},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Zope Public License",
        "Programming Language :: Python",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
        ])
