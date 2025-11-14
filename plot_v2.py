import pandas as pd
import numpy as np
import glob
import os
import matplotlib.pyplot as plt

plt.rcParams.update({
    "axes.titlesize": 20,
    "axes.labelsize": 18,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
    "legend.fontsize": 16,
    "figure.titlesize": 22
})

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
COLUMN_MAP = {
    "time_ms": "time (ms)",
    "avg_current_mA": "Avg Current (mA)",
    "avg_power_mW": "Avg Power (mW)"
}

IMPL_MAP = {
    "cracen": "HW",
    "pac": "HW",
    "rustcrypto": "SW"
}

for filename in glob.glob(os.path.join(folder, "*.csv")):
    base = os.path.basename(filename)
    
    impl_label = None
    op_name = None
    for key, val in IMPL_MAP.items():
        if key in base:
            impl_label = val
            op_name = base.replace(f"-{key}.csv", "")
            break
    if impl_label is None:
        continue  # skip unknown files

    df = pd.read_csv(filename)
    
    if op_name not in data:
        data[op_name] = {}
    data[op_name][impl_label] = df

operations = list(data.keys())

#############################################
# Prepare results per metric
#############################################
results = {
    "time_ms": {"label": "Time", "values": {}},
    "avg_current_mA": {"label": "Avg Current (mA)", "values": {}},
    "avg_power_mW": {"label": "Avg Power (mW)", "values": {}},
}

for op in operations:
    for impl in ["HW", "SW"]:
        df = data[op][impl]
        for key in results:
            mean, ci = mean_and_ci(df[COLUMN_MAP[key]])
            results[key]["values"].setdefault(op, {})[impl] = (mean, ci)

#############################################
# Plotting: Time with two subplots (HW / SW)
#############################################
hw_ops = [op for op in operations if "HW" in data[op]]
sw_ops = [op for op in operations if "SW" in data[op]]

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle(f"Time Comparison - {platform.upper()}")

# Hardware subplot
x = np.arange(len(hw_ops))
hw_means = [results["time_ms"]["values"][op]["HW"][0] for op in hw_ops]
hw_cis = [results["time_ms"]["values"][op]["HW"][1] for op in hw_ops]
axes[0].bar(x, hw_means, yerr=hw_cis, capsize=5)
axes[0].set_xticks(x)
axes[0].set_xticklabels([op.upper() for op in hw_ops])
axes[0].set_ylabel("Time (ms)")
axes[0].set_title("Hardware")
# axes[0].set_yscale("log")

# Software subplot (convert to seconds)
x = np.arange(len(sw_ops))
sw_means = [results["time_ms"]["values"][op]["SW"][0] for op in sw_ops]
sw_cis = [results["time_ms"]["values"][op]["SW"][1] for op in sw_ops]
axes[1].bar(x, sw_means, yerr=sw_cis, capsize=5, color = "darkorange")
axes[1].set_xticks(x)
axes[1].set_xticklabels([op.upper() for op in sw_ops])
axes[1].set_ylabel("Time (s)")
axes[1].set_title("Software")
# axes[1].set_yscale("log")

plt.tight_layout(rect=[0, 0, 1, 0.95])
os.makedirs(f"plots/{platform}", exist_ok=True)
plt.savefig(f"plots/{platform}/time_hw_vs_sw_separate.png", dpi=300, bbox_inches='tight')
plt.close()

#############################################
# Plotting: Current and Power (same as before)
#############################################
def plot_metric(metric_key):
    label = results[metric_key]["label"]
    metric_data = results[metric_key]["values"]
    
    ops = list(metric_data.keys())
    x = np.arange(len(ops))
    width = 0.35
    
    hw_means = [metric_data[op]["HW"][0] for op in ops]
    hw_errs  = [metric_data[op]["HW"][1] for op in ops]
    
    sw_means = [metric_data[op]["SW"][0] for op in ops]
    sw_errs  = [metric_data[op]["SW"][1] for op in ops]

    fig, ax = plt.subplots(figsize=(10, 5))
    
    ax.bar(x - width/2, hw_means, width, yerr=hw_errs, capsize=5, label="Hardware")
    ax.bar(x + width/2, sw_means, width, yerr=sw_errs, capsize=5, label="Software")
    
    ax.set_ylabel(label)
    ax.set_xticks(x)
    ax.set_xticklabels(ops)
    ax.set_title(f"{label}: Hardware vs Software ({platform.upper()})")
    ax.legend()
    
    plt.tight_layout()
    os.makedirs(f"plots/{platform}", exist_ok=True)
    plt.savefig(f"plots/{platform}/{metric_key}_comparison.png", dpi=300, bbox_inches='tight')
    plt.close()

plot_metric("avg_current_mA")
plot_metric("avg_power_mW")

print(f"All figures saved for platform: {platform}")
