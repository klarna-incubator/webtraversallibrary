import re
import setuptools


with open("README.md", "r") as f:
    long_description = f.read()


with open("webtraversallibrary/version.py", "r") as f:
    version = re.search(r"__version__ = \"(.*?)\"", f.read()).group(1)


setuptools.setup(
    name="webtraversallibrary",
    version=version,
    author="Klarna Bank AB",
    author_email="marcus.naslund@klarna.com",
    description="Abstractions of web interactions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/klarna-incubator/webtraversallibrary",
    python_requires=">=3.7",
    packages=["webtraversallibrary"],
    include_package_data=True,
    install_requires=[
        "beautifulsoup4>=4.7",
        "html5lib",
        "pillow>=5.3",
        "requests",
        "selenium",
        "tld",
        "urllib3"
    ],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
