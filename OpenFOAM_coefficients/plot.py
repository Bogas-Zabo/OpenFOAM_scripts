import matplotlib.pyplot as plt
from pathlib import Path

# Locate the coefficient.dat file
script_dir = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
coeff_path = script_dir / "coefficient.dat"
if not coeff_path.exists():
    raise FileNotFoundError(f"coefficient.dat not found in {script_dir}")

with coeff_path.open("r") as file:
    lines = file.readlines()

# Skip header lines
data_lines = [line for line in lines if not line.startswith('#')]

# Extract Cd and Cl values
cd_values = []
cl_values = []
tempo=[]

iteracoes=0

for line in data_lines:
    columns = line.split()
    iteracoes+=1
    if len(columns) > 4 and iteracoes >= 0 and iteracoes < 10000:
        cd_values.append(float(columns[1]))  # Cd is the 2nd column (index 1)
        cl_values.append(float(columns[3]))  # Cl is the 4th column (index 3)
        tempo.append(iteracoes)

plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.plot(tempo, cl_values, label='Cl')
plt.title("Cl values over time")
plt.xlabel("Time")
plt.ylabel("Cl")
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(tempo, cd_values, label='Cd', color='orange')
plt.title("Cd values over time")
plt.xlabel("Time")
plt.ylabel("Cd")
plt.legend()

plt.tight_layout()
plt.show()
