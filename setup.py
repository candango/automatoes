#!/usr/bin/env python
#
# Copyright 2019-2025 Flavio Garcia
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
from setuptools import find_packages, setup
import os

with open("README.md", "r") as fh:
    long_description = fh.read()


# Solution from http://bit.ly/29Yl8VN
def resolve_requires(requirements_file):
    requires = []
    if os.path.isfile(f"./{requirements_file}"):
        file_dir = os.path.dirname(f"./{requirements_file}")
        with open(f"./{requirements_file}") as f:
            for raw_line in f.readlines():
                line = raw_line.strip().replace("\n", "")
                if len(line) > 0:
                    if line.startswith("-r "):
                        partial_file = os.path.join(file_dir, line.replace(
                            "-r ", ""))
                        partial_requires = resolve_requires(partial_file)
                        requires = requires + partial_requires
                        continue
                    requires.append(line)
    return requires


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
    python_requires=">= 3.9",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
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
