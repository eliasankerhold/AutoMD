from abc import ABC, abstractmethod
from typing import Union
from acad_api import Acad
from sections import Section

import numpy as np
from numpy.typing import NDArray


class Component(ABC):
    def __init__(self, name: str, layer: str, maximum_height: float, maximum_width: float,
                 anchor: Union[NDArray, list] = np.array([0, 0])):
        self.name = name
        self.layer = layer
        self.max_height = maximum_height
        self.max_width = maximum_width
        self.anchor = anchor
        self.length = 0

        self.sections = {}
        self._sections_list = []

    @abstractmethod
    def generate(self):
        pass

    @abstractmethod
    def preview(self):
        pass

    def _add_section(self, section: Section):
        self.sections[section.name] = section
        self._sections_list.append(section)
        self.length += section.length

    def draw(self, acad: Acad):
        for sec in self.sections.values():
            for el in sec.elements:
                el.draw(acad=acad)

    def move(self, shift: Union[NDArray, list]):
        shift = np.array(shift)
        assert shift.shape == (2,)
        for section in self.sections.values():
            for el in section.elements:
                el.points[0::2] += shift[0]
                el.points[1::2] += shift[1]
