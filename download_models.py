#!/usr/bin/env python3

import re
from pathlib import Path
import ast

root = Path.cwd()
dnn_dir = root / "opencv_extra/testdata/dnn"
perf_net = root / "opencv/modules/dnn/perf/perf_net.cpp"
download_model = root / "opencv_extra/testdata/dnn/download_models.py"

# extract model names used in perf_net.cpp
src = perf_net.read_text()
pattern = re.compile(r'processNet\s*\(\s*"([^"]+)"')
models = set()
for full_path in pattern.findall(src):
    m = full_path.rsplit("/", 1)[-1]
    models.add(m)
existing_models = {p.name for p in dnn_dir.rglob("*") if p.is_file()}
missing_models = {f for f in models if f not in existing_models}

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

model_names = {filename_to_name[m] for m in models if m in filename_to_name}

for name in sorted(model_names):
    print(name)
