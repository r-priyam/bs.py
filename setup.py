import re
import subprocess

import setuptools
from setuptools import setup

with open("requirements.txt") as f:
    REQUIREMENTS = f.read().splitlines()


with open("bs/__init__.py") as f:
    VERSION = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE
    ).group(1)
if "a" in VERSION:
    VERSION += (
        "+"
        + subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
        .decode("utf-8")
        .strip()
    )

with open("README.md") as f:
    README = f.read()

setup(
    name="bs.py",
    author="priyamroy",
    url="https://github.com/priyamroy/bs.py",
    packages=setuptools.find_packages(),
    version=VERSION,
    license="MIT",
    description="A python wrapper for the Brawl Stars API",
    long_description=README,
    long_description_content_type="text/markdown",
    keywords=["brawl stars", "bs api", "brawl stars python", "brawl stars api"],
    python_requires=">=3.6.0",
    install_requires=REQUIREMENTS,
    classifiers={
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    },
    project_urls={
        "Source": "https://github.com/priyamroy/bs.py",
        "Tracker": "https://github.com/priyamroy/bs.py/issues",
    },
)
