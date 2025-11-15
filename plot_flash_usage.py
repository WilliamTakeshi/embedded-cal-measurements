import matplotlib.pyplot as plt
import numpy as np

def plot_flash_comparison(ops, flash_hw, flash_sw, title, output_file):
    x = np.arange(len(ops))
    width = 0.35

    plt.figure(figsize=(10, 5))

    plt.bar(x - width/2, flash_hw, width, label="Hardware Accelerated")
    plt.bar(x + width/2, flash_sw, width, label="Software Only")

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
ops = ["AES-ECB-128", "SHA2-256", "EC-MULT", "ECDSA-SIGN-VERIFY"]
cracen_nrf = [7692, 8704, 13424, 19652]
rustcrypto_nrf = [13368, 15276, 31920, 46824]

#############################################
# Data for stm
#############################################
pac_stm = [7928, 7536, 8688, 10040]
rustcrypto_stm = [13340, 15908, 28176, 47044]

#############################################
# Generate both plots
#############################################
plot_flash_comparison(ops, cracen_nrf, rustcrypto_nrf,
                      "Flash Usage (nRF)", "plots/nrf/flash_usage.png")

plot_flash_comparison(ops, pac_stm, rustcrypto_stm,
                      "Flash Usage (STM)", "plots/stm/flash_usage.png")
