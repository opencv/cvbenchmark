import pandas as pd
from scipy.stats import gmean
import re
import os
import argparse
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import json

parser = argparse.ArgumentParser(description="Process OpenCV performance results.")
parser.add_argument(
    "--output", default="scores.md",
    help="Output scores filename"
)
parser.add_argument(
    "--modules", nargs="+",
    help="Module Name(s)"
)
parser.add_argument(
    "--figure", default=False, action="store_true",
    help="Create figure for each module"
)
args = parser.parse_args()
output_file = args.output

# 4.x
modules=["core", "imgproc", "features2d", "objdetect", "calib3d", "dnn"]
# 5.x
#modules=["core", "imgproc", "features", "objdetect", "3d", "calib", "stereo", "dnn"]
if args.modules:
    modules = args.modules

df = None
for module in modules:
    file_name = f"perf/{module}.html"
    if not os.path.exists(file_name):
        continue
    try:
        df = pd.read_html(file_name)[0]
        break
    except Exception as e:
        print(f"Error reading {file_name}: {e}")
        continue

if df is None:
    print("No valid performance HTML files found.")
    exit(1)

rows, cols = df.shape
col_start = cols // 2 + 1
cols_to_calculate = list(range(col_start, cols))
dev_types = [re.search(r'-(.*?)\s+vs', s).group(1) for s in df.columns.tolist()[col_start:]]

result = dict()
result["module"] = []
for dev_type in dev_types:
    result[dev_type] = []

for module in modules:
    file_name = f"perf/{module}.html"
    if not os.path.exists(file_name):
        continue
    try:
        df = pd.read_html(file_name)[0]
    except Exception as e:
        print(f"Error reading {file_name}: {e}")
        continue

    df['Group'] = df.iloc[:, 0].astype(str).str.split(':').str[0]

    result["module"].append(module)
    for col_idx in cols_to_calculate:
        col_name = df.columns[col_idx]
        df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
        valid_df = df.dropna(subset=[col_name])

        group_gmeans = valid_df.groupby('Group')[col_name].apply(lambda x: gmean(x[x > 0]) if any(x > 0) else float('nan'))
        file_col_gmean = gmean(group_gmeans.dropna()) if not group_gmeans.dropna().empty else float('nan')
        result[dev_types[col_idx - col_start]].append(file_col_gmean * 100)

df = pd.DataFrame(result)

mean_scores = df.drop(columns="module").apply(lambda x: gmean(x[x > 0]) if any(x > 0) else float('nan'))
df.loc['Score'] = ['Score'] + mean_scores.tolist()
numeric_cols = df.select_dtypes(include="number").columns
df[numeric_cols] = df[numeric_cols].round(2)

with open(output_file, "w") as f:
    f.write(df.to_markdown(index=False))
print(df.to_string(index=False))

# Create figures:
if args.figure:
    with open("processor.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    Baseline = f"{data['baseline']['Processor']}\n{data['baseline']['Cores']}"
    Processor = [f"{p['Processor']} | {p['Cores']} | {p['Arch']}" for p in data["processors"]]

    devices = [c for c in df.columns if c != "module"]

    ARCH_COLORS = {
        "ARM": "#7233F7",       # purple
        "RISC-V": "#EDAC1A",    # yellow
        "x86_64": "#00C7FD",    # cyan
        "Unknown": "#A01A1E"    # red
    }

    legend_items = [mpatches.Patch(color="gray", label="Baseline (ARM)")]
    for arch, color in ARCH_COLORS.items():
        if arch != "Unknown":
            legend_items.append(mpatches.Patch(color=color, label=arch))
    # legend_items.append(mpatches.Patch(color=ARCH_COLORS["Unknown"], label="Unknown"))

    # Loop over each row
    for _, row in df.iterrows():

        module_name = row["module"]

        score_map = dict(zip(devices, row[devices].astype(float)))

        labels = []
        scores = []
        colors = []

        labels.append(Baseline)
        scores.append(100)
        colors.append("gray")   # Baseline color

        for p in Processor:
            soc, cores, arch = [x.strip() for x in p.split("|")]
            if soc in score_map:
                labels.append(f"{soc}\n{cores}")
                scores.append(score_map[soc])

                colors.append(ARCH_COLORS.get(arch, ARCH_COLORS["Unknown"]))

        plt.figure(figsize=(10, 0.5 * len(labels)))

        y_pos = np.arange(len(labels))
        bars = plt.barh(y_pos, scores, color=colors)
        bars[0].set_color("gray")   # Baseline bar in gray

        plt.tick_params(axis='y', length=0)
        plt.yticks(y_pos, labels, fontweight='bold')
        plt.xticks([])

        if module_name == "Score":
            plt.title("Processor Benchmark", fontweight="bold")
        else:
            plt.title(module_name, fontweight="bold")
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
                fontsize=9
            )

        plt.tight_layout()
        # plt.show()
        print(f"Saving figure for {module_name}...")
        plt.savefig(f"perf/{module_name}.png")