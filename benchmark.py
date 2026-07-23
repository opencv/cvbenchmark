import argparse
import glob
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True

OPENCV_4_MODULES = ["calib3d", "core", "features2d", "imgproc", "objdetect", "dnn"]
OPENCV_5_MODULES = [
    "calib",
    "stereo",
    "geometry",
    "core",
    "features",
    "imgproc",
    "objdetect",
    "dnn",
]
OPENCV_4_ONLY_MODULES = {"calib3d", "features2d"}
OPENCV_5_ONLY_MODULES = {"calib", "stereo", "geometry", "features"}
ALL_KNOWN_MODULES = list(dict.fromkeys(OPENCV_4_MODULES + OPENCV_5_MODULES))
AVAILABLE_ARCH_PARAM = ["x86", "arm", "riscv", "riscvv"]


def format_elapsed(seconds):
    seconds = int(round(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}h {minutes}m {seconds}s"
    if minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def run_cmd(cmd, cwd=None, env=None):
    return subprocess.run(
        [str(x) for x in cmd],
        cwd=cwd,
        check=True,
        text=True,
        env=env,
    )


def positive_int(value):
    try:
        parsed = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid integer value: {value!r}")
    if parsed < 1:
        raise argparse.ArgumentTypeError("value must be greater than 0")
    return parsed


def safe_build_dir(opencv_version):
    return Path(f"build_{opencv_version.replace('/', '_')}")


def has_opencv_module(module):
    return (Path("opencv/modules") / module / "perf").is_dir()


def modules_available(candidates):
    return [module for module in candidates if has_opencv_module(module)]


def detect_modules_from_opencv_tree():
    if any(has_opencv_module(module) for module in OPENCV_5_ONLY_MODULES):
        return modules_available(OPENCV_5_MODULES) or OPENCV_5_MODULES

    if any(has_opencv_module(module) for module in OPENCV_4_ONLY_MODULES):
        return modules_available(OPENCV_4_MODULES) or OPENCV_4_MODULES

    return OPENCV_4_MODULES


def detect_opencv_extra_ref(modules):
    module_set = set(modules or [])

    if module_set & OPENCV_5_ONLY_MODULES:
        return "5.x"
    if module_set & OPENCV_4_ONLY_MODULES:
        return "4.x"
    if any(has_opencv_module(module) for module in OPENCV_5_ONLY_MODULES):
        return "5.x"
    if any(has_opencv_module(module) for module in OPENCV_4_ONLY_MODULES):
        return "4.x"

    return "4.x"


def detect_perf_modules(build_dir):
    expected_modules = detect_modules_from_opencv_tree()
    detected_modules = [
        module
        for module in expected_modules
        if (build_dir / f"bin/opencv_perf_{module}").is_file()
    ]
    return detected_modules or expected_modules


def module_has_perf_output(perf_dir, module):
    return bool(glob.glob(str(perf_dir / f"{module}-*.xml"))) or (
        perf_dir / f"{module}.html"
    ).is_file()


def modules_with_perf_output(perf_dir, candidates):
    return [module for module in candidates if module_has_perf_output(perf_dir, module)]


def detect_score_modules(opencv_version):
    perf_dir = Path("perf") / opencv_version
    if perf_dir.is_dir():
        if modules_with_perf_output(perf_dir, OPENCV_5_ONLY_MODULES):
            modules = modules_with_perf_output(perf_dir, OPENCV_5_MODULES)
            if modules:
                return modules

        if modules_with_perf_output(perf_dir, OPENCV_4_ONLY_MODULES):
            modules = modules_with_perf_output(perf_dir, OPENCV_4_MODULES)
            if modules:
                return modules

        modules = modules_with_perf_output(perf_dir, ALL_KNOWN_MODULES)
        if modules:
            return modules

    return detect_modules_from_opencv_tree()


def ensure_submodule(path, args=()):
    target = Path(path)
    if not target.is_dir() or not any(target.iterdir()):
        print(f"{path} is missing or empty. Updating submodules...")
        run_cmd(["git", "submodule", "update", "--init", *args, path])


def checkout_repo_ref(path, ref, label):
    ensure_submodule(path)

    print(f"Checking out {label}: {ref}")
    run_cmd(["git", "fetch", "origin", "--tags"], cwd=path)

    try:
        run_cmd(["git", "checkout", ref], cwd=path)
    except subprocess.CalledProcessError:
        run_cmd(["git", "checkout", "-B", ref, f"origin/{ref}"], cwd=path)


def checkout_opencv(opencv_version):
    checkout_repo_ref("opencv", opencv_version, "OpenCV branch/commit")


def checkout_opencv_extra(modules):
    checkout_repo_ref(
        "opencv_extra",
        detect_opencv_extra_ref(modules),
        "opencv_extra branch/ref",
    )


def build_opencv(arch, opencv_version, jobs=None):
    if arch not in AVAILABLE_ARCH_PARAM:
        raise SystemExit(
            f"Unknown input arch: {arch}. Available architectures: {', '.join(AVAILABLE_ARCH_PARAM)}"
        )

    jobs = jobs or os.cpu_count() or 1
    build_start = time.perf_counter()
    build_dir = safe_build_dir(opencv_version)
    checkout_opencv(opencv_version)

    if build_dir.is_dir() and any(build_dir.iterdir()):
        print(f"OpenCV build {build_dir} already exists. Skipping build opencv.")
        print(
            "OPENCV BUILD ELAPSED TIME: "
            f"{format_elapsed(time.perf_counter() - build_start)}"
        )
        return build_dir

    print(f"Building OpenCV in {build_dir} ...")

    cmake_args = [
        "-DCMAKE_BUILD_TYPE=Release",
        f"-DCMAKE_INSTALL_PREFIX={build_dir}/install",
        "-DWITH_OPENCL=OFF",
        "-DWITH_LAPACK=OFF",
        "-DWITH_EIGEN=OFF",
        "-DBUILD_TESTS=OFF",
        "-DBUILD_opencv_python3=OFF",
    ]
    if arch == "riscvv":
        cmake_args += [
            "-DCPU_BASELINE=RVV",
            "-DCPU_BASELINE_REQUIRE=RVV",
            "-DRISCV_RVV_SCALABLE=ON",
        ]

    run_cmd(["cmake", "-B", build_dir, *cmake_args, "opencv"])
    print(f"Building OpenCV with {jobs} job(s).")
    run_cmd(["cmake", "--build", build_dir, "--target", "install", f"-j{jobs}"])

    print(
        "OPENCV BUILD FINISHED. ELAPSED TIME: "
        f"{format_elapsed(time.perf_counter() - build_start)}"
    )
    return build_dir


# Future option: download DNN models required by perf_net.cpp before running dnn.
# This is intentionally disabled because the current DNN perf command excludes
# DNNTestNetwork* tests.
#
# def ensure_dnn_models():
#     import ast
#
#     root = Path.cwd()
#     dnn_dir = root / "opencv_extra/testdata/dnn"
#     perf_net = root / "opencv/modules/dnn/perf/perf_net.cpp"
#     download_model = root / "opencv_extra/testdata/dnn/download_models.py"
#
#     src = perf_net.read_text()
#     pattern = re.compile(r'processNet\s*\(\s*"([^"]+)"')
#     models = {Path(m.rsplit("/", 1)[-1]).name for m in pattern.findall(src)}
#
#     existing_models = {p.name for p in dnn_dir.rglob("*") if p.is_file()}
#     missing_models = {f for f in models if f not in existing_models}
#
#     tree = ast.parse(download_model.read_text())
#     filename_to_name = {}
#
#     def get_str(node):
#         if isinstance(node, ast.Constant) and isinstance(node.value, str):
#             return node.value
#         return None
#
#     def extract_model(call_node, parent_name=None):
#         name = None
#         filename = None
#         subs = []
#
#         for kw in call_node.keywords:
#             if kw.arg == "name":
#                 name = get_str(kw.value)
#             elif kw.arg == "filename":
#                 filename = get_str(kw.value)
#             elif kw.arg == "sub" and isinstance(kw.value, ast.List):
#                 subs = kw.value.elts
#
#         effective_name = name or parent_name
#         if filename and effective_name:
#             filename_to_name[Path(filename).name] = effective_name
#
#         for sub in subs:
#             if isinstance(sub, ast.Call) and getattr(sub.func, "id", None) == "Model":
#                 extract_model(sub, effective_name)
#
#     for node in ast.walk(tree):
#         if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "Model":
#             extract_model(node)
#
#     model_names = {filename_to_name[m] for m in missing_models if m in filename_to_name}
#
#     if model_names:
#         print("DOWNLOADING DNN MODELS. THIS MAY TAKE A WHILE...")
#         env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
#         for name in sorted(model_names):
#             print(f"Downloading {name}...")
#             run_cmd([sys.executable, "-B", download_model, name, "--dst", dnn_dir], env=env)
#
#
def run_perf(arch, cpu_model, opencv_version, modules=None, jobs=None, threads=None):
    print("Evaluating ...")
    build_dir = build_opencv(arch, opencv_version, jobs)

    if modules is None:
        modules = detect_perf_modules(build_dir)
        print(f"Detected OpenCV performance modules: {', '.join(modules)}")

    checkout_opencv_extra(modules)

    # if "dnn" in modules:
    #     ensure_dnn_models()

    if not build_dir.is_dir() or not any(build_dir.iterdir()):
        raise SystemExit(f"OpenCV build {build_dir} is missing or empty. Exit.")

    result_dir = Path("perf") / opencv_version
    result_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["OPENCV_TEST_DATA_PATH"] = str(Path.cwd() / "opencv_extra/testdata")

    if threads is not None:
        cpu_threads = os.cpu_count() or 1
        if threads > cpu_threads:
            threads = cpu_threads

    perf_start = time.perf_counter()
    failed_modules = []
    for module in modules:
        print(f"PERFORMANCE TEST MODULE: {module}")
        result_file = result_dir / f"{module}-{cpu_model}.xml"

        if result_file.is_file() and result_file.stat().st_size > 0:
            print(f"Performance result {result_file} already exists. Skipping run perf.")
            continue

        cmd = [
            build_dir / f"bin/opencv_perf_{module}",
            f"--gtest_output=xml:{result_file}",
            "--perf_force_samples=20",
            "--perf_min_samples=20",
        ]
        if threads is not None:
            cmd.append(f"--perf_threads={threads}")
        if module == "dnn":
            cmd.append("--gtest_filter=-DNNTestNetwork*")

        try:
            result = subprocess.run([str(x) for x in cmd], check=False, text=True, env=env)
        except OSError as exc:
            failed_modules.append((module, str(exc)))
            print(f"ERROR: Performance test module {module} failed: {exc}. Continuing.")
            continue

        if result.returncode != 0:
            failed_modules.append((module, f"exit code {result.returncode}"))
            print(
                f"ERROR: Performance test module {module} failed "
                f"with exit code {result.returncode}. Continuing."
            )

    if failed_modules:
        failed_text = ", ".join(
            f"{module} ({reason})"
            for module, reason in failed_modules
        )
        print(f"PERFORMANCE TESTING FINISHED WITH FAILURES: {failed_text}")
    else:
        print("PERFORMANCE TESTING FINISHED.")
    print(
        "PERFORMANCE TESTING ELAPSED TIME: "
        f"{format_elapsed(time.perf_counter() - perf_start)}"
    )


def compare_module(perf_dir, module, baseline):
    base_file = perf_dir / f"{module}-{baseline}.xml"
    pattern = str(perf_dir / f"{module}-*.xml")
    score_dir = perf_dir / "score"
    score_dir.mkdir(parents=True, exist_ok=True)
    output_file = score_dir / f"{module}.html"

    print(f"Comparing results of module: {module} ...")

    if not base_file.is_file():
        print(f"ERROR: Baseline file not found: {base_file}")
        return False

    matches = glob.glob(pattern)
    if len(matches) == 1 and Path(matches[0]) == base_file:
        print(f"ERROR: No comparison files found for module: {module}")
        return False

    summary_py = Path("opencv/modules/ts/misc/summary.py")
    if not summary_py.is_file():
        print(f"ERROR: OpenCV summary script not found: {summary_py}")
        return False

    result = subprocess.run(
        [sys.executable, "-B", str(summary_py), str(base_file), pattern, "-o", "html"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )

    if result.returncode != 0:
        print(f"ERROR: Failed to compare module: {module}")
        if result.stderr:
            print(result.stderr.rstrip())
        return False

    output_file.write_text(result.stdout)
    print(f"Generated: {output_file}")
    return True


def compare_results(opencv_version, modules, baseline):
    perf_dir = Path("perf") / opencv_version
    if not perf_dir.is_dir():
        raise SystemExit(f"ERROR: Performance directory not found: {perf_dir}")

    for module in modules:
        compare_module(perf_dir, module, baseline)


def get_device_types(df):
    _, cols = df.shape
    col_start = cols // 2 + 1
    dev_types = []

    for column in df.columns.tolist()[col_start:]:
        match = re.search(r"-(.*?)\s+vs", column)
        if not match:
            raise ValueError(f"Unable to parse device name from column: {column}")
        dev_types.append(match.group(1))

    return col_start, list(range(col_start, cols)), dev_types


def read_first_valid_html(opencv_version, modules):
    import pandas as pd

    score_dir = Path("perf") / opencv_version / "score"
    for module in modules:
        file_name = score_dir / f"{module}.html"
        if not file_name.exists():
            continue

        try:
            return pd.read_html(file_name)[0]
        except Exception as exc:
            print(f"Error reading {file_name}: {exc}")

    return None


def summarize_scores(opencv_version, modules, output_file):
    import pandas as pd
    from scipy.stats import gmean

    score_dir = Path("perf") / opencv_version / "score"
    score_dir.mkdir(parents=True, exist_ok=True)

    df = read_first_valid_html(opencv_version, modules)
    if df is None:
        raise SystemExit("No valid performance HTML files found.")

    col_start, cols_to_calculate, dev_types = get_device_types(df)

    result = {"module": []}
    for dev_type in dev_types:
        result[dev_type] = []

    for module in modules:
        file_name = score_dir / f"{module}.html"
        if not file_name.exists():
            continue

        try:
            df = pd.read_html(file_name)[0]
        except Exception as exc:
            print(f"Error reading {file_name}: {exc}")
            continue

        df["Group"] = df.iloc[:, 0].astype(str).str.split(":").str[0]

        result["module"].append(module)
        for col_idx in cols_to_calculate:
            col_name = df.columns[col_idx]
            df[col_name] = pd.to_numeric(df[col_name], errors="coerce")
            valid_df = df.dropna(subset=[col_name])

            group_gmeans = valid_df.groupby("Group")[col_name].apply(
                lambda x: gmean(x[x > 0]) if any(x > 0) else float("nan")
            )
            file_col_gmean = (
                gmean(group_gmeans.dropna())
                if not group_gmeans.dropna().empty
                else float("nan")
            )
            result[dev_types[col_idx - col_start]].append(file_col_gmean * 100)

    score_df = pd.DataFrame(result)

    mean_scores = score_df.drop(columns="module").apply(
        lambda x: gmean(x[x > 0]) if any(x > 0) else float("nan")
    )
    score_df.loc["Score"] = ["Score"] + mean_scores.tolist()

    numeric_cols = score_df.select_dtypes(include="number").columns
    score_df[numeric_cols] = score_df[numeric_cols].round(2)

    output_path = score_dir / output_file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(score_df.to_markdown(index=False))

    print(score_df.to_string(index=False))
    print(f"Generated: {output_path}")

    return score_df


def create_figures(opencv_version, score_df):
    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt
    import numpy as np

    score_dir = Path("perf") / opencv_version / "score"
    score_dir.mkdir(parents=True, exist_ok=True)

    with open("processor.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    baseline = f"{data['baseline']['Processor']}\n{data['baseline']['Cores']}"
    processors = [
        f"{p['Processor']} | {p['Cores']} | {p['Arch']}"
        for p in data["processors"]
    ]

    devices = [c for c in score_df.columns if c != "module"]

    arch_colors = {
        "ARM": "#7233F7",
        "RISC-V": "#EDAC1A",
        "x86_64": "#00C7FD",
        "Unknown": "#A01A1E",
    }

    legend_items = [mpatches.Patch(color="gray", label="Baseline (ARM)")]
    for arch, color in arch_colors.items():
        if arch != "Unknown":
            legend_items.append(mpatches.Patch(color=color, label=arch))

    for _, row in score_df.iterrows():
        module_name = row["module"]
        score_map = dict(zip(devices, row[devices].astype(float)))

        labels = [baseline]
        scores = [100]
        colors = ["gray"]

        for processor in processors:
            soc, cores, arch = [x.strip() for x in processor.split("|")]
            if soc in score_map:
                labels.append(f"{soc}\n{cores}")
                scores.append(score_map[soc])
                colors.append(arch_colors.get(arch, arch_colors["Unknown"]))

        plt.figure(figsize=(10, 0.5 * len(labels)))

        y_pos = np.arange(len(labels))
        bars = plt.barh(y_pos, scores, color=colors)
        bars[0].set_color("gray")

        plt.tick_params(axis="y", length=0)
        plt.yticks(y_pos, labels, fontweight="bold")
        plt.xticks([])

        title = "Processor Benchmark" if module_name == "Score" else module_name
        plt.title(title, fontweight="bold")
        plt.legend(handles=legend_items, loc="upper right", frameon=False)
        plt.gca().invert_yaxis()

        for spine in plt.gca().spines.values():
            spine.set_visible(False)

        for bar, score in zip(bars, scores):
            plt.text(
                bar.get_width(),
                bar.get_y() + bar.get_height() / 2,
                f" {score:.2f}",
                va="center",
                ha="left",
                fontsize=9,
            )

        plt.tight_layout()
        output_path = score_dir / f"{module_name}.png"
        print(f"Saving figure for {module_name}...")
        plt.savefig(output_path)
        plt.close()


def score_perf(opencv_version, baseline, modules, output, figure):
    if modules is None:
        modules = detect_score_modules(opencv_version)
        print(f"Detected OpenCV performance modules: {', '.join(modules)}")

    compare_results(opencv_version, modules, baseline)
    score_df = summarize_scores(opencv_version, modules, output)

    if figure:
        create_figures(opencv_version, score_df)


def add_run_args(parser):
    parser.add_argument("--arch", required=True,
        help="Target architecture for building OpenCV. Available: x86, arm, riscv, riscvv")
    parser.add_argument("--cpu-model", required=True,
        help="CPU model name for the target device. Used in result file names.")
    parser.add_argument("--version", default="4.13.0",
        help="OpenCV version (branch, tag, or commit) to build and run performance tests. Default: 4.13.0")
    parser.add_argument("--modules", nargs="+",
        help="List of modules to run performance tests.")
    parser.add_argument("--jobs", "-j", type=positive_int,
        help="Number of build jobs used to build OpenCV. Default: CPU count.")
    parser.add_argument("--threads", type=positive_int,
        help="Number of worker threads used to run performance tests. Default: all threads.")


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark CPU performance with OpenCV's Performance Tests."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    perf_parser = subparsers.add_parser("perf", help="Build OpenCV and run performance tests.")
    add_run_args(perf_parser)

    score_parser = subparsers.add_parser(
        "score", help="Compare XML results and compute CPU scores."
    )
    score_parser.add_argument("--version", default="4.13.0",
        help="OpenCV version (branch, tag, or commit) to compute scores. Default: 4.13.0")
    score_parser.add_argument("--baseline", default="Broadcom BCM2711",
        help="Baseline CPU model name for comparison. Default: Broadcom BCM2711")
    score_parser.add_argument("--modules", nargs="+",
        help="List of modules to compute scores.")
    score_parser.add_argument("--output", default="scores.md",
        help="Output markdown file for scores. Default: scores.md")
    score_parser.add_argument("--figure", action="store_true",
        help="Generate figures for each module and the overall score.")

    bench_parser = subparsers.add_parser(
        "bench", help="Run OpenCV performance tests and compute CPU scores."
    )
    add_run_args(bench_parser)
    bench_parser.add_argument("--baseline", default="Broadcom BCM2711",
        help="Baseline CPU model name for comparison. Default: Broadcom BCM2711")
    bench_parser.add_argument("--output", default="scores.md",
        help="Output markdown file for scores. Default: scores.md")
    bench_parser.add_argument("--figure", action="store_true",
        help="Generate figures for each module and the overall score.")

    args = parser.parse_args()

    if args.command == "perf":
        run_perf(args.arch, args.cpu_model, args.version, args.modules, args.jobs, args.threads)
    elif args.command == "score":
        score_perf(args.version, args.baseline, args.modules, args.output, args.figure)
    elif args.command == "bench":
        run_perf(args.arch, args.cpu_model, args.version, args.modules, args.jobs, args.threads)
        score_perf(args.version, args.baseline, args.modules, args.output, args.figure)


if __name__ == "__main__":
    main()
