#!/bin/bash

MATRIX_IO_DIR=~/source/github.com/matrix-io
MATRIX_IO_REPO=https://github.com/matrix-io

cd $MATRIX_IO_DIR
if [ ! -d "matrix-io.github.io" ]; then
   git clone $MATRIX_IO_REPO/matrix-io.github.io
fi
cd matrix-io.github.io

git pull
#npm install
