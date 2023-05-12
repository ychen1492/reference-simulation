import math

from matplotlib import pyplot as plt
# Kriging interpolation--------------------------------
from pykrige.ok import OrdinaryKriging
from pykrige.uk import UniversalKriging
from gstools import Gaussian
import numpy as np


def harmonic_average(input_array, upscaled_amount):
    """
        For the given input array, do a harmonic average on the input according to the upscale amount
    :param input_array: 1D array of the numbers
    :param upscaled_amount: the number of the groups to upscale to
    :return: the upscaled array
    """
    if upscaled_amount > len(input_array):
        raise Exception('Can not upscale the input, please check upscaled amount...')
    groups = []
    group_size = math.ceil(len(input_array) / upscaled_amount)
    for i in range(0, len(input_array), group_size):
        group = input_array[i:i + group_size]
        # Calculate the sum of the reciprocals
        sum_reciprocals = sum([1.0 / x for x in group])
        # Calculate the harmonic average
        harmonic_avg = len(group) / sum_reciprocals
        groups.append(harmonic_avg)

    return groups


def arithmetic_average(input_array, upscaled_amount):
    """
        For the given input array, do an arithmetic average on the input according to the upscale amount
    :param input_array: 1D array of the numbers
    :param upscaled_amount: the number of the groups to upscale to
    :return: the upscaled array
    """
    if upscaled_amount > len(input_array):
        raise Exception('Can not upscale the input, please check upscaled amount...')
    groups = []
    group_size = math.ceil(len(input_array) / upscaled_amount)
    for i in range(0, len(input_array), group_size):
        group = input_array[i:i + group_size]
        # Calculate the sum of the input
        sum_inputs = sum(group)
        # Calculate the arithmetic average
        arithmetic_avg = sum_inputs/len(group)
        groups.append(arithmetic_avg)

    return groups


def apply_kriging(nx, ny, n_sample, poro):
    """
        Apply kriging to generate a large scope of porosity values for the given dimension
        , the number of samples, and the original values
    :param nx: number of the grid in x direction of the final grid for krigining interpolation
    :param ny: number of the grid in y direction of the final grid for krigining interpolation
    :param n_sample: the number of the samples which can be used
    :param poro: the original porosity values which have the same size as the n_sample
    :return:
    """
    Kriging_switch = 1  # 0 --- ordinary kriging; 1 --- universal kriging

    np.random.seed(1234)
    # n_sample = 40  # set 1000 samples to test if the code is correct
    data_idx_x = np.random.randint(nx, size=n_sample)
    data_idx_y = np.random.randint(ny, size=n_sample)

    # data_poro = 0.225 * (1 + 0.15 * np.random.randn(n_sample))  # generate Gaussian poro of N~(0.225，0.15)
    # poro_temp = poro.reshape((ny, nx))
    data_poro = np.zeros(n_sample)
    for ii in range(n_sample):
        # data_poro[ii] = poro_temp[data_idx_y[ii]][data_idx_x[ii]]
        data_poro[ii] = poro[ii]

    data = np.zeros((n_sample, 3))
    data[:, 0] = data_idx_x
    data[:, 1] = data_idx_y
    data[:, 2] = data_poro

    gridx = np.arange(0, nx, 1)
    gridy = np.arange(0, ny, 1)
    # gridx = np.mgrid[0:99:100j]
    # gridy = np.mgrid[0:99:100j]
    data = data.astype(float)
    data = np.array(data)
    gridx = gridx.astype(float)
    gridy = gridy.astype(float)
    cov_model = Gaussian(dim=2, len_scale=30, anis=6.8, angles=-0.2, var=0.5, nugget=0.5)
    if Kriging_switch == 0:
        OK = OrdinaryKriging(data[:, 0], data[:, 1], data[:, 2], cov_model)
        z, ss = OK.execute('grid', gridx, gridy)
    elif Kriging_switch == 1:
        UK = UniversalKriging(data[:, 0], data[:, 1], data[:, 2], cov_model)
        z, ss = UK.execute('grid', gridx, gridy)

    z[z < 0.1] = 0.01
    z[z > 0.4] = 0.4

    # smoothen the sample point
    for ii, sample in enumerate(data):
        neighbors = []
        try:
            if int(sample[0] - 1) == -1:
                pass
            else:
                neighbors.append(z[int(sample[1]), int(sample[0] - 1)])
        except Exception as e:
            print(str(e))

        try:
            neighbors.append(z[int(sample[1]), int(sample[0] + 1)])
        except Exception as e:
            print(str(e))

        try:
            if int(sample[1] - 1) == -1:
                pass
            else:
                neighbors.append(z[int(sample[1] - 1), int(sample[0])])
        except Exception as e:
            print(str(e))

            try:
                neighbors.append(z[int(sample[1] + 1), int(sample[0])])
            except Exception as e:
                print(str(e))

            z[int(sample[1]), int(sample[0])] = np.average(neighbors)
    # plt.hist(z.flatten(), 25, density=True, facecolor='silver')
    # # plt.imshow(z)
    # plt.matshow(z, origin='lower', cmap='plasma')
    # plt.colorbar()
    # plt.show()

    return z