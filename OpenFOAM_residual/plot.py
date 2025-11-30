import re
import matplotlib.pyplot as plt
from pathlib import Path
import sys


# Locate the log file
script_dir = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
log_path = script_dir / "log"
if not log_path.exists():
    raise FileNotFoundError(f"log not found in {script_dir}")

with log_path.open("r") as file:
    log_data = file.read()

# Regular expressions to match the data
time_pattern = re.compile(r'Time\s=\s(\d+)')
residual_pattern = re.compile(r'Solving\sfor\s(\w+),\s.*\sFinal\sresidual\s=\s([\deE+.-]+)')

# Initialize dictionaries to hold data
data = {'time': []}
variables = ['Ux', 'Uy', 'Uz', 'omega', 'k', 'p']
for var in variables:
    data[var] = []

# Process the log data
current_time = None
for line in log_data.split('\n'):
    time_match = time_pattern.match(line)
    if time_match:
        current_time = int(time_match.group(1))
        data['time'].append(current_time)
        for var in variables:
            data[var].append(None)  # Placeholder for missing data

    residual_match = residual_pattern.search(line)
    if residual_match and current_time is not None:
        var = residual_match.group(1)
        residual = float(residual_match.group(2))  # Convert to float to handle scientific notation
        data[var][-1] = residual

# Fill missing data with the last known value to avoid gaps in the graph
for var in variables:
    for i in range(1, len(data['time'])):
        if data[var][i] is None:
            data[var][i] = data[var][i - 1]

# Plot the data
plt.figure(figsize=(10, 6))
for var in variables:
    plt.plot(data['time'], data[var], label=var)

plt.xlabel('Time Step')
plt.ylabel('Final Residual')
plt.title('Final Residuals per Time Step for Different Variables')
plt.yscale('log')
plt.legend()
plt.show()

