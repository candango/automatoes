#!/bin/bash

export PYTHONPATH="${PYTHONPATH}:."

PYTHON_MINOR_VERSION="$(python -c 'import sys; print(sys.version_info.minor)')"

if [ "${PYTHON_MINOR_VERSION}" -eq 5 ]; then
    uv pip install cryptography
    exit 0
fi

uv pip install cryptography
exit 0
