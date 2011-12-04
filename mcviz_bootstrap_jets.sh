#!/bin/sh

set -e
set -u

if [[ ! -d env/bin ]]; then
    echo "This script sets up the mcviz.jet package"
    echo "It requires that MCViz is setup in development mode in the env/ directory."
    echo "Run ./mcviz_bootstrap.py first to do this, then rerun this script."
    exit -1
fi

git submodule update --init mcviz.jet
env/bin/pip install -e mcviz.jet
