import setuptools

with open("README.md", "r") as fp:
    long_description = fp.read()

setuptools.setup(
    name="spos",
    version="1.0.0-alpha",
    description="SPOS stands for Small Payload Object Serializer",
    long_description=long_description,
    long_description_conntent_type="text/markdown",
    author="Luiz Eduardo Amaral",
    author_email="luizamaral306@gmail.com",
    url="https://github.com/luxedo/SPOS",
    packages=setuptools.find_packages(),
    # packages=["payload", "serializer", "LoRa", "Globalstar"],
    python_requires=">=3.6",
    install_requires=["crc8==0.1.0"],
)
