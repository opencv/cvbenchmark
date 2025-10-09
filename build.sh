#!/bin/bash

# Check if a parameter is given
if [ $# -eq 0 ]; then
  echo "Usage: $0 <arch>. Available: x86, arm, risc-v"
  exit 1
fi

iarch="$1"
available_archs=("x86", "arm", "riscv-v")
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

# Get the latest opencv
if [ ! -d "opencv" ]; then
    echo "Cannot find opencv. Updating submodules."
    git submodule update --init --remote opencv
elif [ -z "$(ls -A "opencv")" ]; then
    echo "opencv is empty. Updating submodules."
    git submodule update --init --remote opencv
fi

# Configure and build opencv according to target platform
if [ ${iarch} = "risc-v" ]; then
    echo "Building OpenCV for risc-v"
    TOOLCHAIN_FILE_GCC=$(pwd)/opencv/platforms/linux/riscv64-gcc.toolchain.cmake
    # GCC
    cmake -G Ninja -B build \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
        -DCMAKE_INSTALL_PREFIX=build/install \
        -DCMAKE_C_COMPILER=${TOOLCHAIN_DIR}/bin/riscv64-unknown-linux-gnu-gcc \
        -DCMAKE_CXX_COMPILER=${TOOLCHAIN_DIR}/bin/riscv64-unknown-linux-gnu-g++ \
        -DCMAKE_TOOLCHAIN_FILE=${TOOLCHAIN_FILE_GCC} \
        -DWITH_OPENCL=OFF -DWITH_LAPACK=OFF -DWITH_EIGEN=OFF -DBUILD_TESTS=OFF \
        -DCPU_BASELINE=RVV -DCPU_BASELINE_REQUIRE=RVV -DRISCV_RVV_SCALABLE=ON opencv
    cmake --build build --target install -j10
else
    echo "Building OpenCV for ${iarch}"
    cmake -G Ninja -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=build/install \
    -DWITH_OPENCL=OFF -DWITH_LAPACK=OFF -DWITH_EIGEN=OFF -DBUILD_TESTS=OFF opencv
    cmake --build build --target install -j4
fi
