import numpy as np
from numpy.typing import NDArray
from abc import ABC, abstractmethod
from acad_api import Acad
from utils import to_rad, rounding_precision, dtype


class Shape(ABC):
    def __init__(self, points: NDArray = None, round_prec: int = rounding_precision):
        self.acad_object = None
        self.round_prec = round_prec
        self.points = points

    @abstractmethod
    def draw(self, acad: Acad):
        pass

    def clear(self, acad: Acad):
        self.acad_object.Delete()


class Point2d(Shape):
    def __init__(self, x: float, y: float):
        super().__init__(points=np.round(np.array([x, y, 0], dtype=dtype), self.round_prec))

    def draw(self, acad: Acad):
        self.acad_object = acad.model.AddPoint(self.points)


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
        assert points.shape == (4, 2)
        super(PolyArc, self).__init__(points=points)
        self.angle = angle
        self.bulge = np.round(np.tan(0.25 * self.angle), self.round_prec)

    def draw(self, acad: Acad):
        super().draw(acad=acad)
        self.acad_object.SetBulge(1, self.bulge)
        self.acad_object.SetBulge(3, -self.bulge)


class PolyBulge(PLine2d):
    def __init__(self, points: NDArray, angles_signs: NDArray, bulge_inds: list):
        assert angles_signs.shape[0] == len(bulge_inds)
        super(PolyBulge, self).__init__(points=points)

        self.angles_signs = np.array(angles_signs)
        self.bulge_inds = np.array(bulge_inds, dtype=int)

        self.bulge_values = np.round(np.tan(0.25 * self.angles_signs[:, 0]), self.round_prec) * self.angles_signs[:, 1]

    def draw(self, acad: Acad):
        super().draw(acad=acad)
        for i, k in zip(self.bulge_inds, self.bulge_values):
            self.acad_object.setBulge(i, k)
