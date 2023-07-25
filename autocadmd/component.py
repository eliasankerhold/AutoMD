from abc import ABC, abstractmethod
from typing import Union
from .acad_api import Acad
from .sections import Section
from .utils import to_rad

import numpy as np
from numpy.typing import NDArray


class Component(ABC):
    """
    Implements an abstract component class as a template for arbitrary structures within a single layer.

    :ivar name: Name of the component.
    :ivar layer: Layer on which all sections of the component will be drawn.
    :ivar maximum_height: Maximum y-space the component can occupy.
    :ivar maximum_width: Maximum x-space the component can occupy.
    :ivar anchor: Coordinates of the anchor point of the component.
    :ivar length: Target length of the component.
    :ivar sections: Dictionary of Section objects which form the component.
    :ivar _sections_list: List of Section objects, updated through _add_section().
    :ivar _actual_length: Counter of the current component length, update each time a section is added through
        _add_section()
    :ivar _mirror_operations: List of mirror operations storing the mirror axis. Will be applied in the draw() method.
    """

    def __init__(self, name: str, layer: str, maximum_height: float, maximum_width: float,
                 anchor: Union[NDArray, list] = np.array([0, 0])):
        """
        Creates instance of Component class.
        """
        self.name = name
        self.layer = layer
        self.max_height = maximum_height
        self.max_width = maximum_width
        self.anchor = anchor
        self.length = 0
        self._actual_length = 0
        self._mirror_operations = []
        self.generated = False

        self.sections = {}
        self._sections_list = []

    @abstractmethod
    def generate(self):
        """
        Generates the component and all its sections in Python.
        """
        pass

    @abstractmethod
    def preview(self):
        """
        Creates a preview of the component.
        """
        pass

    def _add_section(self, section: Section):
        """
        Adds a section to the component and updated the actual length paramter.

        :param section: Section to be added.
        """
        self.sections[section.name] = section
        self._sections_list.append(section)
        self._actual_length += section.length

    def draw(self, acad: Acad):
        """
        Draws the generated sections into AutoCAD.

        :param acad: AutoCAD ActiveX API instance as retrieved by Acad class.
        """
        if self.generated:
            for sec in self.sections.values():
                for i, el in enumerate(sec.elements):
                    el.draw(acad=acad)
                    for p1, p2 in self._mirror_operations:
                        sec.elements[i] = el.acad_object.Mirror(p1, p2)
                        el.clear(acad=acad)

        else:
            print('Structures not generated yet.')

    def move(self, shift: Union[NDArray, list]):
        """
        Moves component as a whole. Must be performed before drawing.

        :param shift: Specifies movement.
        """
        shift = np.array(shift)
        assert shift.shape == (2,)
        for section in self.sections.values():
            for el in section.elements:
                el.points[0::2] += shift[0]
                el.points[1::2] += shift[1]

    def mirror(self, angle: float, rad: bool = False):
        """
        Mirrors whole component along axis going through the anchor and forming an angle with the x-axis.

        :param angle: Angle with the x-axis of mirror axis.
        :param rad: If True, angle is given in radians. Defaults to False.
        """
        if not rad:
            angle = to_rad(angle)
        self._mirror_operations.append(np.array([[self.anchor[0], self.anchor[1], 0],
                                                 [np.cos(angle) + self.anchor[0], np.sin(angle) + self.anchor[1], 0]]))
