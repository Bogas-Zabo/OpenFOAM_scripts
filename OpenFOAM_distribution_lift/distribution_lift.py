import os
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import AutoMinorLocator
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Locate the directory
folder_path = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()

txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]

plt.figure(figsize=(12, 8))

colors = plt.cm.nipy_spectral(np.linspace(0, 1, len(txt_files)))

num = 0
for file in txt_files:
    file_path = os.path.join(folder_path, file)

    df = pd.read_csv(file_path, sep='\t', comment='#', header=0)

    if df.columns[0].startswith("#"):
        df.columns = [col.strip('#').strip() for col in df.columns]

    x = df.iloc[:, 0]
    y = df.iloc[:, 1]

    plt.plot(x, y, label=f"Front Wing {num+1}", linewidth=2, color=colors[num])
    num += 1

plt.title("Lift distribution vs x")
plt.xlabel("x (m)")
plt.ylabel("Lift distribution (N)")
plt.legend()

plt.minorticks_on()
plt.gca().xaxis.set_minor_locator(AutoMinorLocator(5))
plt.gca().yaxis.set_minor_locator(AutoMinorLocator(5))
plt.grid(which='both', linestyle='--', linewidth=0.5)
plt.grid(which='minor', linestyle=':', linewidth=0.3)

plt.ylim(top=200)
plt.tight_layout()
plt.show()
