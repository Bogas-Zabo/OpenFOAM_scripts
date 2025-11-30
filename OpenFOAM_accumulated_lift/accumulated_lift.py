import os
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import AutoMinorLocator
from pathlib import Path

# Locate the directory
folder_path = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()

txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]

plt.figure(figsize=(12, 8))

num = 0
for file in txt_files:
    file_path = os.path.join(folder_path, file)

    df = pd.read_csv(file_path, sep='\t', comment='#', header=0)

    if df.columns[0].startswith("#"):
        df.columns = [col.strip('#').strip() for col in df.columns]

    x = df.iloc[:, 0]
    y = df.iloc[:, 1]

    plt.plot(x, y, label="Aero package " + str(num), linewidth=2)
    num += 1

plt.title("Accumulated Lift vs x")
plt.xlabel("x (m)")
plt.ylabel("Accumulated Lift (N)")
plt.legend()

plt.minorticks_on()
plt.gca().xaxis.set_minor_locator(AutoMinorLocator(5))
plt.gca().yaxis.set_minor_locator(AutoMinorLocator(5))
plt.grid(which='both', linestyle='--', linewidth=0.5)
plt.grid(which='minor', linestyle=':', linewidth=0.3)

plt.ylim(top=400)
plt.tight_layout()
plt.show()
