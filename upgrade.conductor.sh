#!/bin/bash

CUDA_BIN=/usr/local/cuda-11.6/bin/

echo "==========="
echo "nvidia-smi"
nvidia-smi
echo
echo "==========="
echo "nvcc -V  # NVidia Cuda Compiler"
echo "==========="
${CUDA_BIN}nvcc -V
echo "==========="

CUDA_INSTALLLER=/home/theather/Downdloads/NVidia/cuda_11.5.0_495.29.05_linux.run
if [ -x "${CUDA_INSTALLER}" ]; then
    . "${CUDA_INSTALLER}"
fi

