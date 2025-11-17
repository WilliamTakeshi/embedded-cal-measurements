import pandas as pd
import glob

for csv in glob.glob("./measurements/nrf/*.csv"):
    df = pd.read_csv(csv)
    avg = df["time (s)"].mean()
    print(csv, avg*1000)

for csv in glob.glob("./measurements/stm/*.csv"):
    df = pd.read_csv(csv)
    avg = df["time (s)"].mean()
    print(csv, avg*1000)
