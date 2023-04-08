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
    proxy_model = Model(total_time=total_time, set_nx=set_nx, set_ny=set_ny, set_nz=set_nz, set_dx=set_dx,
                        set_dy=set_dy, set_dz=set_dz, perms=perms, poro=poro, report_time_step=report_time,
                        overburden=base_overburden)
    proxy_model.init()
    proxy_model.run(export_to_vtk=True)

    proxy_model_elapsed_time = proxy_model.timer.node['initialization'].get_timer() + proxy_model.timer.node[
        'simulation'].get_timer()

    td = pd.DataFrame.from_dict(proxy_model.physics.engine.time_data)

    if not os.path.exists('RealBase'):
        os.mkdir('RealBase')
    output_path = os.path.relpath(f'./RealBase/base_resolution_ho.xlsx')
    writer = pd.ExcelWriter(output_path)
    td.to_excel(writer, 'Sheet1')
    writer.save()
    with open('./RealBase/simulation_time_resolution_ho.txt', 'w') as f:
        f.write(f'{proxy_model_elapsed_time}')


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
    proxy_model = Model(total_time=total_time, set_nx=set_nx, set_ny=set_ny, set_nz=set_nz, set_dx=set_dx,
                        set_dy=set_dy, set_dz=set_dz_new, perms=perms, poro=poro, report_time_step=report_time,
                        overburden=overburden)
    proxy_model.init()
    proxy_model.run(export_to_vtk=True)

    proxy_model_elapsed_time = proxy_model.timer.node['initialization'].get_timer() + proxy_model.timer.node[
        'simulation'].get_timer()

    td = pd.DataFrame.from_dict(proxy_model.physics.engine.time_data)

    if not os.path.exists('UpdateDz'):
        os.mkdir('UpdateDz')
    output_path = os.path.relpath(f'./UpdateDz/scenario_50.xlsx')
    writer = pd.ExcelWriter(output_path)
    td.to_excel(writer, 'Sheet1')
    writer.save()
    with open('./UpdateDz/scenario_50.txt', 'w') as f:
        f.write(f'{proxy_model_elapsed_time}')

    return proxy_model


if __name__ == '__main__':
    # proxy_model = upscale_overburden(220)
    generate_base()
