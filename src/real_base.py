import os

import numpy as np
import pandas as pd
from darts.engines import redirect_darts_output

from model import Model
from utils.read_files import read_pickle_file, from_las_to_poro_gamma

report_time = 100
total_time = 10000
perm = 3000
poro = 0.2

x_spacing = 4500
y_spacing = 4000
z_spacing = 100
set_dx = 20
set_nx = int(x_spacing / set_dx)
set_dy = 75
set_ny = int(y_spacing / set_dy)
set_dz = 10
set_nz = int(z_spacing / set_dz)
overburden = 0


def generate_base_ho():
    """
    This is a function without any inputs to generate vtk and time data file for homogeneous case

    :return:
        vtk and time data excel file
    """
    redirect_darts_output('log.txt')
    perms = np.ones(set_nx * set_ny * set_nz) * perm
    poros = np.ones(set_nx * set_ny * set_nz) * poro
    proxy_model = Model(total_time=total_time, set_nx=set_nx, set_ny=set_ny, set_nz=set_nz, set_dx=set_dx,
                        set_dy=set_dy, set_dz=set_dz, perms=perms, poro=poros, report_time_step=report_time,
                        overburden=overburden)
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


def generate_base_stratified():
    """This is a function without any inputs to generate vtk and time data file for stratified case

    :return:
        vtk and time data excel file
    """
    # read porosity from the file
    org_poro = from_las_to_poro_gamma('LogData/Well_PIJNACKER_GT_01_depth_gamma_4.las', set_nz)
    poro = np.concatenate([np.ones(set_nx * set_ny) * p for p in org_poro], axis=0)
    # calculate permeability, this is from Duncan's thesis
    org_perm = np.exp(110.744 * poro ** 3 - 171.8268 * poro ** 2 + 92.9227 * poro - 2.047)
    perms = org_perm
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
    output_path = os.path.relpath(f'./RealBase/base_resolution_layered.xlsx')
    writer = pd.ExcelWriter(output_path)
    td.to_excel(writer, 'Sheet1')
    writer.save()
    with open('./RealBase/simulation_time_resolution_layered.txt', 'w') as f:
        f.write(f'{proxy_model_elapsed_time}')


def generate_base_he():
    """This is a function without any inputs to generate vtk and time data file for heterogeneous case

    :return:
        vtk and time data excel file
    """
    poros, perms = read_pickle_file(set_ny, set_nx, "Porosity")
    redirect_darts_output('log.txt')
    proxy_model = Model(total_time=total_time, set_nx=set_nx, set_ny=set_ny, set_nz=set_nz, set_dx=set_dx,
                        set_dy=set_dy, set_dz=set_dz, perms=perms, poro=poros, report_time_step=report_time,
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


if __name__ == '__main__':
    generate_base_ho()
