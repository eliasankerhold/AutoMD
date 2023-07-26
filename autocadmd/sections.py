from numpy.typing import NDArray
import numpy as np
from .shapes import PolyArc, PLine2d, PolyBulge
from .utils import (
    rotate_vec, tuple_to_rad, to_rad, dtype, center_two, sort_endpoints, rotate_points, distance_two
)

from typing import Union


class Section:
    """
    Implements arbitrary module or block that is combined with other sections to form a component.

    :ivar name: Name of the section. Must be unique within a single component.
    :ivar anchor: Anchor of the section.
    :ivar length: Length of the section. Defined 0 if not applicable.
    :ivar elements: List of Shape objects that form the section.
    :ivar endpoints: CPWEndpoints object defining the endpoints of the section.
    """
    def __init__(self, name: str, anchor: Union[NDArray, list] = np.array([0, 0])):
        self.name = name
        self.anchor = np.array(anchor, dtype=dtype)
        self.length = 0

        self.elements = None
        self.endpoints = None

    def __repr__(self):
        return f"{self.name}: anchor={self.anchor}, endpoints: {self.endpoints}"


class CPWEndpoints:
    """
    Implements class to define endpoints, i.e., connection or docking points of sections.

    :ivar left_lower: Leftmost-lower endpoint.
    :ivar right_upper: Rightmost-upper endpoints.
    :ivar connected_ll: True if connected to another endpoint at leftmost-lower. Defaults to False.
    :ivar connected_ru: True if connected to another endpoint at rightmost-upper. Defaults to False.
    """
    def __init__(self, left_lower: NDArray, right_upper: NDArray):
        assert left_lower.shape == (2,)
        assert right_upper.shape == (2,)
        self.left_lower = left_lower
        self.right_upper = right_upper
        self.connected_ll = False
        self.connected_ru = False

    def __repr__(self):
        return f'left lower={self.left_lower} - right upper={self.right_upper}'

    def get_connected(self) -> (NDArray, NDArray):
        """
        Returns tuple of all connected endpoints. Gives connected endpoint first if only one is connected. Returns
        None, None if no endpoints are connected.

        :return: Connected endpoints.
        """
        if self.connected_ru and self.connected_ll:
            return self.left_lower, self.right_upper

        elif self.connected_ll:
            return self.left_lower, None

        elif self.connected_ru:
            return self.right_upper, None

        else:
            return None, None

    def get_unconnected(self) ->(NDArray, NDArray):
        """
        Returns tuple of all unconnected endpoints. Gives unconnected endpoint first if only one is unconnected. Returns
        None, None if no endpoints are unconnected.

        :return: Unconnected endpoints.
        """
        if not self.connected_ru and not self.connected_ll:
            return self.left_lower, self.right_upper

        elif not self.connected_ll:
            return self.left_lower, None

        elif not self.connected_ru:
            return self.right_upper, None

        else:
            return None, None

    def connect(self, anchor: Union[NDArray, list], tol: float=1e-3):
        """
        Marks endpoint as connected if within circle with radius tol around given anchor.

        :param anchor: Point to be connected to.
        :param tol: Maximum distance between anchor and one of the unconnected endpoints to still be connected.
        """
        anchor = np.array(anchor)
        assert anchor.shape == (2, )

        dists = np.array([distance_two(anchor, self.left_lower), distance_two(anchor, self.right_upper)])

        conn = np.argmin(dists)

        tols = np.array([True if i <= tol else False for i in dists])
        status = np.array([self.connected_ll, self.connected_ru])

        available = np.logical_and(tols, ~status)

        if conn == 0 and available[0]:
            self.connected_ll = True

        elif conn == 1 and available[1]:
            self.connected_ru = True

        else:
            raise Exception('Points to far apart to be connected or already connected. '
                            'Consider increasing tolerance tol=1e-3')


class CPWSection(Section):
    """
    Implements parent class for any CPW section.

    :ivar width: Width of the conductive part of the CPW.
    :ivar gap: Width of the gaps of the CPW.
    :ivar half_cpw_width: Half of the full width of the CPW.
    """
    def __init__(self, gap: float, width: float, **kwargs):
        super(CPWSection, self).__init__(**kwargs)
        self.width = width
        self.gap = gap
        self.half_cpw_width = 0.5 * self.width + self.gap


class CPWStraight(CPWSection):
    """
    Implements straight CPW section.

    :ivar angle: Tilt angle between section and x-axis, in degree.
    """
    def __init__(self, angle: float, length: float, **kwargs):
        super(CPWStraight, self).__init__(**kwargs)

        self.angle = angle
        self._rad_angle = to_rad(self.angle)
        self.length = np.abs(length)

        l_points = np.array([[0, 0],
                             [self.length, 0],
                             [self.length, self.gap],
                             [0, self.gap]], dtype=dtype)

        l_points[:, 1] -= self.half_cpw_width
        u_points = l_points.copy()
        u_points[:, 1] += self.width + self.gap

        for i in range(l_points.shape[0]):
            l_points[i] = rotate_vec(l_points[i], self.angle)
            u_points[i] = rotate_vec(u_points[i], self.angle)

        l_points += self.anchor
        u_points += self.anchor

        end_a = center_two(l_points[0], u_points[3])
        end_b = center_two(l_points[1], u_points[2])

        self.elements = [PLine2d(l_points), PLine2d(u_points)]
        self.endpoints = CPWEndpoints(*sort_endpoints(end_a, end_b))


class CPWArc(CPWSection):
    """
    Implements curve segment of CPW.

    :ivar radius: Curve radius of the center of the CPW.
    :ivar angle_span: Start and stop angle spanned by the curve, in degree.
    :ivar rads: Inner and outer radii of the CPW elements.
    """
    def __init__(self, radius: float, angle_span: tuple[float, float], straighten_other_end: bool = False, **kwargs):
        super(CPWArc, self).__init__(**kwargs)

        self.radius = radius
        self.angle_span = tuple_to_rad(angle_span)
        self._angle = to_rad(angle_span[1] - angle_span[0])
        self.rads = {'inner inner': self.radius - self.gap - 0.5 * self.width,
                     'inner outer': self.radius - 0.5 * self.width,
                     'outer inner': self.radius + 0.5 * self.width,
                     'outer outer': self.radius + 0.5 * self.width + self.gap}

        self.length = np.abs(self._angle * self.radius)

        sincos = np.array([np.cos(self._angle), np.sin(self._angle)])

        inner_points = np.array([[self.rads['inner inner'], 0], [self.rads['inner outer'], 0],
                                 self.rads['inner outer'] * sincos, self.rads['inner inner'] * sincos], dtype=dtype)
        outer_points = np.array([[self.rads['outer inner'], 0], [self.rads['outer outer'], 0],
                                 self.rads['outer outer'] * sincos, self.rads['outer inner'] * sincos], dtype=dtype)

        rot_angle = self.angle_span[0]
        an_ind = 0

        if straighten_other_end:
            rot_angle = self.angle_span[1]
            an_ind = 1

        for i, vec in enumerate(inner_points):
            inner_points[i] = rotate_vec(vec, rot_angle, rad=True)

        for i, vec in enumerate(outer_points):
            outer_points[i] = rotate_vec(vec, rot_angle, rad=True)

        shift = self.anchor - (inner_points[0] + self.half_cpw_width * np.array(
            [np.cos(self.angle_span[an_ind]), np.sin(self.angle_span[an_ind])]))
        inner_points += shift
        outer_points += shift

        l_end = center_two(p1=inner_points[3], p2=outer_points[2])

        self.elements = [PolyArc(inner_points, angle=self._angle), PolyArc(outer_points, angle=self._angle)]
        self.endpoints = CPWEndpoints(*sort_endpoints(l_end, self.anchor))


class CPWCap(CPWSection):
    """
    Implements end cap to terminate CPW sections.

    :ivar fillet_radius: Fillet radius for edges.
    :ivar angle: Tilt angle with the x-axis, in degree.
    :ivar rounded: If True, produces rounded cap. Rectangular if False.
    """
    def __init__(self, angle: float, rounded: bool = True, **kwargs):
        super(CPWCap, self).__init__(**kwargs)

        self.fillet_radius = self.width * 0.5
        self.angle = angle
        self.rounded = rounded
        self.length = self.gap

        if self.rounded:
            self.points = np.array([[0, 0],
                                    [self.gap, 0],
                                    [self.gap * 2, self.gap],
                                    [self.gap * 2, self.gap + self.width],
                                    [self.gap, self.half_cpw_width * 2],
                                    [0, self.half_cpw_width * 2],
                                    [0, self.half_cpw_width * 2 - self.gap],
                                    [0, self.half_cpw_width * 2 - self.gap - self.width]]) - np.array(
                [0, self.half_cpw_width])

            angle_signs = np.array([[np.pi / 2.0, 1], [np.pi / 2.0, 1], [np.pi, -1]])
            bulge_inds = [1, 3, 6]

            for i, p in enumerate(self.points):
                self.points[i] = rotate_vec(p, theta=self.angle)

            self.points += self.anchor

            self.elements = [PolyBulge(points=self.points, angles_signs=angle_signs, bulge_inds=bulge_inds)]
            # self.endpoints = CPWEndpoint(left_lower=)

        else:
            raise NotImplementedError


class SampleBoundary(Section):
    """
    Implements simple sample boundary polygons.

    :ivar thickness: Thickness of the boundary.
    :ivar width: Total width of the sample, outer edge to outer edge.
    :ivar height: Total height of the sample, outer edge to outer edge.
    """
    def __init__(self, thickness: float, width: float, height: float, **kwargs):
        super(SampleBoundary, self).__init__(**kwargs)
        self.thickness = thickness
        self.width, self.height = width, height

        ll_points = np.array([[0, 0],
                              [self.width - self.thickness, 0],
                              [self.width - self.thickness, self.thickness],
                              [self.thickness, self.thickness],
                              [self.thickness, self.height],
                              [0, self.height]])

        ru_points = np.array([[self.width - self.thickness, 0],
                              [self.width, 0],
                              [self.width, self.height],
                              [self.thickness, self.height],
                              [self.thickness, self.height - self.thickness],
                              [self.width - self.thickness, self.height - self.thickness]])

        self.elements = [PLine2d(points=ll_points), PLine2d(points=ru_points)]


class Pad(Section):
    """
    Implements standard soldering pad with rectangular base shape and funnel-like connection to CPW segments.

    :ivar pad_height: Height of the pad main area.
    :ivar pad_width: Width of the pad main area.
    :ivar thickness: Thickness of the pad border.
    :ivar adapter_len: Length of the funnel-like adapter to CPW segments.
    :ivar cpw_width: Width of the conductive part of the CPW.
    :ivar cpw_gap: Width of the gap of the CPW.
    :ivar angle: Rotation angle with x-axis, given in degree.
    """
    def __init__(self, pad_height: float, pad_width: float, thickness: float, adapter_len: float, width: float,
                 gap: float, angle: float, **kwargs):
        super(Pad, self).__init__(**kwargs)

        self.pad_height = pad_height
        self.pad_width = pad_width
        self.thickness = thickness
        self.adapter_len = adapter_len
        self.cpw_gap = gap
        self.cpw_width = width
        self.angle = angle
        self._rad_angle = to_rad(angle)
        self._shifted_angle = to_rad(angle - 90)

        left_cpw_points = np.array([[self.pad_width / 2.0 - 0.5 * self.cpw_width, self.pad_height + self.adapter_len],
                                    [self.pad_width / 2.0 - 0.5 * self.cpw_width - self.cpw_gap,
                                     self.pad_height + self.adapter_len]])

        right_cpw_points = left_cpw_points + np.array([self.cpw_width + self.cpw_gap, 0])

        ll_points = np.array([[0, 0],
                              [self.thickness, 0],
                              [self.thickness, self.pad_height],
                              left_cpw_points[0],
                              left_cpw_points[1],
                              [0, self.pad_height]])

        ru_points = np.array([[self.thickness, 0],
                              [self.pad_width, 0],
                              [self.pad_width, self.pad_height],
                              right_cpw_points[0],
                              right_cpw_points[1],
                              [self.pad_width - self.thickness, self.pad_height],
                              [self.pad_width - self.thickness, self.thickness],
                              [self.thickness, self.thickness]])

        ll_points = rotate_points(ll_points, theta=self._shifted_angle, rad=True)
        ru_points = rotate_points(ru_points, theta=self._shifted_angle, rad=True)

        end = center_two(ll_points[3], ru_points[4])

        ll_points += (self.anchor - end)
        ru_points += (self.anchor - end)

        end = self.anchor

        self.elements = [PLine2d(points=ll_points), PLine2d(points=ru_points)]
        self.endpoints = CPWEndpoints(left_lower=end, right_upper=end)
