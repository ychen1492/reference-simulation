import math
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


def read_las(path_to_las):
    well_californie_sidetrack1_01 = pd.read_table(path_to_las, delim_whitespace=True)
    well_californie_sidetrack1_01 = well_californie_sidetrack1_01.replace(-999.0000, np.NaN)

    return well_californie_sidetrack1_01


def from_las_to_poro(path_to_las, number_layers, reservoir_thickness):
    """
        For the given las path and number of layers, output the porosity
    :param reservoir_thickness: the thickness of the reservoir
    :param path_to_las: the path to las file which contains density log
    :param number_layers: number of reservoir layers
    :return:
    """

    well_californie_sidetrack1_01 = read_las(path_to_las)
    density_log = well_californie_sidetrack1_01['DT']
    # micro second/foot to second/m
    conversion = 1e-6 / 0.3048
    # sandstone velocity and water velocity
    v_sandstone = 5490  # m/s
    v_water = 1490  # m/s
    porosity = (density_log * conversion - 1. / v_sandstone) / (1. / v_water - 1. / v_sandstone)
    # get porosity which is not nan
    porosity = porosity[~np.isnan(porosity)]
    # get the reservoir thickness of porosity
    intervals = []
    # 10 is the interval of measurement
    for i in range(0, len(porosity), reservoir_thickness*10):
        intervals.append(porosity[i:i+reservoir_thickness*10])
    group_size = math.ceil(len(intervals[1]) / int(number_layers))
    groups = []
    # choose the second interval as the reservoir interval
    for i in range(0, len(intervals[1]), group_size):
        group = porosity[i:i + group_size]
        ave_poro = np.average(group)
        groups.append(ave_poro)

    return np.array(groups)
