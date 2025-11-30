#!/usr/bin/env python3
import math
from pathlib import Path

car_size = 3.0      # car size (length)
cell_size = 0.8     # desired cell size (level 0 refinment)
corner_radius = 10  # corner radius
corner_lateral_space = 3*car_size  # space between car and corner wall (3 * car_size)
innerR   = corner_radius-corner_lateral_space    # inner radius
outerR   = corner_radius+corner_lateral_space     # outer radius
totalAngleDeg = 180   # fixed, but you CAN change it
height   = 8    # 3 * car_size

nr = (corner_lateral_space*2)//cell_size            # radial cells per block
nt = 18           # circumferential cells per block
nz = height/cell_size            # vertical cells

carAngleDeg = 90   # where the car should be placed
                    # script will move that to (0,0,0)

# Two 90° blocks
blockAnglesDeg = [0, 90, 180]

# Car shift
carAngleRad = math.radians(carAngleDeg)
carX = (innerR+outerR)/2 * math.cos(carAngleRad)
carY = (innerR+outerR)/2 * math.sin(carAngleRad)
shiftX = -carX
shiftY = -carY
shiftZ = 0.0

def vtx(r, thetaDeg, z):
    theta = math.radians(thetaDeg)
    x = r * math.cos(theta) + shiftX
    y = r * math.sin(theta) + shiftY
    return f"({x:.6f} {y:.6f} {z:.6f})"

vertices = []
blocks = []
edges = []

vcount = 0
for i in range(2):      # 2 blocks: 0–90 and 90–180
    a0 = blockAnglesDeg[i]
    a1 = blockAnglesDeg[i+1]
    amid = 0.5 * (a0 + a1)

    # bottom ring
    v0 = vtx(innerR, a0, 0)
    v1 = vtx(outerR, a0, 0)
    v2 = vtx(outerR, a1, 0)
    v3 = vtx(innerR, a1, 0)

    # top ring
    v4 = vtx(innerR, a0, height)
    v5 = vtx(outerR, a0, height)
    v6 = vtx(outerR, a1, height)
    v7 = vtx(innerR, a1, height)

    # Add vertices
    vertices += [v0, v1, v2, v3, v4, v5, v6, v7]

    # hex block definition
    blocks.append(f"    hex ({vcount} {vcount+1} {vcount+2} {vcount+3} "
                  f"{vcount+4} {vcount+5} {vcount+6} {vcount+7}) "
                  f"({nr} {nt} {nz}) simpleGrading (1 1 1)")

    # arc midpoints
    edges.append(f"    arc {vcount} {vcount+3} {vtx(innerR, amid, 0)}")
    edges.append(f"    arc {vcount+1} {vcount+2} {vtx(outerR, amid, 0)}")
    edges.append(f"    arc {vcount+4} {vcount+7} {vtx(innerR, amid, height)}")
    edges.append(f"    arc {vcount+5} {vcount+6} {vtx(outerR, amid, height)}")

    vcount += 8


# Generate blockMeshDict
text = f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                |                                                 |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  v2012                                 |
|   \  /    A nd           | Website:  www.openfoam.com                      |
|    \/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/

FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

scale 1.0;

vertices
(
    {"\n    ".join(vertices)}
);

blocks
(
{"\n".join(blocks)}
);

edges
(
{"\n".join(edges)}
);

boundary
(
    innerSide
    {{
        type slip;
        faces
        (
            (0 4 7 3)
            (8 12 15 11)
        );
    }}

    outerSide
    {{
        type slip;
        faces
        (
            (1 2 6 5)
            (9 10 14 13)
        );
    }}

    inlet
    {{
        type patch;
        faces
        (
            (0 1 5 4)
        );
    }}

    outlet
    {{
        type patch;
        faces
        (
            (11 15 14 10)
        );
    }}

    top
    {{
        type slip;
        faces
        (
            (4 5 6 7)
            (12 13 14 15)
        );
    }}

    bottom
    {{
        type wall;
        faces
        (
            (0 3 2 1)
            (8 11 10 9)
        );
    }}
);

mergePatchPairs();

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

"""

# Locate the directory
script_dir = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
blockMeshDict_path = script_dir / "blockMeshDict"

with blockMeshDict_path.open("w") as f:
    f.write(text)

print("blockMeshDict completed")
