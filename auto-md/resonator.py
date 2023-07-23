from component import Component
from cpwblocks import CPWStraight, CPWArc

import numpy as np


class Resonator(Component):
    def __init__(self, length: float, gap: float, width: float, arc_radius: float, coupling_length: float,
                 coupling_spacer: float, arc_distance: float, **kwargs):
        super(Resonator, self).__init__(**kwargs)
        self.length = length
        self._actual_length = 0
        self.gap = gap
        self.width = width
        self.arc_radius = arc_radius
        self.coupling_length = coupling_length
        self.coupling_spacer = coupling_spacer
        self.arc_distance = arc_distance
        self.full_cpw_width = self.width * 2 + self.gap

    def generate(self):
        self._generate_transmission_coupler()
        self._generate_test_arc()
        print('length', self._actual_length)

    def preview(self):
        pass

    def _generate_transmission_coupler(self):
        t_coupler = CPWStraight(length=self.coupling_length, gap=self.gap, width=self.width, anchor=[self.full_cpw_width, 0], angle=90,
                                name='transmission line coupler')

        self.cpw_sections[t_coupler.name] = t_coupler
        self._actual_length += t_coupler.length

    def _generate_spacer_line(self):
        pass

    def _generate_test_arc(self):
        test_arc = CPWArc(name='test arc', gap=self.gap, width=self.width, angle_span=(0, 270),
                          anchor=[self.coupling_length, self.full_cpw_width],
                          radius=200)

        self.cpw_sections[test_arc.name] = test_arc
        self._actual_length += test_arc.length
