import setuptools
import os
pkgname=os.path.basename(os.getcwd())
with open(".CURVER", "r", encoding="utf-8") as fh:
    curver = fh.readline()
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
f=open("requirements.txt", "r")
depends=f.read().split("\n")
f.close()

setuptools.setup(
    name=f"{pkgname}-genwch", # Replace with your own username
    version=f"{curver}",
    author="genwch",
    author_email="",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/genwch/{pkgname}",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=depends,
    python_requires='>=3.7',
)
