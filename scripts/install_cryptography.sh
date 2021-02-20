#!/bin/bash

export PYTHONPATH=$PYTHONPATH:.

PYTHON_VERSION=`python -c 'import sys; print(sys.version_info.minor)'`

if [ $PYTHON_VERSION -eq 5 ]; then
    pip install -r requirements/cryptography_legacy.txt;
    exit;
else
    pip install -r requirements/cryptography.txt;
    exit;
fi
exit 0;
