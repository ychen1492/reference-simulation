import os

import numpy as np
from darts.engines import redirect_darts_output

from model import Model
import pandas as pd

report_time = 100
total_time = 10000

np.random.seed(550)
x_spacing = 4500
y_spacing = 3500
z_spacing = 100
# read porosity from the file
porosity = pd.read_csv('LogData/porosity_californie_sidetrack.csv')
np.random.seed(200)


def proxy_model_simulation(nx, ny):
    # fix nz to be 10
    nz = 10
    org_poro = np.random.choice(porosity['PORO'].to_numpy(), nz)
    poro = np.concatenate([np.ones(nx*ny) * p for p in org_poro], axis=0)
    # calculate permeability
    org_perm = 0.0663 * np.exp(29.507 * org_poro) * 10000
    perms = np.concatenate([np.ones(nx*ny) * perm for perm in org_perm], axis=0)
    set_nx = nx
    set_dx = x_spacing / set_nx
    set_ny = ny
    set_dy = y_spacing / set_ny
    set_nz = nz
    set_dz = z_spacing / set_nz
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
    ny = 80
    for i in range(50, 310, 10):
        temperature, geothermal_model = proxy_model_simulation(i, ny)
        print('\n')
        print(f'nx = {i}, ny = {80}')
        print('\n')
        print(f'dx {x_spacing / geothermal_model.reservoir.nx:.2f}, dy {y_spacing / geothermal_model.reservoir.ny:.2f},'
              f' dz {z_spacing / geothermal_model.reservoir.nz:.2f}')
        print('\n')

        if not os.path.exists('SerialResolution'):
            os.mkdir('SerialResolution')

        output_path = os.path.relpath(f'SerialResolution/temperature_resolution_dx.csv')
        if os.path.exists(output_path):
            df = pd.read_csv(output_path, delimiter=',')
            df[f'{x_spacing / geothermal_model.reservoir.nx:.2f}'] = temperature['PRD : temperature (K)']
            df.to_csv(output_path, index=False)
        else:
            temperature.rename(columns={'PRD : temperature (K)': f'{x_spacing / geothermal_model.reservoir.nx:.2f}'},
                               inplace=True)
            temperature[['time', f'{x_spacing / geothermal_model.reservoir.nx:.2f}']].to_csv(output_path, index=False)


if __name__ == '__main__':
    run_simulation()
