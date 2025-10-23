#!/bin/bash

if [ $# -lt 2 ]; then
  echo "Usage: $0 <arch> <cpu model> [module]" 
  echo "Example: run.sh arm 'Rockchip RK3568' OR run.sh arm 'Rockchip RK3568' imgproc"
  exit 1
fi

# Get the opencv_extra
if [ ! -d "opencv_extra" ]; then
    echo "Cannot find opencv_extra. Updating submodules."
    git submodule update --init --remote opencv_extra
elif [ -z "$(ls -A "opencv_extra")" ]; then
    echo "opencv_extra is empty. Updating submodules."
    git submodule update --init --remote opencv_extra
fi

# 4.x
modules=("calib3d" "core" "features2d" "imgproc" "objdetect")
# 5.x
#modules=("3d" "calib" "core" "features" "imgproc" "objdetect" "stereo")
if [ $# -ge 3 ]; then
    modules=("${@:3}")
fi

RESULT_DIR=perf/
if [ ! -d ${RESULT_DIR} ]; then
    mkdir ${RESULT_DIR}
fi

export OPENCV_TEST_DATA_PATH=$(pwd)/opencv_extra/testdata
if [ $1 = "risc-v" ] && [ $2 = "K1" ]; then
    export LD_LIBRARY_PATH=build/lib
fi

for module in "${modules[@]}"; do
    echo "PERFORMANCE TEST MODULE: $module"
    ./build/bin/opencv_perf_${module} --gtest_output=xml:${RESULT_DIR}/${module}-$2.xml --perf_force_samples=50 --perf_min_samples=50
done
