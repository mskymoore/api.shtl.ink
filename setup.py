#!/usr/bin/env python3

import os
import re
import sys
from setuptools import find_packages, setup


def read(*parts):
    """Read file."""
    filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), *parts)
    sys.stdout.write(filename)
    with open(filename, encoding="utf-8", mode="rt") as fp:
        return fp.read()


with open("./README.md") as readme_file:
    readme = readme_file.read()

setup(
    author="Sky Moore",
    author_email="mskymoore@gmail.com",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10"
    ],
    description="Python URL Shortener",
    include_package_data=True,
    install_requires=[
        "autopep8==1.6.0",
        "build==0.8.0",
        "fastapi==0.78.0",
        "jinja2==3.1.2",
        "multipart==0.2.4",
        "psycopg2-binary==2.9.3",
        "pytest==7.1.2",
        "pytest-cov==3.0.0",
        "python_multipart==0.0.5",
        "requests==2.28.0",
        "setuptools_rust==1.3.0",
        "sqlalchemy==1.4",
        "sqlalchemy_serializer==1.4.1",
        "uvicorn[standard]==0.17.6",
        "virtualenv==20.14.1"
    ],
    keywords=["url", "url_shortener", "api"],
    license="MIT license",
    long_description_content_type="text/markdown",
    long_description=readme,
    name="shtl-ink-api",
    packages=find_packages(include=["shtl_ink_api"]),
    url="https://github.com/mskymoore/url_shortener",
    version="0.0.20",
    zip_safe=True,
)
