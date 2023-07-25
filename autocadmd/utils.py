import numpy as np
from numpy.typing import NDArray

rounding_precision = 10  #: Defines global rounding precision
dtype = 'float64'  #: Defines global NDArray data type


def distance_two(p1: NDArray, p2: NDArray) -> float:
    """
    Computes distance between two 2d-points.

    :param p1: Point A.
    :param p2: Point B.
    :return: Distance between A and B.
    """
    assert p1.shape == (2,)
    assert p2.shape == (2,)

    return np.sqrt(np.sum(np.square(p1 - p2)))


def rotate_vec(vec: NDArray, theta: float, rad: bool = False) -> NDArray:
    """
    Rotates 2d-vector about origin.

    :param vec: Vector to be rotated.
    :param theta: Rotation angle.
    :param rad: If True, angle is given in radians. Defaults to False.
    :return: Rotated vector.
    """
    assert vec.shape == (2,)
    if not rad:
        theta = (theta / 180.0) * np.pi

    rot_mat = np.round(np.array([[np.cos(theta), -np.sin(theta)],
                                 [np.sin(theta), np.cos(theta)]], dtype='float64'), rounding_precision)

    return np.dot(rot_mat, vec)


def mirror_points(points: NDArray, theta: float, rad: bool = False) -> NDArray:
    """
    Mirrors an arbitrary number of 2d-vectors.

    :param points: Points to be mirrored.
    :param theta: Angle of mirror axis and x-axis.
    :param rad: If True, angle is given in radians. Defaults to False.
    :return: Mirrored points.
    """
    assert points.shape[1] == 2
    if not rad:
        theta = (theta / 180.0) * np.pi

    ref_mat = np.round(np.array([[np.cos(2 * theta), np.sin(2 * theta)],
                                 [np.sin(2 * theta), -np.cos(2 * theta)]], dtype='float64'), rounding_precision)

    reflected = points.copy()
    for i, p in enumerate(points):
        reflected[i, :] = np.dot(ref_mat, p)

    return reflected


def rotate_points(points: NDArray, theta: float, rad: bool = False) -> NDArray:
    """
    Rotates arbitrary number of 2d-points about the origin.

    :param points: Points to be rotated.
    :param theta: Rotation angle.
    :param rad: If True, angle is given in radians. Defaults to False.
    :return: Rotated points.
    """
    assert points.shape[1] == 2

    rotated = points.copy()
    for i, p in enumerate(points):
        rotated[i, :] = rotate_vec(theta=theta, vec=p, rad=rad)

    return rotated


def tuple_to_rad(angles: tuple) -> tuple:
    """
    Converts tuple of degree to radians.

    :param angles: Tuple of angles in degrees.
    :return: Tuple of angles in radians.
    """
    return angles[0] * np.pi / 180.0, angles[1] * np.pi / 180.0


def to_rad(angle: float) -> float:
    """
    Converts degree to radians.

    :param angle: Angle in degree.
    :return: Angle in radians.
    """
    return angle * np.pi / 180.0


def to_deg(angle: float) -> float:
    """
    Converts radians to degree.

    :param angle: Angle in radians.
    :return: Angle in degree.
    """
    return angle * 180.0 / np.pi


def center_two(p1: NDArray, p2: NDArray) -> NDArray:
    """
    Computes geometrical center between two points.

    :param p1: Point A.
    :param p2: Point B.
    :return: Center of A and B.
    """
    assert p1.shape == (2,)
    assert p2.shape == (2,)

    return np.array([(p2[0] + p1[0]) * 0.5, (p2[1] + p1[1]) * 0.5], dtype=dtype)


def sort_endpoints(p1: NDArray, p2: NDArray) -> (NDArray, NDArray):
    """
    Sorts two points such that the leftmost-lowest is returned first. Returns the leftmost point first, unless both
    points have equal x-coordinates, then returns the lowest point first.

    :param p1: Point A.
    :param p2: Point B.
    :return: Leftmost-lowest and rightmost-highest point.
    """
    assert p1.shape == (2,)
    assert p2.shape == (2,)

    if p1[0] > p2[0]:
        return p2, p1

    elif p1[0] < p2[0]:
        return p1, p2

    elif p1[0] == p2[0]:
        if p1[1] > p2[1]:
            return p2, p1

        else:
            return p1, p2
