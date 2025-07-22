#!/bin/bash
# 4.x
modules=("calib3d" "core" "dnn" "features2d" "imgcodecs" "imgproc" "objdetect" "photo" "stitching" "video" "videoio") # exclude "gapi"
# 5.x
#modules=("3d" "calib" "core" "dnn" "features" "imgcodecs" "imgproc" "objdetect" "photo" "stereo" "stitching" "video" "videoio")

for module in "${modules[@]}"; do
    python opencv/modules/ts/misc/summary.py perf/i7-12700k/${module}.xml perf/${module}.xml -o html > perf/${module}.html
done

