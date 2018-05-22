#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="j2j",
    version="0.1.0",
    description="This library supports converting one form of json to another.",
    packages=find_packages(),
    url="https://github.com/prafulbagai/j2j",
    author="Praful Bagai",
    author_email="praful.bagai1991@gmail.com",
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    long_description=open("README.md").read(),
)
