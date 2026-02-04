#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: $0 <cpu model> [opencv module]"
  printf "  %-16s %s\n" "-cpu model" "the model name of the target CPU"
  printf "  %-16s %s\n" "-opencv module" "default modules will be tested if no module specified: calib3d, core, features2d, imgproc, objdetect, dnn"
  echo "Example:"
  printf "  %-7s %s\n" "$0" "'Rockchip RK3568'"
  printf "  %-7s %s %s\n" "$0" "'Rockchip RK3568'" "imgproc"
  exit 1
fi

# Get the opencv_extra
if [ ! -d "opencv_extra" ]; then
    echo "Cannot find opencv_extra. Updating submodules."
    git submodule update --init --remote opencv_extra
elif [ -z "$(ls -A "opencv_extra")" ]; then
    echo "opencv_extra is empty. Updating submodules."
    git submodule update --init --remote opencv_extra
fi

# 4.x
modules=("calib3d" "core" "features2d" "imgproc" "objdetect" "dnn")
# 5.x
#modules=("3d" "calib" "core" "features" "imgproc" "objdetect" "stereo" "dnn")
if [ $# -ge 2 ]; then
    modules=("${@:2}")
fi

if [[ " ${modules[@]} " =~ " dnn " ]]; then
    python3 - <<'EOF'
import subprocess
import re
from pathlib import Path
import ast

root = Path.cwd()
dnn_dir = root / "opencv_extra/testdata/dnn"
perf_net = root / "opencv/modules/dnn/perf/perf_net.cpp"
download_model = root / "opencv_extra/testdata/dnn/download_models.py"

# extract model filenames
src = perf_net.read_text()
pattern = re.compile(r'processNet\s*\(\s*"([^"]+)"')
models = {Path(m.rsplit("/", 1)[-1]).name for m in pattern.findall(src)}

existing_models = {p.name for p in dnn_dir.rglob("*") if p.is_file()}
missing_models = {f for f in models if f not in existing_models}

# parse download_models.py
tree = ast.parse(download_model.read_text())
filename_to_name = {}

def get_str(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None

def extract_model(call_node, parent_name=None):
    name = None
    filename = None
    subs = []
    for kw in call_node.keywords:
        if kw.arg == "name":
            name = get_str(kw.value)
        elif kw.arg == "filename":
            filename = get_str(kw.value)
        elif kw.arg == "sub" and isinstance(kw.value, ast.List):
            subs = kw.value.elts
    effective_name = name or parent_name
    if filename and effective_name:
        basename = Path(filename).name
        filename_to_name[basename] = effective_name
    for sub in subs:
        if isinstance(sub, ast.Call) and getattr(sub.func, "id", None) == "Model":
            extract_model(sub, effective_name)

for node in ast.walk(tree):
    if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "Model":
        extract_model(node)

model_names = {filename_to_name[m] for m in missing_models if m in filename_to_name}

# Download each model directly
if model_names:
    print("DOWNLOADING DNN MODELS. THIS MAY TAKE A WHILE...")
    for name in sorted(model_names):
        print(f"Downloading {name}...")
        subprocess.run(
            [
                "python3",
                download_model,
                name,
                "--dst", dnn_dir
            ], 
            check=True)
EOF
fi

RESULT_DIR=perf/
if [ ! -d ${RESULT_DIR} ]; then
    mkdir ${RESULT_DIR}
fi

export OPENCV_TEST_DATA_PATH=$(pwd)/opencv_extra/testdata
for module in "${modules[@]}"; do
    echo "PERFORMANCE TEST MODULE: $module"
    if [[ "$module" == "dnn" ]]; then
        ./build/bin/opencv_perf_dnn \
            --gtest_output=xml:"${RESULT_DIR}/${module}-${1}.xml" \
            --gtest_filter=DNNTestNetwork* \
            --perf_force_samples=10 \
            --perf_min_samples=10
    else
        ./build/bin/opencv_perf_${module} --gtest_output=xml:"${RESULT_DIR}/${module}-${1}.xml" --perf_force_samples=20 --perf_min_samples=20
    fi
done
echo "PERFORMANCE TESTING FINISHED."