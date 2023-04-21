# Reference simulation of Direct Use Geothermal Systems
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
1. `model.py`
    - It inherents from `DartsModel`, where the initial contion, boundary condition, reservoir type, simulation engine can be defined
    - To avoid effect of pressure and temperature on water density, mass rate control is chosen as boundary condition
    - `grav` option in `Geothermal` class is set to `True` by default. 
2. `real_base.py`
    - It is a main file to generate base model for a homogeneous reservoir with given resolution and confining layers

## Results visualization
### Homogeneous reservoir
Following two tables show the base domain and resolution for a homogeneous reservoir, given a fixed injection/production rate. 
The serial forward simulation results which are used to decide this base can be found in [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7834079.svg)](https://doi.org/10.5281/zenodo.7834079). The colab link 
<a target="_blank" href="https://colab.research.google.com/github/ychen1492/reference-simulation/blob/main/ho_resolution_visualization.ipynb">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a> 
is to visulize the forward simulation results (loss and production temperature). Set the loss tolerance to $10^{-3}$, following resolution and confining layers result is decided for a homogeneous reservoir.

- resolution and confining layers

| dx     | dy | dz   | overburden layers |
|:----:    |:----:  |  :----: |  :----:  |
| 18.5m  | 27.5m     | 10m     | 22      |

for the given domain as follows
- domain

| x spacing    | y spacing | z spacing   | 
|:----:    |:----:  |  :----: |  
| 3000m  | 2500m     | 100m     | 
### Layered reservoir
Following two tables show the base domain and resolution for a layered reservoir, given a fixed injection/production rate using one well logs to get permeability and porosity for each layer. Link to all goethermal well log data [Geothermal Log](https://gitlab.com/puskar1998/geothermal_logs).
The serial forward simulation results which are used to decide this base can be found in 
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7834079.svg)](https://doi.org/10.5281/zenodo.7834079). The colab link 
<a target="_blank" href="https://colab.research.google.com/github/ychen1492/reference-simulation/blob/main/he_resolution_visualization.ipynb">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a>
is to visulize the forward simulation results (loss and production temperature). Set the loss tolerance to $10^{-3}$, following resolution and confining layers result is decided for a layered reservoir.

- resolution and confining layers

| dx     | dy | dz   | overburden layers |
|:----:    |:----:  |  :----: |  :----:  |
| 18m  | 20m     | 10m     | 22      |

for the given domain as follows

- domain

| x spacing    | y spacing | z spacing   | 
|:----:    |:----:  |  :----: |  
| 4000m  | 3600m     | 100m     | 