import numpy as np
from numpy.typing import NDArray

rounding_precision = 10
dtype = 'float64'


def rotate_vec(vec: NDArray, theta: float, rad: bool = False):
    assert vec.shape == (2,)
    if not rad:
        theta = (theta / 180.0) * np.pi

    rot_mat = np.round(np.array([[np.cos(theta), -np.sin(theta)],
                                 [np.sin(theta), np.cos(theta)]], dtype='float64'), rounding_precision)

    return np.dot(rot_mat, vec)


def tuple_to_rad(angles: tuple):
    return angles[0] * np.pi / 180.0, angles[1] * np.pi / 180.0


def to_rad(angle: float):
    return angle * np.pi / 180.0
