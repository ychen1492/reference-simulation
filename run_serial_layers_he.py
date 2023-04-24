import os

import numpy as np
import pandas as pd
from darts.engines import redirect_darts_output

from model import Model
from utils.math_rel import harmonic_average, arithmetic_average
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


def serial_layers_simulation(overburden=0):
    # read porosity from the file
    org_poro = from_las_to_poro('LogData/Well_HONSELERSDIJK_GT_01_depth_gr.las', 180)
    # calculate permeability, this is from Duncan's thesis
    org_perm = np.exp(110.744 * (org_poro ** 3) - 171.8268 * (org_poro ** 2) + 102.9227 * org_poro - 2.047)
    org_poro = arithmetic_average(org_poro, set_nz)
    org_perm = harmonic_average(org_perm, set_nz)
    poro = np.concatenate([np.ones(set_nx * set_ny) * p for p in org_poro], axis=0)
    perms = np.concatenate([np.ones(set_nx * set_ny) * p for p in org_perm], axis=0)
    redirect_darts_output(' ')
    print(f'overburden: {overburden}')
    print('\n')
    proxy_model = Model(total_time=total_time, set_nx=set_nx, set_ny=set_ny, set_nz=set_nz, set_dx=set_dx,
                        set_dy=set_dy, set_dz=set_dz, perms=perms, poro=poro, report_time_step=report_time,
                        overburden=overburden)
    proxy_model.init()
    proxy_model.run(export_to_vtk=True)
    return proxy_model


def run_simulation():
    overburden_layers = 0
    temperature_dict = {}
    pressure_dict = {}
    print('\n')
    print(f'overburden layers: {overburden_layers}')
    print('\n')
    geothermal_model = serial_layers_simulation(overburden=overburden_layers)
    pressure, temperature, _ = geothermal_model.export_data()

    if not os.path.exists('SerialLayers'):
        os.mkdir('SerialLayers')
    # the temperature distribution of the first layer
    top_layer_temp = temperature.reshape(geothermal_model.reservoir.nx, geothermal_model.reservoir.ny,
                                         geothermal_model.reservoir.nz, order='F')[:, :, 1].flatten(order='F')
    top_layer_pressure = pressure.reshape(geothermal_model.reservoir.nx, geothermal_model.reservoir.ny,
                                          geothermal_model.reservoir.nz, order='F')[:, :, 1].flatten(order='F')
    temperature_dict[overburden_layers] = top_layer_temp
    pressure_dict[overburden_layers] = top_layer_pressure

    if not os.path.exists('SerialLayers'):
        os.mkdir('SerialLayers')
    output_path = os.path.relpath(f'SerialLayers/temperature_layers_4500.csv')
    output_path_pressure = os.path.relpath(f'SerialLayers/pressure_layers_4500.csv')
    df = pd.DataFrame.from_dict(temperature_dict)
    df.to_csv(output_path, index=False)
    df_press = pd.DataFrame.from_dict(pressure_dict)
    df_press.to_csv(output_path_pressure, index=False)

    while np.abs(min(top_layer_temp) - max(top_layer_temp)) > 0.05:
        overburden_layers += 2
        print('\n')
        print(f'overburden layers: {overburden_layers}')
        print('\n')
        geothermal_model = serial_layers_simulation(overburden=overburden_layers)
        pressure, temperature, _ = geothermal_model.export_data()

        top_layer_temp = temperature.reshape(geothermal_model.reservoir.nx, geothermal_model.reservoir.ny,
                                             geothermal_model.reservoir.nz, order='F')[:, :, 1].flatten(order='F')
        top_layer_pressure = pressure.reshape(geothermal_model.reservoir.nx, geothermal_model.reservoir.ny,
                                              geothermal_model.reservoir.nz, order='F')[:, :, 1].flatten(order='F')
        temperature_dict[overburden_layers] = top_layer_temp
        pressure_dict[overburden_layers] = top_layer_pressure
        if os.path.exists(output_path):
            df = pd.read_csv(output_path, delimiter=',')
            df[overburden_layers] = top_layer_temp
            df.to_csv(output_path, index=False)

            df_press = pd.read_csv(output_path_pressure, delimiter=',')
            df_press[overburden_layers] = top_layer_pressure
            df_press.to_csv(output_path_pressure, index=False)

    print('\n')
    print(f'The minimum number of confining layers is: {overburden_layers}')


if __name__ == '__main__':
    run_simulation()