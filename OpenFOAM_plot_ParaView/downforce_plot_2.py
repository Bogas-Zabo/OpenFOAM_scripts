from paraview.simple import *
import numpy as np
import matplotlib.pyplot as plt

# Car width in meters
car_width = 0.75

# Slice step distance in meters
step = 0.01

# Load OpenFOAM case
print("Loading OpenFOAM case")
foam_reader = OpenFOAMReader(FileName="open.foam")
foam_reader.MeshRegions = ['group/FWGroup']  # Adjust as needed

# Get the last timestep
print("Getting last step")
timesteps = foam_reader.TimestepValues
last_time = timesteps[-1]
print(f"Using last timestep: {last_time}")
UpdatePipeline(time=last_time)

case = foam_reader  # Use consistently

# Surface normals
print("Getting surface normals")
normals = SurfaceNormals(Input=case)
normals.ComputeCellNormals = 1
normals.Splitting = 0
UpdatePipeline(time=last_time)

# Convert Normals to cell data if needed
print("Converting cell data")
normals_to_cell = PointDatatoCellData(Input=normals)
normals_to_cell.PassPointData = 0
UpdatePipeline(time=last_time)

# Forces calc
print("Using forces formula")
calc = Calculator(Input=normals_to_cell)
calc.ResultArrayName = "Forces"
calc.Function = "1.225*pMean*Normals"
UpdatePipeline(time=last_time)


# Integrate the whole car
print("Integrating over car's surface")
car_integ = IntegrateVariables(Input=calc)
UpdatePipeline(time=last_time)

car_data = servermanager.Fetch(car_integ)
car_array = car_data.GetCellData().GetArray("Forces")
print(car_array.GetTuple(0)[0])
car_lft = car_array.GetTuple(0)[2] * 2
car_drag = car_array.GetTuple(0)[0] * 2

# Slice and integrate
x_vals = np.arange(step, car_width+0.05, step)
lft_vals = []

# Main slice loop
print("Going over each slice:")
for x in x_vals:
    sliceX = Slice(Input=calc)
    sliceX.SliceType = "Plane"
    sliceX.SliceType.Origin = [0, x, 0]
    sliceX.SliceType.Normal = [0, 1, 0]
    UpdatePipeline(time=last_time)

    integ = IntegrateVariables(Input=sliceX)
    UpdatePipeline(time=last_time)

    data = servermanager.Fetch(integ)
    try:
        array = data.GetCellData().GetArray("Forces")
        if array:
            z = array.GetTuple(0)[2]
        else:
            z = 0.0
    except:
        z = 0.0
    lft_vals.append(z)
    print(f"x = {x:.2f} m, lift = {z:.2f} N")

lft_other_half = list(reversed(lft_vals))
full_x_vals = np.arange(-car_width-0.05+step, car_width+0.05-step, step)
full_lft = lft_other_half + lft_vals

# Compute total downforce by integrating df_vals over x_vals
total_lift = np.trapz(lft_vals, x_vals) * 2
print(f"Total car lift = {car_lft:.2f} N")
print(f"Total integrated lift: {total_lift:.2f} N")
error = ((total_lift-car_lft)/car_lft)*100
print(f"Error: {error:.2f} %")

print(f"Total car drag = {car_drag:.2f} N")

# Plot and save
plt.plot(full_x_vals, full_lft)
plt.xlabel("x (m)")
plt.ylabel("lift (N)")
plt.title("Lift Distribution")
plt.grid(True)
plt.savefig("lift_plot_2.png", dpi=300)
print("Plot saved as lift_plot2.png")

output_filename = "distribution_lift_data2.txt"
np.savetxt(output_filename, np.column_stack((full_x_vals, full_lft)), 
           header="x (m)\tLift (N)", fmt="%.6f", delimiter="\t")
print(f"Lift distribution data saved to {output_filename}")
