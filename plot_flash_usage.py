import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({
    "axes.titlesize": 20,
    "axes.labelsize": 18,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
    "legend.fontsize": 16,
    "figure.titlesize": 22
})

def plot_flash_comparison(ops, flash_hw, flash_sw, title, output_file):
    x = np.arange(len(ops))
    width = 0.35

    plt.figure(figsize=(10, 5))

    plt.bar(x - width/2, flash_hw, width, label="Hardware Accelerated")
    plt.bar(x + width/2, flash_sw, width, label="RustCrypto")

    plt.xticks(x, ops)
    plt.ylabel("Flash (bytes)")
    plt.title(title)
    plt.legend()

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()


#############################################
# Data for nrf
#############################################
# Data generated using cargo size --release --bin "$BIN" -- -A | awk '/\.text|\.rodata|\.data/ {sum += strtonum($2)} END {print sum}'
# where $BIN is the binary name
ops = ["aes-128", "ec-mult", "ecdsa-sign-verify", "sha2-256"]
cracen_nrf = [7692, 13424, 19652, 8704]
rustcrypto_nrf = [13368, 31920, 46824, 15276]

#############################################
# Data for stm
#############################################
pac_stm = [7928, 8688, 10040, 7536]
rustcrypto_stm = [13340, 28176, 47044, 15908]

#############################################
# Generate both plots
#############################################
plot_flash_comparison(ops, cracen_nrf, rustcrypto_nrf,
                      "Flash Usage (nRF)", "plots/nrf/flash_usage.png")

plot_flash_comparison(ops, pac_stm, rustcrypto_stm,
                      "Flash Usage (STM)", "plots/stm/flash_usage.png")
