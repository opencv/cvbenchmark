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
    TOOLCHAIN_FILE_GCC=$(pwd)/opencv/platforms/linux/riscv64-gcc.toolchain.cmake
    TOOLCHAIN_FILE_CLANG=$(pwd)/opencv/platforms/linux/riscv64-clang.toolchain.cmake
    # GCC
    cmake -G Ninja -B cross-build-gcc \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
        -DCMAKE_INSTALL_PREFIX=cross-build-gcc/install \
        -DCMAKE_C_COMPILER=${TOOLCHAIN_DIR}/bin/riscv64-unknown-linux-gnu-gcc \
        -DCMAKE_CXX_COMPILER=${TOOLCHAIN_DIR}/bin/riscv64-unknown-linux-gnu-g++ \
        -DCMAKE_TOOLCHAIN_FILE=${TOOLCHAIN_FILE_GCC} \
        -DCPU_BASELINE=RVV -DCPU_BASELINE_REQUIRE=RVV -DRISCV_RVV_SCALABLE=ON opencv
    # Clang
    cmake -G Ninja -B cross-build-clang \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
        -DCMAKE_INSTALL_PREFIX=cross-build-clang/install \
        -DRISCV_CLANG_BUILD_ROOT=${TOOLCHAIN_DIR} \
        -DRISCV_GCC_INSTALL_ROOT=${TOOLCHAIN_DIR} \
        -DCMAKE_TOOLCHAIN_FILE=${TOOLCHAIN_FILE_CLANG} \
        -DCPU_BASELINE=RVV -DCPU_BASELINE_REQUIRE=RVV -DRISCV_RVV_SCALABLE=ON opencv
    cmake --build cross-build-gcc --target install -j10
    cmake --build cross-build-clang --target install -j10
else
    echo "Building for ${iarch}"
    cmake -G Ninja -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=build/install opencv
    cmake --build build --target install -j6
fi
