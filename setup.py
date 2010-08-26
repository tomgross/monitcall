#!/usr/bin/env python

from setuptools import setup, find_packages

README = open('README').read().strip()

setup(
    name="monitcall",
    license="ZPL 2.1",
    version="0.2",
    description="Call and monitor executables",
    author="Tom Gross",
    maintainer="Tom Gross",
    maintainer_email="itconsense@gmail.com",
    url="",
    packages=find_packages(),
    long_description=README,
    zip_safe=True,
    install_requires=['psutil', 'argparse'],
    entry_points={
        'console_scripts': [
            'monitcall = monitcall.monitcall:main']},
    classifiers=[
        "Development Status :: 4 - Beta"
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Zope Public License",
        "Programming Language :: Python",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
        ])
