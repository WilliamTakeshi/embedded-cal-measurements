import pandas as pd
import numpy as np
import glob
import os
import matplotlib.pyplot as plt

#############################################
# Helper: compute mean and 95% CI
#############################################
def mean_and_ci(series):
    mean = series.mean()
    std = series.std()
    n = len(series)
    ci95 = 1.96 * (std / np.sqrt(n))
    return mean, ci95

#############################################
# Ask user for platform
#############################################
platform = input("Enter platform (nrf/stm): ").strip().lower()
if platform not in ["nrf", "stm"]:
    raise ValueError("Invalid platform. Please enter 'nrf' or 'stm'.")

folder = os.path.join("measurements", platform)

#############################################
# Load CSV files
#############################################
data = {}
for filename in glob.glob(os.path.join(folder, "*.csv")):
    base = os.path.basename(filename)

    if "cracen" in base or "pac" in base:
        impl = "HW"
    elif "rustcrypto" in base:
        impl = "SW"
    else:
        continue

    op = base.replace("-cracen.csv", "").replace("-pac.csv", "").replace("-rustcrypto.csv", "")

    df = pd.read_csv(filename)
    if op not in data:
        data[op] = {}
    data[op][impl] = df

#############################################
# Define groups
#############################################
group1 = ["aes-256", "sha-256"]            # symmetric
group2 = ["ecdsa", "ecc_scalar_mult"]      # asymmetric
groups = [group1, group2]
titles = ["Symmetric operations", "Asymmetric operations"]

#############################################
# Plot figure with 2 subplots
#############################################
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle(f"Time Comparison - {platform.upper()}")

for ax, group, subtitle in zip(axes, groups, titles):
    ops = []
    hw_means, hw_cis = [], []
    sw_means, sw_cis = [], []

    for op in group:
        if op not in data:
            print(f"Warning: {op} not found in {platform} measurements.")
            continue
        ops.append(op.upper())

        # Hardware in ms
        hw_mean, hw_ci = mean_and_ci(data[op]["HW"]["time (ms)"])
        hw_means.append(hw_mean)
        hw_cis.append(hw_ci)

        # Software in seconds
        sw_mean, sw_ci = mean_and_ci(data[op]["SW"]["time (ms)"]) / 1000.0
        sw_cis.append(sw_ci / 1000.0)
        sw_means.append(sw_mean)

    x = np.arange(len(ops))
    width = 0.35
    ax.bar(x - width/2, hw_means, width, yerr=hw_cis, capsize=5, label="Hardware (ms)")
    ax.bar(x + width/2, sw_means, width, yerr=sw_cis, capsize=5, label="Software (s)")
    ax.set_xticks(x)
    ax.set_xticklabels(ops)
    ax.set_ylabel("Time")
    ax.set_title(subtitle)
    ax.legend()
    # ax.set_yscale("log")  # keep log scale

plt.tight_layout(rect=[0, 0, 1, 0.95])
os.makedirs(f"plots/{platform}", exist_ok=True)
plt.savefig(f"plots/{platform}/time_hw_vs_sw_split.png", dpi=300, bbox_inches='tight')
plt.close()

print(f"Figure saved for platform: {platform}")
