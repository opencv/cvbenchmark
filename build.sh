#!/bin/bash

# Check if a parameter is given
if [ $# -eq 0 ]; then
  echo "Usage: $0 <arch>. Available: x64, arm, risc-v"
  exit 1
fi

iarch="$1"
available_archs=("x64", "arm", "riscv-v")
found=true
for arch in "${available_archs[@]}"; do
    if [ "$iarch" != "$arch" ]; then
        found=false
        break
    fi
done
if [ ! ${found} ]; then
    echo "Unkonwn arch ${iarch}. exiting ..."
    exit 1
else
    echo "Evaluating ..."
fi

# Get latest opencv
if [ ! -d "opencv" ]; then
    echo "Cannot find opencv. Updating submodules."
    git submodule update --init
fi

# Configure and build opencv according to target platform
if [ ${arch} = "risc-v" ]; then
    echo "Building for risc-v"
    # [TODO] build for risc-v
else
    echo "Building for ${iarch}"
    cmake -G Ninja -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=build/install opencv
fi
cmake --build build --target install -j6
