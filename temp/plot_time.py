import pandas as pd
import numpy as np
import glob
import os
import matplotlib.pyplot as plt
from scipy import stats

plt.rcParams.update({
    "axes.titlesize": 20,       # title of the axes
    "axes.labelsize": 18,       # x and y labels
    "xtick.labelsize": 16,      # x tick labels
    "ytick.labelsize": 16,      # y tick labels
    "legend.fontsize": 16,      # legend
    "figure.titlesize": 22      # figure title
})

#############################################
# Helper: compute mean and 95% CI
#############################################
def mean_and_ci(series, confidence=0.95):
    data = series.values
    n = len(data)
    mean = np.mean(data)
    se = stats.sem(data)
    h = se * stats.t.ppf((1 + confidence) / 2., n-1)
    return mean, h

#############################################
# Ask user which platform and impl
#############################################
platform = input("Enter platform (nrf/stm): ").strip().lower()
if platform not in ["nrf", "stm"]:
    raise ValueError("Invalid platform. Please enter 'nrf' or 'stm'.")

impl_input = input("Enter implementation (hw/sw): ").strip().lower()
if impl_input not in ["hw", "sw"]:
    raise ValueError("Invalid implementation. Please enter 'hw' or 'sw'.")

folder = os.path.join("measurements", platform)
output_folder = os.path.join("plots", platform)
os.makedirs(output_folder, exist_ok=True)

# Map implementation identifiers in filenames
IMPL_MAP = {
    "cracen": "hw",
    "pac": "hw",
    "rustcrypto": "sw"
}

#############################################
# Load data
#############################################
data = {}

for filename in glob.glob(os.path.join(folder, "*.csv")):
    base = os.path.basename(filename)
    for key, val in IMPL_MAP.items():
        if key in base and val == impl_input:
            op_name = base.replace(f"-{key}.csv", "")
            df = pd.read_csv(filename)
            data[op_name] = df
            break

if not data:
    raise ValueError(f"No data found for {platform} with {impl_input} implementation.")

#############################################
# Prepare means and CI
#############################################
ops = list(data.keys())
means = []
cis = []

for op in ops:
    df = data[op]
    mean, ci = mean_and_ci(df["time (ms)"])
    means.append(mean)
    cis.append(ci)

#############################################
# Plot all operations
#############################################
plt.figure(figsize=(10,5))
plt.bar(ops, means, yerr=cis, capsize=5, color="skyblue")
plt.yscale("log")
plt.ylabel("Time (ms log scale)")
plt.title(f"{platform.upper()} - {impl_input.upper()} Time per Operation")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(output_folder, f"time_{impl_input}.png"), dpi=300)
plt.close()

print(f"Plot saved as {os.path.join(output_folder, f'time_{impl_input}.png')}")
