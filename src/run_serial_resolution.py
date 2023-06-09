import os

import numpy as np
from darts.engines import redirect_darts_output
from .model import Model
import pandas as pd

from src.read_files import read_pickle_file_upscaling_z, from_las_to_poro_gamma

report_time = 100
total_time = 10000
perm = 3000
poro = 0.2
set_nz = 10


def proxy_model_simulation_layered(nx, ny, nz):
    set_nx = nx
    set_dx = x_spacing / set_nx
    set_nz = nz
    set_dz = z_spacing / set_nz
    set_ny = ny
    set_dy = y_spacing / set_ny
    # read porosity from the file
    org_poro = from_las_to_poro_gamma('LogData/Well_PIJNACKER_GT_01_depth_gamma_4.las', nz)
    poro = np.concatenate([np.ones(nx * ny) * p for p in org_poro], axis=0)
    # calculate permeability, this is from Duncan's thesis
    org_perm = np.exp(110.744 * poro ** 3 - 171.8268 * poro ** 2 + 92.9227 * poro - 2.047)
    perms = org_perm
    redirect_darts_output('log.txt')
    proxy_model = Model(total_time=total_time, set_nx=set_nx, set_ny=set_ny, set_nz=set_nz, set_dx=set_dx,
                        set_dy=set_dy, set_dz=set_dz, perms=perms, poro=poro, report_time_step=report_time,
                        overburden=0)
    proxy_model.init()
    proxy_model.run(export_to_vtk=False)

    td = pd.DataFrame.from_dict(proxy_model.physics.engine.time_data)

    return td, proxy_model


def proxy_model_simulation_he(nx, ny, nz=10):
    poro, perm = read_pickle_file_upscaling_z(ny, nx, nz, "Porosity20")
    set_nx = nx
    set_dx = x_spacing / set_nx
    set_nz = nz
    set_dz = z_spacing / set_nz
    set_ny = ny
    set_dy = y_spacing / set_ny
    redirect_darts_output('log.txt')
    proxy_model = Model(total_time=total_time, set_nx=set_nx, set_ny=set_ny, set_nz=set_nz, set_dx=set_dx,
                        set_dy=set_dy, set_dz=set_dz, perms=perm, poro=poro, report_time_step=report_time,
                        overburden=0)
    proxy_model.init()
    proxy_model.run(export_to_vtk=False)

    td = pd.DataFrame.from_dict(proxy_model.physics.engine.time_data)

    return td, proxy_model


def proxy_model_simulation(nx, ny, nz=set_nz):
    """For the given nx, ny and nz constructs a homogeneous reservoir model and
    run the forward simulation

    :param nx: the number of cells in x direction
    :param ny: the number of cells in y direction
    :param nz: the number of cells in z directions
    :return: time data and the geothermal model which is inherited from the DartsModel
    """
    set_dx = x_spacing / nx
    set_nx = nx
    set_dy = y_spacing / ny
    set_ny = ny
    set_dz = z_spacing / nz
    set_nz = nz
    redirect_darts_output('log.txt')
    perms = np.ones(nx * ny * nz) * perm
    poros = np.ones(nx * ny * nz) * poro
    proxy_model = Model(total_time=total_time, set_nx=set_nx, set_ny=set_ny, set_nz=set_nz, set_dx=set_dx,
                        set_dy=set_dy, set_dz=set_dz, perms=perms, poro=poros, report_time_step=report_time,
                        overburden=0)
    proxy_model.init()
    proxy_model.run(export_to_vtk=False)

    td = pd.DataFrame.from_dict(proxy_model.physics.engine.time_data)

    return td, proxy_model


def run_simulation():
    """Give the input of different nx, ny and nz to proxy_model_simulation

    :return:
    """
    nx = 225
    ny = 75
    # list_nx = [40]
    # list_nx = [160, 180, 200, 220, 240, 260, 280, 300]
    # list_nz = [16, 18, 20]
    list_nz = [1, 3, 5, 7, 9, 11, 13, 15]
    # list_nz = [10]
    for i in list_nz:
        print('\n')
        print(f'nz = {i}')
        print('\n')
        print(f'dx {x_spacing / nx:.2f}, dy {y_spacing / ny:.2f},'
              f'dz {z_spacing / i:.2f}')
        print('\n')
        temperature, geothermal_model = proxy_model_simulation(nx, ny, i)

        if not os.path.exists('SerialResolutionHo'):
            os.mkdir('SerialResolutionHo')

        output_path = os.path.relpath(f'SerialResolutionHo/temperature_resolution_dz.csv')
        if os.path.exists(output_path):
            df = pd.read_csv(output_path, delimiter=',')
            df[f'{z_spacing / geothermal_model.reservoir.nz:.2f}'] = temperature['PRD : temperature (K)']
            df.to_csv(output_path, index=False)
        else:
            temperature.rename(columns={'PRD : temperature (K)': f'{z_spacing / geothermal_model.reservoir.nz:.2f}'},
                               inplace=True)
            temperature[['time', f'{z_spacing / geothermal_model.reservoir.nz:.2f}']].to_csv(output_path, index=False)


if __name__ == '__main__':
    x_spacing = 4500
    y_spacing = 4000
    z_spacing = 100
    run_simulation()
