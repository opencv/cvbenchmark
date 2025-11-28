# Rating

The repository is to evaluate various CPUs' performance with OpenCV's Performance Tests. The scores are calibrated against a baseline score of 100 (which is the score of a **Broadcom BCM2711** by default). Higher scores indicate better CPU performance.

![](perf/benchmark.png?raw=true)

## How to compute the score

OpenCV's Performance Tests evaluate the speed of OpenCV functions run under controlled conditions. Each OpenCV module includes several test suites, and each test suite contains multiple test cases. For each test case, a performance score is computed as:

$$ score = \frac{\text{Baseline CPU Time}}{\text{CPU Time}} \times 100 $$

where:
- Baseline CPU Time is the arithmetic mean runtime (in milliseconds) of the test case measured on the baseline CPU.
- CPU Time is the corresponding runtime measured on the tested CPU. 

The geometric mean of all test case scores within a test suite represents the score on that test suite. Similarly, the geometric mean of all test suite scores forms the score on the module.
**The overall benchmark score** is obtained as the geometric mean of all module scores.

After the benchmark completes, detailed scores are reported as:


| module     |   Amlogic A311D |   Amlogic A311D2 |   Apple M1 |   Apple M4 |   Horizon Robotics Sunrise 3 |   Huawei Kunpeng |   Intel Core i7-12700K |   Intel Core i9-9880H |   Rockchip RK3568 |   Rockchip RK3568B2 |   Rockchip RK3588S2 |   SpacemiT M1 |   StarFive JH7110 |
|:-----------|----------------:|-----------------:|-----------:|-----------:|-----------------------------:|-----------------:|-----------------------:|----------------------:|------------------:|--------------------:|--------------------:|--------------:|------------------:|
| calib3d    |          168.5  |           167.83 |     805.11 |    1276.45 |                        57.12 |           180.74 |                1060.27 |                670.97 |             92.17 |               89.21 |              379.78 |         86.56 |             35.38 |
| core       |          157.2  |           157.9  |     964.48 |    1573.05 |                        57.54 |           178.97 |                1227.25 |                709.42 |             81.14 |               77.41 |              368.45 |        107.72 |             26.96 |
| features2d |          148.54 |           187.02 |     823.6  |    1753.81 |                        49.69 |           141.08 |                1686.13 |                852.97 |             72.93 |               71.62 |              328.12 |        103.65 |             30.52 |
| imgproc    |          151.89 |           160.65 |     865.98 |    1514.13 |                        52.4  |           178.01 |                1451.1  |                799.71 |             82.88 |               79.7  |              337.92 |        119.81 |             33.73 |
| objdetect  |          140.49 |           143.46 |     646.15 |    1191.21 |                        45.13 |           181.85 |                1189    |                658.11 |             67.34 |               65.16 |              339.64 |         65.25 |             33.72 |
| **Score**  |      **153.04** |       **162.76** | **814.22** |**1447.36** |                    **52.16** |       **171.35** |            **1305.04** |            **734.44** |         **78.83** |            **76.2** |          **350.23** |     **94.55** |         **31.92** |

*The baseline CPU is Broadcom BCM2711.*

CPU specs:
- **Broadcom BCM2711**: quad-core ARM Cortex-A72 (ARMv8, 1.5 GHz). Corresponding SBC used is Raspberry Pi 4 Model B.
- **Amlogic A311D**: quad-core ARM Cortex-A73 (2.2 GHz) and dual-core ARM Cortex-A53 (1.8 GHz). Corresponding SBC used is Khadas VIM3.
- **Amlogic A311D2**: quad-core ARM Cortex-A73 (2.2 GHz) and quad-core ARM Cortex-A53 (2.0 GHz). Corresponding SBC used is Khadas VIM4.
- **Apple M1**: 4 performance cores (3.2 GHz) and 4 efficiency cores.
- **Apple M4**: 4 performance cores (4.4 GHz) and 6 efficiency cores.
- **Horizon Robotics Sunrise 3**: quad-core ARM Cortex-A53 (1.2 GHz). Corresponding SBC used is Horizon Robotics X3_PI_V1.2.
- **Huawei KunPeng**: quad-core 64-bit Kunpeng CPU. Corresponding SBC used is OrangePi Kunpeng Pro V1.
- **Intel Core i7-12700K**: 8 Performance cores (3.60 GHz, turbo boost up to 4.90 GHz), 4 Efficient cores (2.70 GHz, turbo boost up to 3.80 GHz).
- **Intel Core i9-9880H**: 8 cores (2.3 GHz, turbo boost up to 4.8 GHz).
- **Rockchip RK3568**: quad-core ARM Cortex-A55 (up to 2.0 GHz). Corresponding SBC used is Firefly ROC-RK3568-PC.
- **Rockchip RK3568B2**: quad-core ARM Cortex-A55 (up to 2.0 GHz). Corresponding SBC used is ATK-DLRK3568.
- **Rockchip RK3588S2**: quad-core ARM Cortex-A76 (2.25 GHz) and quad-core ARM Cortex-A55 (1.8 GHz). Corresponding SBC used is Khadas Edge2 ARM PC.
- **SpacemiT M1**: octa-core 64-bit RISC-V AI CPU (clocked at 1.6 GHz). Corresponding SBC used is MUSE Pi V30.
- **StarFive JH7110**: quad-core 64-bit RISC-V CPU (1.5 GHz). Corresponding SBC used is StarFive VisionFive 2.

## How to run the benchmark

- Clone the repository to the target hardware:
```shell
git clone https://github.com/OpenCVChina/rating.git && cd rating
```

- Run *build.sh* to build OpenCV.
```bash
# for example if Rockchip RK3568 is used
bash build.sh arm
```

- Then run *run.sh* to run the performance tests across OpenCV modules. Results will be saved as *modulename-cpumodel.xml* respectively, e.g. *imgproc-Rockchip RK3568.xml*.
```bash
# for example if Rockchip RK3568 is used
bash run.sh 'Rockchip RK3568'
```

- Collect all the *modulename-cpumodel.xml* files from different hardware into the *your_path_to_rating_repo/perf* directory on a single hardware, then run the following scripts to obtain the CPU scores:
```bash
bash compare.sh
python rate.py
```
> **Note**
> The default baseline CPU is the one on Raspberry Pi 4 Model B: Broadcom BCM2711. If a different CPU is used as the baseline CPU, run:
> ```bash
> # for example Intel Core i7-12700K is taken the baseline CPU
> bash compare.sh 'Intel Core i7-12700K'
> python rate.py
> ```

## License

This project is licensed under [Apache 2.0 License](./LICENSE).
