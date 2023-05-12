import math
import os
import pickle

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from skimage.transform import resize

from utils.math_rel import apply_kriging


def read_las(path_to_las):
    """
        Retrieve the log values from the las file
    :param path_to_las: the path to the las file which contains the log data
    :return: the log values which are from the las. it is a DataFrame
    """
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


def from_las_to_poro_gamma(path_to_las, number_of_layers):
    """
        For the given las path and number of layers, using the gamma ray to output the porosity
    :param path_to_las: the path to the second las file which contains gamma ray log
    :param number_of_layers: number of layers
    :return: porosity for different layers
    """

    well_gr = read_las(path_to_las)
    if 'DEPTH' in well_gr.columns:
        well_gr = well_gr[(well_gr['DEPTH'] <= 2100) & (2000 <= well_gr['DEPTH'])]
    elif 'DEPT' in well_gr.columns:
        well_gr = well_gr[(2000 <= well_gr['DEPT']) & (well_gr['DEPT'] <= 2100)]
    if 'GR' in well_gr.columns:
        well_gamma_ray = well_gr['GR']
    elif 'GR_A' in well_gr.columns:
        well_gamma_ray = well_gr['GR_A']
    gr_sandstone = min(well_gamma_ray)
    gr_shale = max(well_gamma_ray)
    # get the shale content
    shale_content_well = (well_gamma_ray - gr_sandstone) / (gr_shale - gr_sandstone)
    # the relationship between shale contents and total porosity
    total_porosity_well = (shale_content_well - 0.4876) / -1.8544
    # effective porosity
    eff_porosity_well = abs(total_porosity_well - shale_content_well * 0.1)
    # get porosity which is not nan
    eff_porosity_well = eff_porosity_well[~np.isnan(eff_porosity_well)]
    group_size = math.ceil(len(eff_porosity_well) / int(number_of_layers))
    groups = []
    # choose the second interval as the reservoir interval
    for i in range(0, len(eff_porosity_well), group_size):
        group = eff_porosity_well[i:i + group_size]
        ave_poro = np.average(group)
        groups.append(ave_poro)

    return np.array(groups)


def get_porosity_values(nz):
    """
        Read las files from seven wells and output the porosity using kriging
        for different nz
    :param nz: number of the grid in z direction
    :return: 1D array of porosity
    """
    well_1_poro = from_las_to_poro_gamma('LogData/Well_HONSELERSDIJK_GT_01_depth_gr.las', nz)
    well_2_poro = from_las_to_poro_gamma('LogData/Well_PIJNACKER_GT_01_depth_gamma_4.las', nz)
    well_3_poro = from_las_to_poro_gamma('LogData/Well_PIJNACKER_GT_03_SIDETRACK2_depth_gamma_2.las', nz)
    well_4_poro = from_las_to_poro_gamma('LogData/Well_DE_LIER_GT_01_depth_gr_3.las', nz)
    well_5_poro = from_las_to_poro_gamma('LogData/Well_POELDIJK_GT_01_depth_gr_temp_2.las', nz)
    well_6_poro = from_las_to_poro_gamma('LogData/Well_KWINNTSHEUL_GT_01_depth_gr_temp.las', nz)
    well_7_poro = from_las_to_poro_gamma('LogData/Well_NAALDWIJK_GT_01_depth_cali_sonic_gr_pef_rhob_rt_rxo_nphi.las',
                                         nz)

    # poros = []
    for i in range(nz):
        data_points = np.array([well_1_poro[i], well_2_poro[i], well_3_poro[i], well_4_poro[i], well_5_poro[i],
                                well_6_poro[i], well_7_poro[i]])
        layers_poro = apply_kriging(900, 900, len(data_points), data_points)
        # poros.append(layers_poro)
    #
    # return np.array(poros)

        if not os.path.exists('Porosity20'):
            os.mkdir('Porosity20')

        # Open a file and use dump()
        with open(f'./Porosity20/layer_poro_{i}.pkl', 'wb') as file:

            # A new file will be created
            pickle.dump(layers_poro, file)


def read_pickle_file(ny, nx, dir_to_pickle):
    """
        This method is used in heterogeneous reservoir resolution and layers study
        when nz is 10
    :param ny: number of the grid in y direction
    :param nx: number of the grid in x direction
    :param dir_to_pickle: the directory which contains the pickles files for just 10 layers' porosity
    :return: 1D array of porosity and permeability
    """
    poros = {}
    perms = {}
    for file in sorted(os.listdir(dir_to_pickle)):
        if file.endswith(".pkl"):
            # Open the file in binary mode
            with open(os.path.join(dir_to_pickle, file), 'rb') as f:
                # Call load method to deserialze
                poro = pickle.load(f)
                f = [110.744 * (p ** 3) - 171.8268 * (p ** 2) + 92.9227 * p - 2.047 for p in poro.flatten()]
                org_perm = [np.exp(x) for x in f]
                perm = np.reshape(org_perm, poro.shape)
                poro = resize(poro, (ny, nx), order=1, mode='reflect', anti_aliasing=True)
                perm = resize(perm, (ny, nx), order=0, mode='reflect', anti_aliasing=True)
                poros[file] = np.rot90(poro).flatten(order='F')
                perms[file] = np.rot90(perm).flatten(order='F')
    porosity = []
    for i in list(poros.values()):
        porosity.extend(i)
    permeability = []
    for i in list(perms.values()):
        permeability.extend(i)
    return np.array(porosity), np.array(permeability)

def read_pickle_file_upscaling_z(ny, nx, nz, dir_to_pickle):
    """
        The way to get the upscaled reservoir permeability, porosity when different
        nx, ny and nz are given
    :param ny: number of the grid in y direction
    :param nx: number of the grid in x direction
    :param nz: number of the grid in z direction
    :param dir_to_pickle: the directory which contains the pickle files which have porosity in
    :return: porosity, permeability in 1D
    """
    poros = []
    perms = []
    for file in os.listdir(dir_to_pickle):
        if file.endswith(".pkl"):
            # Open the file in binary mode
            with open(os.path.join(dir_to_pickle, file), 'rb') as f:
                # Call load method to deserialze
                poro = pickle.load(f)
                f = [110.744 * (p ** 3) - 171.8268 * (p ** 2) + 92.9227 * p - 2.047 for p in poro.flatten()]
                org_perm = [np.exp(x) for x in f]
                perm = np.reshape(org_perm, poro.shape)
                poro = resize(poro, (ny, nx), order=1, mode='reflect', anti_aliasing=True)
                perm = resize(perm, (ny, nx), order=0, mode='reflect', anti_aliasing=True)
                poros.append(poro)
                perms.append(perm)
    porosity = np.array(poros)
    permeability = np.array(perms)

    porosity = resize(porosity, (nz, ny, nx), order=1, mode='reflect', anti_aliasing=True)
    permeability = resize(permeability, (nz, ny, nx), order=0, mode='reflect', anti_aliasing=True)
    # fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    # axx = fig.axes
    # permplot = axx[0].imshow(permeability[2,:,:], cmap='viridis', aspect='auto')
    # axx[0].scatter(120, 35, color='r', marker='x')
    # axx[0].scatter(210, 35, color='r', marker='o')
    # fig.colorbar(permplot, ax=axx[0], location='bottom', label='Permeability (mD)')
    # plt.show()

    return porosity.flatten(), permeability.flatten()