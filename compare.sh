#!/bin/bash

# 4.x
modules=("calib3d" "core" "features2d" "imgproc" "objdetect")
# 5.x
#modules=("3d" "calib" "core" "features" "imgproc" "objdetect" "stereo")

BASELINE="Broadcom BCM2711"
if [ $# -eq 1 ]; then
    BASELINE=$1
fi

for module in "${modules[@]}"; do
    echo "Comparing results of $module ..."
    python3 opencv/modules/ts/misc/summary.py perf/${module}-${BASELINE}.xml perf/${module}*.xml -o html > perf/${module}.html
done
