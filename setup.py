import re
import setuptools


with open("README.md", "r") as f:
    long_description = f.read()


with open("wtl/version.py", "r") as f:
    version = re.search(r"__version__ = \"(.*?)\"", f.read()).group(1)


setuptools.setup(
    name="webtraversallibrary",
    version=version,
    author="Klarna Bank AB",
    author_email="ai.automation.gb@klarna.com",
    description="Abstractions of web interactions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/klarna-incubator/wtl",
    python_requires=">=3.7",
    packages=["wtl"],
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
        "License :: Apache 2.0",
        "Operating System :: OS Independent",
    ],
)
