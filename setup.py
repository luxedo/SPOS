"""
SPOS - Small Payload Object Serializer
MIT License

Copyright (c) 2020 [Luiz Eduardo Amaral](luizamaral306@gmail.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from os import path

import setuptools

with open("README.md", "r") as fp:
    long_description = fp.read()

rootdir = path.abspath(path.dirname(__file__))
with open(path.join(rootdir, "spos", "__init__.py"), "r") as fp:
    version = (
        [
            line
            for line in fp.read().split("\n")
            if line.startswith("__version__")
        ][0]
        .split("=")[1]
        .strip()
        .strip('"')
    )

setuptools.setup(
    name="spos",
    version=version,
    description="SPOS stands for Small Payload Object Serializer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Luiz Eduardo Amaral",
    author_email="luizamaral306@gmail.com",
    url="https://github.com/luxedo/SPOS",
    license="LICENSE.md",
    packages=setuptools.find_packages(exclude=("tests",)),
    scripts=["bin/spos"],
    python_requires=">=3.7",
    install_requires=["crc8==0.1.0"],
    extra_require={
        "dev": [
            "pytest==5.4.1",
            "pytest-cov==2.8.1",
            "coverage==5.0.3",
            "flake8==3.8.3",
            "black==19.10b0",
            "pre-commit==2.6.0",
        ]
    },
    keywords="serializer LoRa Globalstar low-bandwidth",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
