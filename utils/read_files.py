import math
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


def read_las(path_to_las):
    well_log = pd.read_table(path_to_las, delim_whitespace=True)
    well_log = well_log.replace(-999.0000, np.NaN)

    return well_log


def from_las_to_poro(path_to_las, number_layers):
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
    group_size = math.ceil(len(porosity) / int(number_layers))
    groups = []
    # choose the second interval as the reservoir interval
    for i in range(0, len(porosity), group_size):
        group = porosity[i:i + group_size]
        ave_poro = np.average(group)
        groups.append(ave_poro)

    return np.array(groups)


def from_las_to_poro_gamma(path_to_las, number_points):
    """
        For the given las path and number of layers, using the gamma ray to output the porosity
    :param path_to_las: the path to the second las file which contains gamma ray log
    :param number_points: number of points in one interval
    :return:
    """

    well_gr = read_las(path_to_las)["GR"]

    gr_sandstone = min(well_gr)
    gr_shale = max(well_gr)
    # get the shale content
    shale_content_well = (well_gr-gr_sandstone[0])/(gr_shale[0]-gr_sandstone[0])
    # the relationship between shale contents and total porosity
    total_porosity_well = (shale_content_well - 0.4876)/-1.8544
    # effective porosity
    eff_porosity_well = total_porosity_well-shale_content_well*0.1
    # get porosity which is not nan
    eff_porosity_well = eff_porosity_well[~np.isnan(eff_porosity_well)]
    group_size = math.ceil(len(eff_porosity_well) / int(number_points))
    groups = []
    # choose the second interval as the reservoir interval
    for i in range(0, len(eff_porosity_well), group_size):
        group = eff_porosity_well[i:i + group_size]
        ave_poro = np.average(group)
        groups.append(ave_poro)

    return np.array(groups)