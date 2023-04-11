import os
import pickle

import numpy as np
from darts.engines import redirect_darts_output
from matplotlib import pyplot as plt

from model import Model
import pandas as pd

report_time = 100
total_time = 365*20

def proxy_model_simulation(nx, ny):
    # fix nz to be 10
    nz = 10
    poro = np.concatenate([np.ones(nx*ny) * p for p in org_poro[9]], axis=0)
    # calculate permeability
    org_perm = 0.0663 * np.exp(29.507 * poro) * 10000
    perms = org_perm
    set_nx = nx
    set_dx = x_spacing / set_nx
    set_ny = ny
    set_dy = y_spacing / set_ny
    set_nz = nz
    set_dz = z_spacing / set_nz
    redirect_darts_output(' ')
    proxy_model = Model(total_time=total_time, set_nx=set_nx, set_nz=set_nz, set_dx=set_dx,
                        set_dz=set_dz, perms=perms, poro=poro, report_time_step=report_time,
                        overburden=0)
    proxy_model.init()
    proxy_model.run(export_to_vtk=False)

    td = pd.DataFrame.from_dict(proxy_model.physics.engine.time_data)

    return td, proxy_model


def run_simulation():
    # fixed ny = 80
    ny = 1
    list_nx = [40, 60, 120, 200]
    for i in list_nx[::-1]:
        fig, ax = plt.subplots(2, 2, figsize=(10, 10))
        axx = fig.axes
        temperature, geothermal_model = proxy_model_simulation(i, ny)
        press, temp, perm = geothermal_model.export_data()
        td = pd.DataFrame.from_dict(geothermal_model.physics.engine.time_data)
        td['Time (yrs)'] = td['time'] / 365
        string = 'PRD : temperature (K)'
        axx[0].plot(td['time'], td[string], linewidth=2, color='b')

        permplot = axx[1].imshow(np.rot90(perm.reshape(i, 10, order='F')), cmap='viridis', aspect='auto')
        fig.colorbar(permplot, ax=axx[1], location='bottom', label='Permeability (mD)')  # ,

        pressplot = axx[2].imshow(np.rot90(press.reshape(i, 10, order='F')), cmap='inferno', aspect='auto')
        fig.colorbar(pressplot, ax=axx[2], location='bottom', label='Pressure (bar)')

        tempplot = axx[3].imshow(np.rot90(temp.reshape(i, 10, order='F')), cmap='coolwarm', aspect='auto')
        fig.colorbar(tempplot, ax=axx[3], location='bottom', label='Temperature (K)')
        plt.show()

        if not os.path.exists('SerialResolution'):
            os.mkdir('SerialResolution')

        output_path = os.path.relpath(f'SerialResolution/temperature_resolution_dx_1.csv')
        if os.path.exists(output_path):
            df = pd.read_csv(output_path, delimiter=',')
            df[f'{x_spacing / geothermal_model.reservoir.nx:.2f}'] = temperature['PRD : temperature (K)']
            df.to_csv(output_path, index=False)
        else:
            temperature.rename(columns={'PRD : temperature (K)': f'{x_spacing / geothermal_model.reservoir.nx:.2f}'},
                               inplace=True)
            temperature[['time', f'{x_spacing / geothermal_model.reservoir.nx:.2f}']].to_csv(output_path, index=False)


if __name__ == '__main__':
    x_spacing = 4800
    y_spacing = 3600
    z_spacing = 100
    # read porosity from the file
    with open('LogData/porosity_californie_sidetrack_dz.pkl', 'rb') as f:
        org_poro = pickle.load(f)
    run_simulation()
