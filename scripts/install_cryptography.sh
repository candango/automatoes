#!/bin/bash

export PYTHONPATH="${PYTHONPATH}:."

PYTHON_MINOR_VERSION="$(python -c 'import sys; print(sys.version_info.minor)')"

if [ "${PYTHON_MINOR_VERSION}" -eq 5 ]; then
    pip install -r requirements/cryptography_legacy.txt
    exit 0
fi

pip install -r requirements/cryptography.txt
exit 0
