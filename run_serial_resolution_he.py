import os

from darts.engines import redirect_darts_output
from model import Model
import pandas as pd

from utils.read_files import read_pickle_file

report_time = 100
total_time = 10000
nz = 10


def proxy_model_simulation(nx, ny, nz=10):
    poro, perm = read_pickle_file(ny, nx, "Porosity")
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
    proxy_model.run(export_to_vtk=True)

    td = pd.DataFrame.from_dict(proxy_model.physics.engine.time_data)

    return td, proxy_model


def run_simulation():
    # fixed ny = 80
    ny = 100
    # list_nx = [40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300]
    list_nx = [40,60,80]
    # list_nx = [160, 180, 200, 220, 240, 260, 280, 300]
    # list_nz = [16, 18, 20]
    # list_nz = [1,3,5,7,9,11,13,15]
    # list_nz = [10]
    for i in list_nx:
        print('\n')
        print(f'nx = {i}')
        print('\n')
        print(f'dx {x_spacing / i:.2f}, dy {y_spacing / ny:.2f},'
              f' dz {z_spacing / nz:.2f}')
        print('\n')

        temperature, geothermal_model = proxy_model_simulation(i, ny)

        if not os.path.exists('SerialResolution'):
            os.mkdir('SerialResolution')

        output_path = os.path.relpath(f'SerialResolution/temperature_resolution_dz_tt.csv')
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
