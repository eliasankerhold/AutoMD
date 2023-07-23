from numpy.typing import NDArray
import numpy as np
from shapes import PolyArc, PolyRectangle, PLine2d
from utils import rotate_vec, tuple_to_rad, to_rad, dtype
from acad_api import Acad

from typing import Union


class CPWEndpoint:
    def __init__(self, ends: NDArray):
        assert ends.shape[0] == 4
        self.ends = ends


class CPWSection:
    def __init__(self, name: str, gap: float, width: float, anchor: Union[NDArray, list]):
        self.name = name
        self.gap = gap
        self.width = width
        self.anchor = anchor
        self.elements = None
        self.endpoints = None
        self.length = None

    def __repr__(self):
        return f"{self.name}: anchor={self.anchor}"


class CPWStraight(CPWSection):
    def __init__(self, angle: float, length: float, **kwargs):
        super(CPWStraight, self).__init__(**kwargs)

        self.angle = angle
        self.rad_angle = to_rad(self.angle)
        self.length = length

        l_points = np.array([[0, 0],
                             [self.length, 0],
                             [self.length, self.width],
                             [0, self.width]], dtype=dtype)

        u_points = l_points.copy()
        u_points[:, 1] += self.gap + self.width

        for i in range(l_points.shape[0]):
            l_points[i] = rotate_vec(l_points[i], self.angle)
            u_points[i] = rotate_vec(u_points[i], self.angle)

        l_points += self.anchor
        u_points += self.anchor

        r_ends = CPWEndpoint(ends=np.array([l_points[1], l_points[2], u_points[1], u_points[2]]))
        l_ends = CPWEndpoint(ends=np.array([l_points[0], l_points[3], u_points[0], u_points[3]]))

        self.elements = [PLine2d(l_points), PLine2d(u_points)]
        self.endpoints = (l_ends, r_ends)


class CPWArc(CPWSection):
    def __init__(self, radius: float, angle_span: tuple[float, float], **kwargs):
        super(CPWArc, self).__init__(**kwargs)

        self.radius = radius
        self.angle_span = tuple_to_rad(angle_span)
        self.angle = to_rad(angle_span[1] - angle_span[0])
        self.rads = {'inner inner': self.radius - self.width - 0.5 * self.gap,
                     'inner outer': self.radius - 0.5 * self.gap,
                     'outer inner': self.radius + 0.5 * self.gap,
                     'outer outer': self.radius + 0.5 * self.gap + self.width}

        self.length = self.angle / (2 * np.pi) * self.radius

        sincos = np.array([np.cos(self.angle), np.sin(self.angle)])

        inner_points = np.array([[self.rads['inner inner'], 0], [self.rads['inner outer'], 0],
                                 self.rads['inner outer'] * sincos, self.rads['inner inner'] * sincos], dtype=dtype)
        outer_points = np.array([[self.rads['outer inner'], 0], [self.rads['outer outer'], 0],
                                 self.rads['outer outer'] * sincos, self.rads['outer inner'] * sincos], dtype=dtype)

        for i, vec in enumerate(inner_points):
            inner_points[i] = rotate_vec(vec, self.angle_span[0], rad=True)

        for i, vec in enumerate(outer_points):
            outer_points[i] = rotate_vec(vec, self.angle_span[0], rad=True)

        shift = self.anchor - inner_points[0]
        inner_points += shift
        outer_points += shift

        r_ends = CPWEndpoint(
            ends=np.array([inner_points[0], inner_points[1], outer_points[0], outer_points[1]], dtype=dtype))
        l_ends = CPWEndpoint(
            ends=np.array([inner_points[3], inner_points[2], outer_points[3], inner_points[2]], dtype=dtype))

        self.elements = [PolyArc(inner_points, angle=self.angle), PolyArc(outer_points, angle=self.angle)]
        self.endpoints = (l_ends, r_ends)
