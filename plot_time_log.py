import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
from scipy import stats

# --- CONFIG ---
platform = input("Enter platform (nrf/stm): ").strip().lower()
if platform not in ["nrf", "stm"]:
    raise ValueError("Invalid platform. Enter 'nrf' or 'stm'.")

data_folder = os.path.join("./measurements", platform)   # platform-specific folder
output_folder = "./figs"
os.makedirs(output_folder, exist_ok=True)

# --- HELPER FUNCTION ---
def mean_and_ci(series, confidence=0.95):
    data = series.values
    n = len(data)
    mean = np.mean(data)
    se = stats.sem(data)
    h = se * stats.t.ppf((1 + confidence) / 2., n-1)
    return mean, h

# --- LOAD FILES ---
hw_files = glob.glob(os.path.join(data_folder, "*cracen*.csv"))
sw_files = glob.glob(os.path.join(data_folder, "*rustcrypto*.csv"))

# --- PLOTTING FUNCTION ---
def plot_time(files, title, filename):
    ops = []
    means = []
    cis = []

    for f in files:
        df = pd.read_csv(f)
        mean, ci = mean_and_ci(df['time (ms)'])  # keep in ms
        op_name = os.path.basename(f).split('-')[0]  # use filename to label operation
        ops.append(op_name)
        means.append(mean)
        cis.append(ci)

    plt.figure(figsize=(8,5))
    plt.bar(ops, means, yerr=cis, capsize=5, color='skyblue')
    plt.yscale('log')
    plt.ylabel("Time (ms, log scale)")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, filename), dpi=300)
    plt.close()

# --- GENERATE PLOTS ---
plot_time(hw_files, f"{platform.upper()} Hardware Time", f"{platform}_hw_time.png")
plot_time(sw_files, f"{platform.upper()} Software Time", f"{platform}_sw_time.png")

print("Plots saved in:", output_folder)
