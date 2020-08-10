"""
SPOS - Small Payload Object Serializer
Copyright (C) 2020 Luiz Eduardo Amaral <luizamaral306@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import setuptools

with open("README.md", "r") as fp:
    long_description = fp.read()

setuptools.setup(
    name="spos",
    version="1.2.3-b",
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
