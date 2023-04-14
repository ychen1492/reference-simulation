import math
import numpy as np
import pandas as pd


def from_las_to_poro(path_to_las, number_layers):
    """
        For the given las path and number of layers, output the porosity
    :param path_to_las: the path to las file which contains density log
    :param number_layers: number of reservoir layers
    :return:
    """
    well_californie_sidetrack1_01 = pd.read_table(path_to_las, delim_whitespace=True)
    well_californie_sidetrack1_01 = well_californie_sidetrack1_01.replace(-999.0000, np.NaN)

    density_log = well_californie_sidetrack1_01['DT']
    # micro second/foot to second/m
    conversion = 1e-6 / 0.3048
    # sandstone velocity and water velocity
    v_sandstone = 5490  # m/s
    v_water = 1490  # m/s
    porosity = (density_log * conversion - 1. / v_sandstone) / (1. / v_water - 1. / v_sandstone)
    # get porosity which is not nan
    porosity = porosity[~np.isnan(porosity)]

    group_size = math.ceil(len(porosity) / int(number_layers))
    groups = []
    for i in range(0, len(porosity), group_size):
        group = porosity[i:i + group_size]
        ave_poro = np.average(group)
        groups.append(ave_poro)

    return np.array(groups)
