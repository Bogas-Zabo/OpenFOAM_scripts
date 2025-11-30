from paraview.simple import *
import numpy as np
import matplotlib.pyplot as plt

# Car length and step
car_len = 3.1
step = 0.01
offset = -0.9873

print("Loading OpenFOAM case")
foam_reader = OpenFOAMReader(FileName="open.foam")
foam_reader.MeshRegions = ['group/bodyGroup', 'group/chassiGroup', 'group/FTGroup', 'group/FWGroup', 'group/intakeGroup', 'group/pilotGroup', 'group/radiatorGroup', 'group/RTGroup', 'group/RWGroup', 'group/suspGroup', 'group/SWGroup', 'group/undertrayGroup']

print("Getting last step")
timesteps = foam_reader.TimestepValues
last_time = timesteps[-1]
print(f"Using last timestep: {last_time}")
UpdatePipeline(time=last_time)

case = foam_reader

print("Getting surface normals")
normals = SurfaceNormals(Input=case)
normals.ComputeCellNormals = 1
normals.Splitting = 0
UpdatePipeline(time=last_time)

print("Converting cell data")
normals_to_cell = PointDatatoCellData(Input=normals)
normals_to_cell.PassPointData = 0
UpdatePipeline(time=last_time)

print("Computing lift")
lift_calc = Calculator(Input=normals_to_cell)
lift_calc.ResultArrayName = "Lift"
lift_calc.Function = "1.225*pMean*Normals_Z"
UpdatePipeline(time=last_time)

car_lift_integ = IntegrateVariables(Input=lift_calc)
UpdatePipeline(time=last_time)
car_lift_data = servermanager.Fetch(car_lift_integ)
car_lift_val = car_lift_data.GetCellData().GetArray("Lift").GetTuple1(0) * 2

x_vals = np.arange(0, car_len+0.1, step)
x_offset_vals = np.arange(offset, car_len+0.1+offset, step)
lift_vals = []
accumulated_lift_vals = []
drag_vals = []

accumulated_lift_val = 0

print("Going over each slice:")
for x in x_offset_vals:
    # Slice lift
    slice_lift = Slice(Input=lift_calc)
    slice_lift.SliceType = "Plane"
    slice_lift.SliceType.Origin = [x, 0, 0]
    slice_lift.SliceType.Normal = [1, 0, 0]
    UpdatePipeline(time=last_time)
    
    integ_lift = IntegrateVariables(Input=slice_lift)
    UpdatePipeline(time=last_time)
    data_lift = servermanager.Fetch(integ_lift)
    try:
        arr_lift = data_lift.GetCellData().GetArray("Lift")
        lift = arr_lift.GetTuple1(0) * 2 if arr_lift else 0.0
    except:
        lift = 0.0
    lift_vals.append(lift)
    accumulated_lift_val += lift*step
    accumulated_lift_vals.append(accumulated_lift_val)
    print(f"x = {x:.2f} m, lift = {lift:.2f} N")

# Integrated totals
total_lift = np.trapz(lift_vals, x_offset_vals)
lift_error = ((total_lift - car_lift_val) / car_lift_val) * 100

print(f"\nTotal Lift (direct)       = {car_lift_val:.2f} N")
print(f"Total Lift (integrated)   = {total_lift:.2f} N")
print(f"Lift error                = {lift_error:.2f} %")

# Plot both
plt.plot(x_vals, lift_vals, label="Lift")
plt.xlabel("x (m)")
plt.ylabel("Force (N)")
plt.title("Lift Distribution")
plt.legend()
plt.grid(True)
plt.savefig("lift_plot.png", dpi=300)
print("Plot saved as lift_plot.png")

output_filename = "accumulated_lift_data.txt"
np.savetxt(output_filename, np.column_stack((x_vals, accumulated_lift_vals)), 
           header="x (m)\tAccumulated Lift (N)", fmt="%.6f", delimiter="\t")
print(f"Accumulated lift data saved to {output_filename}")

output_filename = "distribution_lift_data.txt"
np.savetxt(output_filename, np.column_stack((x_vals, lift_vals)), 
           header="x (m)\tLift (N)", fmt="%.6f", delimiter="\t")
print(f"Lift distribution data saved to {output_filename}")
