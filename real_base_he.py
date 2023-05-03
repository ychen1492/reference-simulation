import os

import numpy as np
import pandas as pd
from darts.engines import redirect_darts_output

from model import Model
from utils.math_rel import arithmetic_average, harmonic_average
from utils.read_files import from_las_to_poro_gamma, read_pickle_file

report_time = 100
total_time = 10000

x_spacing = 4500
y_spacing = 4000
z_spacing = 100
set_dx = 20
set_nx = int(x_spacing / set_dx)
set_dy = 70
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
    generate_base()
