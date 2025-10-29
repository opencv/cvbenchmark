# Rating

The repository is to evaluate various CPUs' performance with OpenCV's Performance Tests. The scores are calibrated against a baseline score of 100 (which is the score of an **Broadcom BCM2711** by default). Higher scores indicate better CPU performance.

![](perf/benchmark.png?raw=true)

## How to compute the score

OpenCV's Performance Tests evaluate the speed of OpenCV functions run under controlled conditions. Each OpenCV module includes several test suites, and each test suite contains multiple test cases. For each test case, a performance score is computed as:

$$ score = \frac{\text{Baseline CPU Time}}{\text{CPU Time}} \times 100 $$

where:
- Baseline CPU Time is the arithmetic mean runtime (in milliseconds) of the test case measured on the baseline CPU.
- CPU Time is the corresponding runtime measured on the tested CPU. 

The geometric mean of all test case scores within a test suite represents the score of that test suite. Similarly, the geometric mean of all test suite scores forms the score of the module.
**The overall benchmark score** is obtained as the geometric mean of all module scores.

After the benchmark completes, detailed scores are reported:

| module     |   Amlogic A311D |   Amlogic A311D2 |   Apple M1 |   Huawei Kunpeng |   Intel Core i7-12700K |   Rockchip RK3568 |   Rockchip RK3568B2 |   Rockchip RK3588S2 |   SpacemiT M1 |   StarFive JH7110 |   Sunrise 3 |
|:-----------|----------------:|-----------------:|-----------:|-----------------:|-----------------------:|------------------:|--------------------:|--------------------:|--------------:|------------------:|------------:|
| calib3d    |          168.5  |           167.83 |     805.11 |           180.74 |                1047.36 |             92.17 |               89.21 |              379.78 |         86.56 |             35.38 |       57.12 |
| core       |          157.2  |           157.9  |     964.48 |           178.97 |                1129.9  |             81.14 |               77.41 |              368.45 |        107.72 |             26.96 |       57.54 |
| features2d |          148.54 |           187.02 |     823.6  |           141.08 |                1659.51 |             72.93 |               71.62 |              328.12 |        103.65 |             30.52 |       49.69 |
| imgproc    |          151.89 |           160.65 |     865.98 |           178.01 |                1318.76 |             82.88 |               79.7  |              337.92 |        119.81 |             33.73 |       52.4  |
| objdetect  |          140.49 |           143.46 |     646.15 |           181.85 |                1188.76 |             67.34 |               65.16 |              339.64 |         65.25 |             33.72 |       45.13 |
| **Score**  |      **153.04** |       **162.76** | **814.22** |       **171.35** |            **1252.2**  |         **78.83** |            **76.2** |          **350.23** |     **94.55** |      **31.92** |           **52.16**|

*The baseline CPU is Broadcom BCM2711.*

CPU specs:
- **Broadcom BCM2711**: quad-core ARM Cortex-A72 (ARMv8, 1.5 GHz). Corresponding SBC used is Raspberry Pi 4 Model B.
- **Amlogic A311D**: quad-core ARM Cortex-A73 (2.2 GHz) and dual-core ARM Cortex-A53 (1.8 GHz). Corresponding SBC used is Khadas VIM3.
- **Amlogic A311D2**: quad-core ARM Cortex-A73 (2.2 GHz) and quad-core ARM Cortex-A53 (2.0 GHz). Corresponding SBC used is Khadas VIM4.
- **Apple M1**: 4 performance cores (up to 3.2 GHz) and 4 efficiency cores.
- **Huawei KunPeng**: quad-core 64-bit Kunpeng CPU. Corresponding SBC used is OrangePi Kunpeng Pro V1.
- **Intel Core i7-12700K**: 8 Performance cores (3.60 GHz, turbo up to 4.90 GHz), 4 Efficient cores (2.70 GHz, turbo up to 3.80 GHz).
- **Rockchip RK3568**: quad-core ARM Cortex-A55 (up to 2.0 GHz). Corresponding SBC used is Firefly ROC-RK3568-PC.
- **Rockchip RK3568B2**: quad-core ARM Cortex-A55 (up to 2.0 GHz). Corresponding SBC used is ATK-DLRK3568.
- **Rockchip RK3588S2**: quad-core ARM Cortex-A76 (2.25 GHz) and quad-core ARM Cortex-A55 (1.8 GHz). Corresponding SBC used is Khadas Edge2 ARM PC.
- **SpacemiT M1**: octa-core 64-bit RISC-V AI CPU (clocked at 1.6 GHz). Corresponding SBC used is MUSE Pi V30.
- **StarFive JH7110**: quad-core 64-bit RISC-V CPU (1.5 GHz). Corresponding SBC used is StarFive VisionFive 2.
- **Horizon Sunrise 3**: quad-core ARM Cortex-A53 (1.2 GHz). Corresponding SBC used is Horizon Robotics X3_PI_V1.2.

## How to run the benchmark

- On the hardware to be tested, clone the repository:
```shell
git clone https://github.com/OpenCVChina/rating.git && cd rating
```

- Run the scripts to build OpenCV and run the performance tests across modules. Results will be saved in `modulename-cpumodel.xml` respectively.
```bash
# for example if Rockchip RK3568 is used
bash build.sh arm
bash run.sh arm "Rockchip RK3568"
```

> **Note:**
> If you are running the repo with RISC-V (SpacemiT) CPU, clone the repo on both the build host and the target host. On the build host, download and extract the [toolchain](https://archive.spacemit.com/toolchain/spacemit-toolchain-linux-glibc-x86_64-v1.0.5.tar.xz) and set the environment variable.
> ```shell
> export TOOLCHAIN_DIR=/path/to/spacemit-toolchain-linux-glibc-x86_64-v1.0.5
> ```
> Run the scripts on the build host to cross build OpenCV.
> ```bash
> bash build.sh risc-v
> ```
> Then upload the directories *your_path_to_rating_repo/cross-build-gcc/bin* and *your_path_to_rating_repo/cross-build-gcc/lib* on the build host to the correspondent paths on the target host. Run the script to run the performance tests.
> ```bash
> bash run.sh risc-v K1
> ```

- Collect all the `modulename-cpumodel.xml` files from different devices into the directory *your_path_to_rating_repo/perf* on a single device, and then run the scripts to obtain the scores:
```bash
bash compare.sh
python rate.py
```
The default baseline CPU is the one used by Raspberry Pi 4 Model B, which is Broadcom BCM2711. If a different CPU is used as the baseline CPU, run:
```bash
bash compare.sh you-baseline-cpu-model
python rate.py
```

## License

This project is licensed under [Apache 2.0 License](./LICENSE).
