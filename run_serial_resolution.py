import os

import numpy as np
from darts.engines import redirect_darts_output

from model import Model
import pandas as pd

report_time = 100
total_time = 10000
training_model = True
perms = 3000
poro = 0.2

# mean and standard deviation of perm lognormal distribution
mu, sigma = 5, 1.

# fix seed and sample from lognormal distribution;
# for project I will be using seed = 550
np.random.seed(550)
permdist = np.random.lognormal(mu, sigma, 90000)
x_spacing = 3000
y_spacing = 2800
z_spacing = 100


def proxy_model_simulation(nz=20):

    set_dx = 18.5
    set_nx = int(x_spacing / set_dx)
    set_dy = 27.5
    set_ny = int(y_spacing / set_dy)
    set_dz = 9.7
    set_nz = int(z_spacing / set_dz)
    redirect_darts_output('log.txt')
    proxy_model = Model(total_time=total_time, set_nx=set_nx, set_ny=set_ny, set_nz=set_nz, set_dx=set_dx,
                        set_dy=set_dy, set_dz=set_dz, perms=perms, poro=poro, report_time_step=report_time)
    proxy_model.init()
    proxy_model.run(export_to_vtk=False)

    td = pd.DataFrame.from_dict(proxy_model.physics.engine.time_data)

    return td, proxy_model


def run_simulation():
    # check the dz effect, keep dy, dz constant
    for i in range(9, 50, 2):
        temperature, geothermal_model = proxy_model_simulation(i)
        print('\n')
        print(f'nz = {i}')
        print('\n')
        print(f'dx {x_spacing / geothermal_model.reservoir.nx:.2f}, dy {y_spacing / geothermal_model.reservoir.ny:.2f},'
              f' dz {z_spacing / geothermal_model.reservoir.nz:.2f}')
        print('\n')

        if not os.path.exists('SerialResolution'):
            os.mkdir('SerialResolution')

        output_path = os.path.relpath(f'SerialResolution/temperature_resolution_dz.csv')
        if os.path.exists(output_path):
            df = pd.read_csv(output_path, delimiter=',')
            df[f'{z_spacing / geothermal_model.reservoir.nz:.2f}'] = temperature['PRD : temperature (K)']
            df.to_csv(output_path, index=False)
        else:
            temperature.rename(columns={'PRD : temperature (K)': f'{z_spacing / geothermal_model.reservoir.nz:.2f}'},
                               inplace=True)
            temperature[['time', f'{z_spacing / geothermal_model.reservoir.nz:.2f}']].to_csv(output_path, index=False)


if __name__ == '__main__':
    run_simulation()
