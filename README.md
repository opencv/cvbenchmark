# Rating

The repository is to rate SBC (Single Board Computer) CPUs performance with OpenCV's Performance Tests. CPU scores are calculated against a baseline CPU:

$$ Score = \frac{\text{CPU Score}}{\text{Baseline CPU Score}} \times 100 $$

OpenCV's Performance Tests measure the speed (not the accuracy) of various OpenCV key functions across modules run under controlled conditions. The **CPU Score** represents the mean execution time in milliseconds of key OpenCV functions within the performance test suite.

## How To Get Scores With Rating

- On the SBCs, clone the repository:
```shell
git clone https://github.com/OpenCVChina/rating.git && cd rating
```

- Run the scripts to build OpenCV and run the performance tests across modules. Results will be saved in `modulename-sbc.xml` respectively.
```bash
bash build.sh
bash run.sh
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
> bash run.sh risc-v
> ```

- Collect all the `modulename-sbc.xml` files from different devices into the directory *your_path_to_rating_repo/perf* on a single device, and then run the scripts to obtain the scores:
```bash
bash compare.sh
python rate.py
```

## Benchmarks

| module     |   rk3568 |   k1(gcc) |   k1(clang) |
|:-----------|---------:|---------:|-----------:|
| calib3d    |    88.82 |    83.74 |      72.64 |
| core       |    77.53 |   138.36 |     145.97 |
| features2d |    77.23 |    84.13 |      74    |
| imgproc    |    80.99 |   233.41 |     227.48 |
| objdetect  |    60.56 |    62.21 |      62.33 |
| photo      |    72.45 |    68    |      66.36 |
| stitching  |    73.06 |    63.64 |      60.62 |
| video      |    84.75 |   110.6  |      99.11 |
| Mean       |    76.92 |   105.51 |     101.06 |

The baseline CPU is **Broadcom BCM2711**, *rk3568* represents **Rockchip RK3568B2**, and *k1* represents **SpacemiT Key Stone® K1**.
SBCs are Raspberry Pi 4 Model B, ATK-DLRK3568 and SpacemiT MUSE Pi accordingly.

## License

This project is licensed under [Apache 2.0 License](./LICENSE).
