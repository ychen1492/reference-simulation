import os
import numpy as np
from darts.engines import redirect_darts_output
from model import Model
import pandas as pd

from utils.math_rel import harmonic_average, arithmetic_average
from utils.read_files import from_las_to_poro

report_time = 100
total_time = 10000
nz = 10


def proxy_model_simulation(nx, ny, nz=10):
    # read porosity from the file
    org_poro = from_las_to_poro('LogData/Well_HONSELERSDIJK_GT_01_depth_gr.las', 180)
    # calculate permeability, this is from Duncan's thesis
    f = 110.744 * (org_poro ** 3) - 171.8268 * (org_poro ** 2) + 102.9227 * org_poro - 2.047
    org_perm = [np.exp(x) for x in f]
    if nz < 20:
        org_poro = arithmetic_average(org_poro, nz)
        org_perm = harmonic_average(org_perm, nz)
    set_nx = nx
    set_dx = x_spacing / set_nx
    set_nz = nz
    set_dz = z_spacing / set_nz
    set_ny = ny
    set_dy = y_spacing / set_ny
    redirect_darts_output('log.txt')
    poro = np.concatenate([np.ones(nx * ny) * p for p in org_poro], axis=0)
    perms = np.concatenate([np.ones(nx * ny) * p for p in org_perm], axis=0)
    proxy_model = Model(total_time=total_time, set_nx=set_nx, set_ny=set_ny, set_nz=set_nz, set_dx=set_dx,
                        set_dy=set_dy, set_dz=set_dz, perms=perms, poro=poro, report_time_step=report_time,
                        overburden=0)
    proxy_model.init()
    proxy_model.run(export_to_vtk=False)

    td = pd.DataFrame.from_dict(proxy_model.physics.engine.time_data)

    return td, proxy_model


def run_simulation():
    # fixed ny = 80
    nx = 222
    ny = 90
    # list_ny = [40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300]
    # list_nx = [160, 180, 200, 220, 240, 260, 280, 300]
    # list_nz = [16, 18, 20]
    list_nz = [1,3,5,7,9,11,13,15]
    # list_nz = [3]
    for i in list_nz:
        temperature, geothermal_model = proxy_model_simulation(nx, ny, i)

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
    x_spacing = 4000
    y_spacing = 3600
    z_spacing = 100

    run_simulation()
