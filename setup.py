#!/usr/bin/env python3
"""Setup script for RapidSim_Cfg package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rapidsim_cfg",
    version="0.1.1",
    author="Zan Ren",
    author_email="zan.ren@cern.ch",
    description="Generate RapidSim configuration files programmatically",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ericbrownrenzan/rapidsim_cfg",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies required
    ],
)
