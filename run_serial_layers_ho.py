import os

import numpy as np
from darts.engines import redirect_darts_output

from model import Model
import pandas as pd

report_time = 100
total_time = 10000
perm = 3000
poro = 0.2

x_spacing = 4500
y_spacing = 4000
z_spacing = 100


def proxy_model_simulation(overburden):
    set_dx = 20
    set_nx = int(x_spacing / set_dx)
    set_dy = 75
    set_ny = int(y_spacing / set_dy)
    set_dz = 10
    set_nz = int(z_spacing / set_dz)
    redirect_darts_output(' ')
    perms = np.ones(set_nx * set_ny * set_nz) * perm
    poros = np.ones(set_nx * set_ny * set_nz) * poro
    proxy_model = Model(total_time=total_time, set_nx=set_nx, set_ny=set_ny, set_nz=set_nz, set_dx=set_dx,
                        set_dy=set_dy, set_dz=set_dz, perms=perms, poro=poros, report_time_step=report_time,
                        overburden=overburden)
    proxy_model.init()
    proxy_model.run(export_to_vtk=False)

    pressure, temperature, _ = proxy_model.export_data()

    return pressure, temperature, proxy_model


def run_simulation():
    overburden_layers = 0
    temperature_dict = {}
    pressure_dict = {}
    print('\n')
    print(f'overburden layers: {overburden_layers}')
    print('\n')
    pressure, temperature, geothermal_model = proxy_model_simulation(overburden=overburden_layers)

    if not os.path.exists('SerialLayersHo'):
        os.mkdir('SerialLayersHo')
    # the temperature distribution of the first layer
    top_layer_temp = temperature.reshape(geothermal_model.reservoir.nx, geothermal_model.reservoir.ny,
                                         geothermal_model.reservoir.nz, order='F')[:, :, 1].flatten(order='F')
    top_layer_pressure = pressure.reshape(geothermal_model.reservoir.nx, geothermal_model.reservoir.ny,
                                         geothermal_model.reservoir.nz, order='F')[:, :, 1].flatten(order='F')
    temperature_dict[overburden_layers] = top_layer_temp
    pressure_dict[overburden_layers] = top_layer_pressure

    if not os.path.exists('SerialLayersHo'):
        os.mkdir('SerialLayersHo')
    output_path = os.path.relpath(f'SerialLayersHo/temperature_layers.csv')
    output_path_pressure = os.path.relpath(f'SerialLayersHo/pressure_layers.csv')
    df = pd.DataFrame.from_dict(temperature_dict)
    df.to_csv(output_path, index=False)
    df_press = pd.DataFrame.from_dict(pressure_dict)
    df_press.to_csv(output_path_pressure, index=False)

    while np.abs(min(top_layer_temp) - max(top_layer_temp)) > 0.05:
        overburden_layers += 2
        print('\n')
        print(f'overburden layers: {overburden_layers}')
        print('\n')
        pressure, temperature, geothermal_model = proxy_model_simulation(overburden=overburden_layers)
    
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
