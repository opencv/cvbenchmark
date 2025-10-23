import pandas as pd
from scipy.stats import gmean
import re
import argparse

parser = argparse.ArgumentParser(description="Process OpenCV performance results.")
parser.add_argument(
    "--output", default="score.md",
    help="Output Markdown filename"
)
parser.add_argument(
    "--modules", nargs="+", 
    help="Module Name(s)"
)
args = parser.parse_args()
output_file = args.output

# 4.x
modules=["calib3d", "core", "features2d", "imgproc", "objdetect"]
# 5.x
#modules=["3d", "calib", "core", "features", "imgproc", "objdetect", "stereo"]
if args.modules:
    modules = args.modules

df = pd.read_html(f"perf/{modules[0]}.html")[0]
rows, cols = df.shape
col_start = cols // 2 + 1
cols_to_calculate = list(range(col_start, cols))
dev_types = [re.search(r'-(.*?)\s+vs', s).group(1) for s in df.columns.tolist()[col_start:]]

result = dict()
result["module"] = []
for dev_type in dev_types:
    result[dev_type] = []


for module in modules:
    df = pd.read_html(f"perf/{module}.html")[0]
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