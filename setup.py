import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="avstudio_api",
    version="0.0.1",
    author="Ian Harvey",
    author_email="iharvey@epiphan.com",
    description="AVStudio API wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: ???",
        "Operating System :: OS Independent"
    ],
)