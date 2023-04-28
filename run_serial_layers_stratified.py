import os

import numpy as np
from darts.engines import redirect_darts_output

from model import Model
import pandas as pd

from utils.math_rel import arithmetic_average, harmonic_average
from utils.read_files import from_las_to_poro_gamma

report_time = 100
total_time = 10000

x_spacing = 4500
y_spacing = 4000
z_spacing = 100


def proxy_model_simulation(overburden):
    """
        Main method to run multiple forward simulations for given different overburden layers
    :param overburden: the number of the overburden layers
    :return:
    """
    set_dx = 20
    set_nx = int(x_spacing / set_dx)
    set_dy = 75
    set_ny = int(y_spacing / set_dy)
    set_dz = 10
    set_nz = int(z_spacing / set_dz)
    redirect_darts_output(' ')
    # read porosity from the file
    org_poro = from_las_to_poro_gamma('LogData/Well_PIJNACKER_GT_01_depth_gamma_4.las', set_nz)
    # calculate permeability, this is from Duncan's thesis
    org_perm = np.exp(110.744 * (org_poro ** 3) - 171.8268 * (org_poro ** 2) + 102.9227 * org_poro - 2.047)
    org_poro = arithmetic_average(org_poro, set_nz)
    org_perm = harmonic_average(org_perm, set_nz)
    poros = np.concatenate([np.ones(set_nx * set_ny) * p for p in org_poro], axis=0)
    perms = np.concatenate([np.ones(set_nx * set_ny) * p for p in org_perm], axis=0)
    proxy_model = Model(total_time=total_time, set_nx=set_nx, set_ny=set_ny, set_nz=set_nz, set_dx=set_dx,
                        set_dy=set_dy, set_dz=set_dz, perms=perms, poro=poros, report_time_step=report_time,
                        overburden=overburden)
    proxy_model.init()
    proxy_model.run(export_to_vtk=False)

    pressure, temperature, _ = proxy_model.export_data()

    return pressure, temperature, proxy_model


def run_simulation():
    """
        Run simulation and increase the number of confining layers
    :return: csv files which contain the pressure and temperature of the top reservoir layer
    """
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

    if not os.path.exists('SerialLayersStratified'):
        os.mkdir('SerialLayersStratified')
    output_path = os.path.relpath(f'SerialLayersStratified/temperature_layers.csv')
    output_path_pressure = os.path.relpath(f'SerialLayersStratified/pressure_layers.csv')
    df = pd.DataFrame.from_dict(temperature_dict)
    # Write the temperature of the top reservoir layer to a csv
    df.to_csv(output_path, index=False)
    df_press = pd.DataFrame.from_dict(pressure_dict)
    # Write the pressure of the top reservoir layer to a csv
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