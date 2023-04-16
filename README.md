# Reference simulation of Direct Use Geothermal Systems
Link to jupyter notebook visualization of heterogeneous case
<a target="_blank" href="https://colab.research.google.com/github/ychen1492/reference-simulation/blob/heterogeneous-case/he_resolution_visualization.ipynb">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a>
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
    - It is a main file to generate base model for a homogeneous reservoir with given resolution and overburden and underburden layers

Following two tables show the base domain and resolution for a homogeneous reservoir, given a fixed injection/production rate. The serial forward simulation results which are used to decide this base can be found in [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7828527.svg)](https://doi.org/10.5281/zenodo.7828527)
- domain

| x spacing    | y spacing | z spacing   | 
|:----:    |:----:  |  :----: |  
| 3000m  | 2500m     | 100m     | 

- resolution

| dx     | dy | dz   | overburden layers |
|:----:    |:----:  |  :----: |  :----:  |
| 18.5m  | 27.5m     | 10m     | 22      |


