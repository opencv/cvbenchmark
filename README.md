# Rating

The repository is to rate various CPUs' performance with OpenCV's Performance Tests. The scores are calculated against a baseline CPU:

$$ Score = \frac{\text{Baseline CPU Time}}{\text{CPU Time}} \times 100 $$

OpenCV's Performance Tests measure the speed of various OpenCV key functions across modules run under controlled conditions. The **CPU Time** represents the mean execution time in milliseconds of key OpenCV functions within the performance test suite. The final average scores are geometric means of the ratios. 

## How To Get Scores With Rating

- On the hardware to be tested, clone the repository:
```shell
git clone https://github.com/OpenCVChina/rating.git && cd rating
```

- Run the scripts to build OpenCV and run the performance tests across modules. Results will be saved in `modulename-cpumodel.xml` respectively.
```bash
# for example RK3568 is used
bash build.sh arm
bash run.sh arm RK3568
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

## Benchmarks

| module     |     K1 |     M1 |   RK3568 |   i7-12700K |
|:-----------|-------:|-------:|---------:|------------:|
| calib3d    |  86.56 | 789.3  |    89.21 |     1047.36 |
| core       | 107.72 | 937.43 |    77.41 |     1129.9  |
| features2d | 103.65 | 827.43 |    71.62 |     1659.51 |
| imgproc    | 119.81 | 849.14 |    79.7  |     1318.76 |
| objdetect  |  65.25 | 622.16 |    65.16 |     1188.76 |
| Mean       |  94.55 | 797.92 |    76.2  |     1252.2  |
*Note: Baseline CPU score is 100. The higher the score is, better the performance of that CPU is.*

The baseline CPU is **Broadcom BCM2711**, quad-core ARM Cortex-A72 (ARMv8-A, 1.5 GHz), 4 threads.
- **K1**: SpacemiT Key Stone® K1, an octa-core 64-bit RISC-V AI CPU, 8 threads.
- **M1**: Apple M1, 4 performance cores (up to 3.2 GHz) and 4 efficiency cores, 8 threads.
- **RK3568**: Rockchip RK3568B2, quad-core ARM Cortex-A55 (up to 2.0 GHz), 4 threads.
- **i7-12700K**: Intel Core i7-12700K, 8 Performance cores (3.60 GHz, turbo up to 4.90 GHz), 4 Efficient cores (2.70 GHz, turbo up to 3.80 GHz), 20 threads.


## License

This project is licensed under [Apache 2.0 License](./LICENSE).
