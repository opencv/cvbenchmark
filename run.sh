#!/bin/bash

# Get opencv_extra
if [ ! -d "opencv_extra" ]; then
    echo "Cannot find opencv_extra. Updating submodules."
    git submodule update --init
fi

# 4.x
modules=("calib3d" "core" "dnn" "features2d" "imgcodecs" "imgproc" "objdetect" "photo" "stitching" "video" "videoio") # exclude "gapi"
# 5.x
#modules=("3d" "calib" "core" "dnn" "features" "imgcodecs" "imgproc" "objdetect" "photo" "stereo" "stitching" "video" "videoio")

RESULT_DIR=perf/
if [ $# -eq 0 ]; then
    RESULT_DIR=${RESULT_DIR}/new
else
    RESULT_DIR=${RESULT_DIR}/$1
fi

if [ -d ${RESULT_DIR} ]; then
    mkdir ${RESULT_DIR}
fi

export OPENCV_TEST_DATA_PATH=$(pwd)/opencv_extra/testdata
for module in "${modules[@]}"; do
    ./build/bin/opencv_perf_${module} --gtest_output=xml:perf/${module}.xml --perf_force_samples=50 --perf_min_samples=50
done
