import pandas as pd
import numpy as np
import glob
import os
import matplotlib.pyplot as plt

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
def mean_and_ci(series):
    mean = series.mean()
    std = series.std()
    n = len(series)
    ci95 = 1.96 * (std / np.sqrt(n))
    return mean, ci95

#############################################
# Load all CSV files
#############################################
# Ask user which platform
platform = input("Enter platform (nrf/stm): ").strip().lower()
if platform not in ["nrf", "stm"]:
    raise ValueError("Invalid platform. Please enter 'nrf' or 'stm'.")

# Build folder path based on platform
folder = os.path.join("measurements", platform)

data = {}

COLUMN_MAP = {
    "time_ms": "time (ms)",
    "avg_current_mA": "Avg Current (mA)",
    "avg_power_mW": "Avg Power (mW)"
}

# Map file identifiers to implementation type
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
    "time_ms": {"label": "Time (ms)", "values": {}},
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
# Plotting function
#############################################
def plot_metric(metric_key, platform):
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
    
    ax.set_ylabel(label + (" (log scale)" if metric_key == "time_ms" else ""))
    ax.set_xticks(x)
    ax.set_xticklabels(ops)
    ax.set_title(f"{label}: Hardware vs Software ({platform.upper()})")
    ax.legend()
    
    if metric_key == "time_ms":
        ax.set_yscale("log")  # Log scale for time
    
    plt.tight_layout()
    
    # Ensure plots folder exists
    os.makedirs(f"plots/{platform}", exist_ok=True)
    plt.savefig(f"plots/{platform}/{metric_key}_comparison.png", dpi=300, bbox_inches='tight')
    plt.close()

#############################################
# Generate all three figures
#############################################
plot_metric("time_ms", platform)
plot_metric("avg_current_mA", platform)
plot_metric("avg_power_mW", platform)
