#!/bin/bash

# Get opencv_extra
git clone https://github.com/opencv/opencv_extra
cd opencv_extra
git checkout 4.x
cd ..

# 4.x
modules=("calib3d" "core" "dnn" "features2d" "imgcodecs" "imgproc" "objdetect" "photo" "stitching" "video" "videoio") # exclude "gapi"
# 5.x
#modules=("3d" "calib" "core" "dnn" "features" "imgcodecs" "imgproc" "objdetect" "photo" "stereo" "stitching" "video" "videoio")

for module in "${modules[@]}"; do
    ./build/bin/opencv_perf_${module} --gtest_output=xml:perf/${module}.xml --perf_force_samples=50 --perf_min_samples=50
done
