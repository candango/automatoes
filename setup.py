#!/usr/bin/env python
#
# Copyright 2019-2021 Flavio Garcia
# Copyright 2016-2017 Veeti Paananen under MIT License
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import automatoes
from codecs import open
from setuptools import find_packages, setup
import sys

try:
    # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:
    # for pip <= 9.0.3
    print("error: Upgrade to a pip version newer than 10. Run \"pip install "
          "--upgrade pip\".")
    sys.exit(1)

with open("README.md", "r") as fh:
    long_description = fh.read()


# Solution from http://bit.ly/29Yl8VN
def resolve_requires(requirements_file):
    try:
        requirements = parse_requirements("./%s" % requirements_file,
                                          session=False)
        return [str(ir.req) for ir in requirements]
    except AttributeError:
        # for pip >= 20.1.x
        # Need to run again as the first run was ruined by the exception
        requirements = parse_requirements("./%s" % requirements_file,
                                          session=False)
        # pr stands for parsed_requirement
        return [str(pr.requirement) for pr in requirements]


setup(
    name="automatoes",
    version=automatoes.get_version(),
    license=automatoes.__licence__,
    description=("Let's Encrypt/ACME V2 client replacement for Manuale. Manual"
                 " or automated your choice."),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/candango/automatoes",
    author=automatoes.get_author(),
    author_email=automatoes.get_author_email(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],
    packages=find_packages(),
    package_dir={'automatoes': "automatoes"},
    include_package_data=True,
    install_requires=resolve_requires("requirements/basic.txt"),
    entry_points={
        'console_scripts': [
            "automatoes = automatoes.cli:automatoes_main",
            "manuale = automatoes.cli:manuale_main",
        ],
    },
)
