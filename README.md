# Reference simulation of Direct Use Geothermal Systems

- Before running any py files, make sure the environment install `requirements.txt`
    - Create a blank conda environment and activate it
    - Run `pip install -r <path to requirements.txt>` in terminal

### Files explanation
1. `model.py`
    - It inherents from `DartsModel`, where the initial contion, boundary condition, reservoir type, simulation engine can be defined
    - To avoid effect of pressure and temperature on water density, mass rate control is chosen as boundary condition
    - `grav` option in `Geothermal` class is set to `True` by default. 
2. `real_base.py`
    - It is a main file to generate base model for a homogeneous reservoir with given resolution and overburden and underburden layers
- domain

| x spacing    | y spacing | z spacing   | 
|:----:    |:----:  |  :----: |  
| 3000m  | 2500m     | 100m     | 
|
- resolution

| dx     | dy | dz   | overburden layers |
|:----:    |:----:  |  :----: |  :----:  |
| 18.5m  | 27.5m     | 10m     | 22      |
|

