import numpy as np
from numpy.typing import NDArray
from abc import ABC, abstractmethod
from acad_api import Acad
from utils import to_rad


class Shape(ABC):
    def __init__(self):
        self.acad_object = None

    @abstractmethod
    def draw(self, acad: Acad):
        pass

    def clear(self, acad: Acad):
        self.acad_object.Delete()


class Point2d(Shape):
    def __init__(self, x: float, y: float):
        super().__init__()
        self.point = np.array([x, y, 0], dtype='float64')

    def draw(self, acad: Acad):
        self.acad_object = acad.model.AddPoint(self.point)


class PLine2d(Shape):
    def __init__(self, points: NDArray):
        super().__init__()
        assert points.shape[1] == 2

        self.points = np.zeros((points.shape[0] + 1, 2))

        for i, p in enumerate(points):
            self.points[i] = np.array([p[0], p[1]], dtype='float64')

        self.points[-1] = self.points[0]

        self.points = self.points.flatten()

    def draw(self, acad: Acad):
        self.acad_object = acad.model.AddLightweightPolyline(self.points)
        self.acad_object.closed = True


class PolyArc(PLine2d):
    def __init__(self, points: NDArray, angle: float):
        super(PolyArc, self).__init__(points=points)
        self.angle = angle

    def draw(self, acad: Acad):
        self.acad_object = acad.model.AddLightweightPolyline(self.points)
        self.acad_object.closed = True
        self.acad_object.SetBulge(1, np.tan(0.25 * self.angle))
        self.acad_object.SetBulge(3, -np.tan(0.25 * self.angle))

