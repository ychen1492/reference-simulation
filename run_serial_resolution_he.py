import os
import pickle

import numpy as np
from darts.engines import redirect_darts_output
from matplotlib import pyplot as plt

from model import Model
import pandas as pd

from utils.read_files import from_las_to_poro

report_time = 100
total_time = 10000
nz = 10
def proxy_model_simulation(nx, ny):
    poro = np.concatenate([np.ones(nx*ny) * p for p in org_poro], axis=0)
    # calculate permeability, this is from Duncan's thesis
    org_perm = np.exp(110.744 * poro**3-171.8268*poro**2+92.9227*poro-2.047)
    perms = org_perm
    set_nx = nx
    set_dx = x_spacing / set_nx
    set_nz = nz
    set_dz = z_spacing / set_nz
    set_ny = ny
    set_dy = y_spacing / set_ny
    redirect_darts_output(' ')
    proxy_model = Model(total_time=total_time, set_nx=set_nx, set_ny=set_ny, set_nz=set_nz, set_dx=set_dx,
                        set_dy=set_dy, set_dz=set_dz, perms=perms, poro=poro, report_time_step=report_time,
                        overburden=0)
    proxy_model.init()
    proxy_model.run(export_to_vtk=False)

    td = pd.DataFrame.from_dict(proxy_model.physics.engine.time_data)

    return td, proxy_model


def run_simulation():
    # fixed ny = 80
    ny = 50
    # list_nx = [40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300]
    list_nx = [160, 180, 200, 220, 240, 260, 280, 300]
    for i in list_nx:
        temperature, geothermal_model = proxy_model_simulation(i, ny)

        if not os.path.exists('SerialResolution'):
            os.mkdir('SerialResolution')

        output_path = os.path.relpath(f'SerialResolution/temperature_resolution_dx_test_1.csv')
        if os.path.exists(output_path):
            df = pd.read_csv(output_path, delimiter=',')
            df[f'{x_spacing / geothermal_model.reservoir.nx:.2f}'] = temperature['PRD : temperature (K)']
            df.to_csv(output_path, index=False)
        else:
            temperature.rename(columns={'PRD : temperature (K)': f'{x_spacing / geothermal_model.reservoir.nx:.2f}'},
                               inplace=True)
            temperature[['time', f'{x_spacing / geothermal_model.reservoir.nx:.2f}']].to_csv(output_path, index=False)


if __name__ == '__main__':
    x_spacing = 4000
    y_spacing = 3600
    z_spacing = 100
    # read porosity from the file
    org_poro = from_las_to_poro('LogData/Well_HONSELERSDIJK_GT_01_depth_gr.las', nz)
    run_simulation()
