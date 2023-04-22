import math

import numpy as np


def harmonic_average(input_array, upscaled_amount):
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