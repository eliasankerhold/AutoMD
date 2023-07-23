import numpy as np
from numpy.typing import NDArray
from abc import ABC, abstractmethod
from acad_api import Acad
from utils import to_rad, rounding_precision, dtype


class Shape(ABC):
    def __init__(self, roun_prec=rounding_precision):
        self.acad_object = None
        self.round_prec = roun_prec

    @abstractmethod
    def draw(self, acad: Acad):
        pass

    def clear(self, acad: Acad):
        self.acad_object.Delete()


class Point2d(Shape):
    def __init__(self, x: float, y: float):
        super().__init__()
        self.point = np.round(np.array([x, y, 0], dtype=dtype), self.round_prec)

    def draw(self, acad: Acad):
        self.acad_object = acad.model.AddPoint(self.point)


class PLine2d(Shape):
    def __init__(self, points: NDArray):
        super().__init__()
        assert points.shape[1] == 2

        self.points = np.zeros((points.shape[0] + 1, 2), dtype=dtype)

        for i, p in enumerate(points):
            self.points[i] = np.array([p[0], p[1]], dtype=dtype)

        self.points[-1] = self.points[0]

        self.points = np.round(self.points.flatten(), self.round_prec)

    def draw(self, acad: Acad):
        self.acad_object = acad.model.AddLightweightPolyline(self.points)
        self.acad_object.closed = True


class PolyArc(PLine2d):
    def __init__(self, points: NDArray, angle: float):
        super(PolyArc, self).__init__(points=points)
        self.angle = angle
        self.bulge = np.round(np.tan(0.25 * self.angle), self.round_prec)

    def draw(self, acad: Acad):
        self.acad_object = acad.model.AddLightweightPolyline(self.points)
        self.acad_object.closed = True
        self.acad_object.SetBulge(1, self.bulge)
        self.acad_object.SetBulge(3, -self.bulge)


class PolyRectangle(PLine2d):
    def __init__(self, points: NDArray, angle: float):
        super(PolyRectangle, self).__init__(points=points)
        self.angle = angle
        self.base_point = np.array([np.average(self.points[0::2]), np.average(self.points[1::2]), 0], dtype=dtype)

    def draw(self, acad: Acad):
        super(PolyRectangle, self).draw(acad=acad)
        self.acad_object.Rotate(self.base_point, self.angle)
