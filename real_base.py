import os

import numpy as np
import pandas as pd
from darts.engines import redirect_darts_output

from model import Model

report_time = 100
total_time = 10000
perms = 3000
poro = 0.2

np.random.seed(550)
x_spacing = 3000
y_spacing = 2500
z_spacing = 100
set_dx = 18.5
set_nx = int(x_spacing / set_dx)
set_dy = 27.5
set_ny = int(y_spacing / set_dy)
set_dz = 10
set_nz = int(z_spacing / set_dz)
base_overburden = 22


def generate_base():
    """
    This is a function without any inputs to generate vtk and time data file
    :return:
    vtk and time data excel file
    """
    redirect_darts_output('log.txt')
    geothermal_model = Model(total_time=total_time, set_nx=set_nx, set_ny=set_ny, set_nz=set_nz, set_dx=set_dx,
                        set_dy=set_dy, set_dz=set_dz, perms=perms, poro=poro, report_time_step=report_time,
                        overburden=base_overburden)
    geothermal_model.init()
    geothermal_model.run(export_to_vtk=True)

    pressure, temperature = geothermal_model.export_data()
    temperature_dict = {}
    pressure_dict = {}
    if not os.path.exists('RealBase'):
        os.mkdir('RealBase')
    # the temperature distribution of the first 22 layers
    top_layer_temp = temperature.reshape(geothermal_model.reservoir.nx, geothermal_model.reservoir.ny,
                                         geothermal_model.reservoir.nz, order='F')[:, :, 0:22].flatten(order='F')
    top_layer_pressure = pressure.reshape(geothermal_model.reservoir.nx, geothermal_model.reservoir.ny,
                                          geothermal_model.reservoir.nz, order='F')[:, :, 0:22].flatten(order='F')
    temperature_dict['base'] = top_layer_temp
    pressure_dict['base'] = top_layer_pressure

    output_path = os.path.relpath(f'RealBase/temperature_layers.csv')
    output_path_pressure = os.path.relpath(f'RealBase/pressure_layers.csv')
    df = pd.DataFrame.from_dict(temperature_dict)
    df.to_csv(output_path, index=False)
    df_press = pd.DataFrame.from_dict(pressure_dict)
    df_press.to_csv(output_path_pressure, index=False)


def upscale_overburden(overburden_thickness):
    """
    This function is to upscale the overburden layer by giving different dz
    :param overburden_thickness: the thickness of overburden from the base
    :return:
    """
    # the number of overburden layers groups in upscaled case
    number_layers_group = 4
    # the layers in on group
    layers_in_group = 2
    # for different z layers, give different dz
    # the size of dz list is nx*ny*overburden_nz
    overburden = number_layers_group * layers_in_group
    overburden_dz = np.zeros(set_nx * set_ny * overburden)
    dz_list = [50, 30, 20, 10]

    if sum([2 * x for x in dz_list]) != overburden_thickness:
        raise Exception("The overburden domain is not conservative...")
    for k in range(overburden):
        start = k * set_nx * set_ny
        end = (k + 1) * set_nx * set_ny
        if k < 2:
            overburden_dz[start:end] = dz_list[0]
        elif 2 <= k < 4:
            overburden_dz[start:end] = dz_list[1]
        elif 4 <= k < 6:
            overburden_dz[start:end] = dz_list[2]
        else:
            overburden_dz[start:end] = dz_list[3]

    redirect_darts_output('log.txt')
    # add the overburden layers' dz
    set_dz_new = np.concatenate([overburden_dz, np.ones(set_nx * set_ny * set_nz) * set_dz])
    geothermal_model = Model(total_time=total_time, set_nx=set_nx, set_ny=set_ny, set_nz=set_nz, set_dx=set_dx,
                        set_dy=set_dy, set_dz=set_dz_new, perms=perms, poro=poro, report_time_step=report_time,
                        overburden=overburden)
    geothermal_model.init()
    geothermal_model.run(export_to_vtk=True)
    pressure, temperature = geothermal_model.export_data()
    temperature_dict = {}
    pressure_dict = {}
    if not os.path.exists('UpdateDz'):
        os.mkdir('UpdateDz')
    # the temperature distribution of the first 8 layers
    top_layer_temp = temperature.reshape(geothermal_model.reservoir.nx, geothermal_model.reservoir.ny,
                                         geothermal_model.reservoir.nz, order='F')[:, :, 0:8].flatten(order='F')
    top_layer_pressure = pressure.reshape(geothermal_model.reservoir.nx, geothermal_model.reservoir.ny,
                                          geothermal_model.reservoir.nz, order='F')[:, :, 0:8].flatten(order='F')
    temperature_dict['upscaled'] = top_layer_temp
    pressure_dict['upscaled'] = top_layer_pressure
    output_path = os.path.relpath(f'UpdateDz/temperature_upscaled_layers.csv')
    output_path_pressure = os.path.relpath(f'UpdateDz/pressure_upscaled_layers.csv')
    df = pd.DataFrame.from_dict(temperature_dict)
    df.to_csv(output_path, index=False)
    df_press = pd.DataFrame.from_dict(pressure_dict)
    df_press.to_csv(output_path_pressure, index=False)


if __name__ == '__main__':
    upscale_overburden(220)
    # generate_base()
