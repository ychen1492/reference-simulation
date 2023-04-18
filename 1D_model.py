import os

import numpy as np
import pandas as pd
from darts.engines import redirect_darts_output

from model import Model

report_time = 100
total_time = 5*365
perm = 2000
poro = 0.2

np.random.seed(550)
x_spacing = 300
y_spacing = 100
z_spacing = 100
set_dx = 2
set_nx = int(x_spacing / set_dx)
set_dy = 8
set_ny = 1
set_dz = 5
set_nz = 1
overburden = 0


def generate_base():
    """
    This is a function without any inputs to generate vtk and time data file
    :return:
    vtk and time data excel file
    """
    redirect_darts_output('log.txt')
    poros = np.ones(set_nx*set_ny*set_nz)*poro
    perms = np.ones(set_nx*set_ny*set_nz)*perm
    proxy_model = Model(total_time=total_time, set_nx=set_nx, set_ny=set_ny, set_nz=set_nz, set_dx=set_dx,
                        set_dy=set_dy, set_dz=set_dz, perms=perms, poro=poros, report_time_step=report_time,
                        overburden=overburden, rate=1, well_spacing=100)
    proxy_model.init()
    proxy_model.run(export_to_vtk=False)

    proxy_model_elapsed_time = proxy_model.timer.node['initialization'].get_timer() + proxy_model.timer.node[
        'simulation'].get_timer()

    td = pd.DataFrame.from_dict(proxy_model.physics.engine.time_data)

    if not os.path.exists('SmallModel'):
        os.mkdir('SmallModel')
    output_path = os.path.relpath(f'./SmallModel/1d_model.xlsx')
    writer = pd.ExcelWriter(output_path)
    td.to_excel(writer, 'Sheet1')
    writer.save()
    with open('./SmallModel/1d_model.txt', 'w') as f:
        f.write(f'{proxy_model_elapsed_time}')


if __name__ == '__main__':
    generate_base()