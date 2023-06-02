# Reference simulation of Direct Use Geothermal Systems

[fair-software.nl](https://fair-software.nl) recommendations:

![Github](https://img.shields.io/badge/github-repo-000.svg?logo=github&labelColor=gray&color=blue/target?=https://github.com/ychen1492/reference-simulation)
[![GitHub](https://img.shields.io/github/license/ychen1492/reference-simulation)](https://github.com/ychen1492/reference-simulation/blob/main/LICENSE)


Code quality checks

![GitHub Workflow Status (with branch)](https://img.shields.io/github/actions/workflow/status/ychen1492/reference-simulation/python-app.yml?branch=main)

## What is DUGS?
Direct Use Geothermal Systems (DUGS), which are also known as low enthalpy geothermal systems, are mainly conduction mechanism dominated.
## System requirements
- Windows 10
- Language: Python

## Computational Dependencies
- Packages and libraries
    - Before running any py files, make sure the environment install `requirements.txt`
    - Create a blank conda environment and activate it
    - Run `pip install -r <path to requirements.txt>` in terminal

## Files explanation
1. `src/model.py`
    - It inherents from `DartsModel`, where the initial contion, boundary condition, reservoir type, simulation engine can be defined
    - To avoid effect of pressure and temperature on water density, mass rate control is chosen as boundary condition
    - `grav` option in `Geothermal` class is set to `True` by default. 
2. `src/run_serial_resolution.py`
    - It is a main file to run multiple forward simultions to investigate the production temperature of different types of the reservoirs
    - The results of these files are csv files which have production temperature for each dx, dy and dz values
3. `src/run_serial_layers.py`
    - It is a main file to run multiple forward simulations to investigate the minimum confining layers 
    - The results fo these files are csv files whcih record the temperature and pressure of the top reservoir layer
4. `src/real_base.py`
    - It is the file which is used to generate the vtk results using the the resolution and confining layers information derived from `src/run_serial_resolution.py`.



## Results visualization
Following two tables show the base domain, resolution and the number of confining layeres for a homogeneous reservoir, a stratified reservoir and a heterogeneous reservoir, given a fixed injection/production rate. Dutch geothermal well log data: [Geothermal Log](https://gitlab.com/puskar1998/geothermal_logs) is used to generate porosity and permeability field for stratified reservoirs and heterogeneous reservoirs. 
- resolution and confining layers

| dx     | dy | dz   | overburden layers |
|:----:    |:----:  |  :----: |  :----:  |
| 20m  | 75m     | 10m     | 22      |

for the given domain as follows
- domain

| x spacing    | y spacing | z spacing   | 
|:----:    |:----:  |  :----: |  
| 4500m  | 4000m     | 100m     | 

The serial forward simulation results which are used to decide above bases for three types of the reservoirs can be found in 

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7834079.svg)](https://doi.org/10.5281/zenodo.7834079).

**Before running following colab links, please make sure download all above dataset** 

The colab link to visualize the homogeneous reservoir base case can be found at

<a target="_blank" href="https://colab.research.google.com/github/ychen1492/reference-simulation/blob/main/ho_resolution_visualization.ipynb">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a>

The colab link to visualize the stratified reservoir base case can be found at

<a target="_blank" href="https://colab.research.google.com/github/ychen1492/reference-simulation/blob/main/layered_resolution_visualization.ipynb">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a>

The colab link to visualize the heterogeneous reservoir base case can be found at

<a target="_blank" href="https://colab.research.google.com/github/ychen1492/reference-simulation/blob/main/he_resolution_visualization.ipynb">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a>
