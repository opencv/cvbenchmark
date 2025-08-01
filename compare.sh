#!/bin/bash
# 4.x
modules=("calib3d" "core" "dnn" "features2d" "imgcodecs" "imgproc" "objdetect" "photo" "stitching" "video" "videoio") # exclude "gapi"
# 5.x
#modules=("3d" "calib" "core" "dnn" "features" "imgcodecs" "imgproc" "objdetect" "photo" "stereo" "stitching" "video" "videoio")

if [ $1 = "risc-v" ]; then
    for module in "${modules[@]}"; do
        python opencv/modules/ts/misc/summary.py perf/i7-12700k/${module}.xml perf/gcc-${module}.xml -o html > perf/gcc-${module}.html
    done
    for module in "${modules[@]}"; do
        python opencv/modules/ts/misc/summary.py perf/i7-12700k/${module}.xml perf/clang-${module}.xml -o html > perf/clang-${module}.html
    done
else
    for module in "${modules[@]}"; do
        python opencv/modules/ts/misc/summary.py perf/i7-12700k/${module}.xml perf/${module}.xml -o html > perf/${module}.html
    done
fi
