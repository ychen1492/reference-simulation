import os

import numpy as np
import pandas as pd
from darts.engines import redirect_darts_output

from model import Model

report_time = 100
total_time = 10000
perm = 3000
poro = 0.2

x_spacing = 3000
y_spacing = 2500
z_spacing = 100
set_dx = 18.5
set_nx = int(x_spacing / set_dx)
set_dy = 27.5
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
    redirect_darts_output('log.txt')
    poros = np.ones(set_nx * set_ny*set_nz) * poro
    perms = np.ones(set_nx * set_ny*set_nz) * perm
    proxy_model = Model(total_time=total_time, set_nx=set_nx, set_ny=set_ny, set_nz=set_nz, set_dx=set_dx,
                        set_dy=set_dy, set_dz=set_dz, perms=perms, poro=poros, report_time_step=report_time,
                        overburden=overburden, rate=7500, is_mass_rate=True)
    proxy_model.init()
    proxy_model.run(export_to_vtk=True)

    td = pd.DataFrame.from_dict(proxy_model.physics.engine.time_data)

    if not os.path.exists('RealBase'):
        os.mkdir('RealBase')
    output_path = os.path.relpath(f'./RealBase/base_resolution_ho_mass_constraint.xlsx')
    writer = pd.ExcelWriter(output_path)
    td.to_excel(writer, 'Sheet1')
    writer.save()


if __name__ == '__main__':
    generate_base()
