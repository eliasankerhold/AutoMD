from numpy.typing import NDArray
import numpy as np
from shapes import PolyArc, PLine2d, PolyBulge
from utils import rotate_vec, tuple_to_rad, to_rad, dtype, center_two, sort_endpoints

from typing import Union


class CPWEndpoint:
    def __init__(self, left_lower: NDArray, right_upper: NDArray):
        assert left_lower.shape == (2,)
        assert right_upper.shape == (2,)
        self.left_lower = left_lower
        self.right_upper = right_upper

    def __repr__(self):
        return f'left lower={self.left_lower} - right upper={self.right_upper}'


class CPWSection:
    def __init__(self, name: str, gap: float, width: float, anchor: Union[NDArray, list]):
        self.name = name
        self.gap = gap
        self.width = width
        self.anchor = np.array(anchor, dtype=dtype)
        self.elements = None
        self.endpoints = None
        self.length = None
        self.half_cpw_width = 0.5 * self.gap + self.width

    def __repr__(self):
        return f"{self.name}: anchor={self.anchor}, endpoints: {self.endpoints}"


class CPWStraight(CPWSection):
    def __init__(self, angle: float, length: float, **kwargs):
        super(CPWStraight, self).__init__(**kwargs)

        self.angle = angle
        self.rad_angle = to_rad(self.angle)
        self.length = np.abs(length)

        l_points = np.array([[0, 0],
                             [self.length, 0],
                             [self.length, self.width],
                             [0, self.width]], dtype=dtype)

        l_points[:, 1] -= self.half_cpw_width
        u_points = l_points.copy()
        u_points[:, 1] += self.gap + self.width

        l_end = rotate_vec(self.anchor, self.angle)
        r_end = rotate_vec(np.array([self.length, 0]), self.angle) + self.anchor

        for i in range(l_points.shape[0]):
            l_points[i] = rotate_vec(l_points[i], self.angle)
            u_points[i] = rotate_vec(u_points[i], self.angle)

        l_points += self.anchor
        u_points += self.anchor

        self.elements = [PLine2d(l_points), PLine2d(u_points)]
        self.endpoints = CPWEndpoint(*sort_endpoints(l_end, r_end))


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

        self.length = np.abs(self.angle * self.radius)

        sincos = np.array([np.cos(self.angle), np.sin(self.angle)])

        inner_points = np.array([[self.rads['inner inner'], 0], [self.rads['inner outer'], 0],
                                 self.rads['inner outer'] * sincos, self.rads['inner inner'] * sincos], dtype=dtype)
        outer_points = np.array([[self.rads['outer inner'], 0], [self.rads['outer outer'], 0],
                                 self.rads['outer outer'] * sincos, self.rads['outer inner'] * sincos], dtype=dtype)

        for i, vec in enumerate(inner_points):
            inner_points[i] = rotate_vec(vec, self.angle_span[0], rad=True)

        for i, vec in enumerate(outer_points):
            outer_points[i] = rotate_vec(vec, self.angle_span[0], rad=True)

        shift = self.anchor - (inner_points[0] + self.half_cpw_width * np.array(
            [np.cos(self.angle_span[0]), np.sin(self.angle_span[0])]))
        inner_points += shift
        outer_points += shift

        l_end = center_two(p1=inner_points[3], p2=outer_points[2])

        self.elements = [PolyArc(inner_points, angle=self.angle), PolyArc(outer_points, angle=self.angle)]
        self.endpoints = CPWEndpoint(*sort_endpoints(l_end, self.anchor))


class CPWCap(CPWSection):
    def __init__(self, angle: float, rounded: bool = True, **kwargs):
        super(CPWCap, self).__init__(**kwargs)

        self.fillet_radius = self.gap * 0.5
        self.angle = angle
        self.rounded = rounded
        self.length = self.width

        if self.rounded:
            self.points = np.array([[0, 0],
                                    [self.width, 0],
                                    [self.width * 2, self.width],
                                    [self.width * 2, self.width + self.gap],
                                    [self.width, self.half_cpw_width * 2],
                                    [0, self.half_cpw_width * 2],
                                    [0, self.half_cpw_width * 2 - self.width],
                                    [0, self.half_cpw_width * 2 - self.width - self.gap]]) - np.array(
                [0, self.half_cpw_width])

            angle_signs = np.array([[np.pi / 2.0, 1], [np.pi / 2.0, 1], [np.pi, -1]])
            bulge_inds = [1, 3, 6]

            for i, p in enumerate(self.points):
                self.points[i] = rotate_vec(p, theta=self.angle)

            self.points += self.anchor

            self.elements = [PolyBulge(points=self.points, angles_signs=angle_signs, bulge_inds=bulge_inds)]

        else:
            raise NotImplementedError
