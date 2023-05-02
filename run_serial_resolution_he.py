import os

from darts.engines import redirect_darts_output
from model import Model
import pandas as pd

from utils.read_files import read_pickle_file_upscaling_z, get_porosity_values

report_time = 100
total_time = 10000
nz = 10


def proxy_model_simulation(nx, ny, nz=10):
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


def run_simulation():
    nx = 225
    ny = 70
    # list_nx = [40]
    # list_nx = [160, 180, 200, 220, 240, 260, 280, 300]
    # list_nz = [16, 18, 20]
    # list_nz = [20]
    list_nz = [1, 3, 5, 7, 9, 11, 13, 15, 17]
    # list_nz = [1]
    # list_nz = [10]

    for i in list_nz:
        print('\n')
        print(f'nz = {i}')
        print('\n')
        print(f'dx {x_spacing / nx:.2f}, dy {y_spacing / ny:.2f}, '
              f'dz {z_spacing / i:.2f}')
        print('\n')
        temperature, geothermal_model = proxy_model_simulation(nx, ny, i)

        if not os.path.exists('SerialResolutionHe'):
            os.mkdir('SerialResolutionHe')

        output_path = os.path.relpath(f'SerialResolutionHe/temperature_resolution_dz.csv')
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
