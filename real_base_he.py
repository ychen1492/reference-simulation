import os

import numpy as np
import pandas as pd
from darts.engines import redirect_darts_output

from model import Model
from utils.math_rel import arithmetic_average, harmonic_average
from utils.read_files import from_las_to_poro

report_time = 100
total_time = 10000

x_spacing = 4000
y_spacing = 3600
z_spacing = 100
set_dx = 25
set_nx = int(x_spacing / set_dx)
set_dy = 25
set_ny = int(y_spacing / set_dy)
set_dz = 10
set_nz = int(z_spacing / set_dz)
overburden = 0


def generate_base():
    """
    This is a function without any inputs to generate vtk and time data file
    :return:
    vtk and time data excel file
    """
    # read porosity from the file
    org_poro = from_las_to_poro('LogData/Well_HONSELERSDIJK_GT_01_depth_gr.las', 180)
    # calculate permeability, this is from Duncan's thesis
    f = 110.744 * (org_poro ** 3) - 171.8268 * (org_poro ** 2) + 102.9227 * org_poro - 2.047
    org_perm = [np.exp(x) for x in f]
    org_poro = arithmetic_average(org_poro, set_nz)
    org_perm = harmonic_average(org_perm, set_nz)
    poro = np.concatenate([np.ones(set_nx * set_ny) * p for p in org_poro], axis=0)
    perms = np.concatenate([np.ones(set_nx * set_ny) * p for p in org_perm], axis=0)
    redirect_darts_output('log.txt')
    proxy_model = Model(total_time=total_time, set_nx=set_nx, set_ny=set_ny, set_nz=set_nz, set_dx=set_dx,
                        set_dy=set_dy, set_dz=set_dz, perms=perms, poro=poro, report_time_step=report_time,
                        overburden=overburden)
    proxy_model.init()
    proxy_model.run(export_to_vtk=True)

    proxy_model_elapsed_time = proxy_model.timer.node['initialization'].get_timer() + proxy_model.timer.node[
        'simulation'].get_timer()

    td = pd.DataFrame.from_dict(proxy_model.physics.engine.time_data)

    if not os.path.exists('RealBase'):
        os.mkdir('RealBase')
    output_path = os.path.relpath(f'./RealBase/base_resolution_he.xlsx')
    writer = pd.ExcelWriter(output_path)
    td.to_excel(writer, 'Sheet1')
    writer.save()
    with open('./RealBase/simulation_time_resolution_he.txt', 'w') as f:
        f.write(f'{proxy_model_elapsed_time}')

def check_the_number_of_overburden(overburden=0):
    # read porosity from the file
    org_poro = from_las_to_poro('LogData/Well_HONSELERSDIJK_GT_01_depth_gr.las', 180)
    # calculate permeability, this is from Duncan's thesis
    org_perm = np.exp(110.744 * (org_poro ** 3) - 171.8268 * (org_poro ** 2) + 102.9227 * org_poro - 2.047)
    org_poro = arithmetic_average(org_poro, set_nz)
    org_perm = harmonic_average(org_perm, set_nz)
    poro = np.concatenate([np.ones(set_nx * set_ny) * p for p in org_poro], axis=0)
    perms = np.concatenate([np.ones(set_nx * set_ny) * p for p in org_perm], axis=0)

    print(f'overburden: {overburden}')
    print('\n')
    proxy_model = Model(total_time=total_time, set_nx=set_nx, set_ny=set_ny, set_nz=set_nz, set_dx=set_dx,
                        set_dy=set_dy, set_dz=set_dz, perms=perms, poro=poro, report_time_step=report_time,
                        overburden=overburden)
    proxy_model.init()
    proxy_model.run(export_to_vtk=True)
    return proxy_model


if __name__ == '__main__':
    overburden_layers = [1]
    temperature_dict = {}
    for o in overburden_layers:
        geothermal_model = check_the_number_of_overburden(o)
        pressure, temperature, _ = geothermal_model.export_data()
        # the temperature distribution of the first layer
        top_layer_temp = temperature.reshape(geothermal_model.reservoir.nx, geothermal_model.reservoir.ny,
                                             geothermal_model.reservoir.nz, order='F')[:, :, 1].flatten(order='F')
        temperature_dict[o] = top_layer_temp
        if not os.path.exists('BaseLayers'):
            os.mkdir('BaseLayers')
        output_path = os.path.relpath(f'BaseLayers/temperature_layers.csv')
        if os.path.exists(output_path):
            df = pd.read_csv(output_path, delimiter=',')
            df[o] = top_layer_temp
            df.to_csv(output_path, index=False)
        else:
            df = pd.DataFrame.from_dict(temperature_dict)
            df.to_csv(output_path, index=False)
