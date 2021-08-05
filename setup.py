import os
import subprocess

from setuptools import setup

REQUIREMENTS = []
with open(os.path.join(os.getcwd(), "requirements.txt")) as f:
    REQUIREMENTS = f.read().splitlines()

VERSION = "0.0.1"
if "a" in VERSION:
    VERSION += "+" + subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode("utf-8").strip()

README = ""
with open("README.rst") as f:
    README = f.read()

setup(
    name="bs.py",
    author="priyamroy",
    url="https://github.com/priyamroy/bs.py",
    packages=["bs"],
    version=VERSION,
    license="MIT",
    description="A python wrapper for the Brawl Stars API",
    long_description=README,
    python_requires=">=3.6.0",
    install_requires=REQUIREMENTS,
    classifiers={
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    }
)
