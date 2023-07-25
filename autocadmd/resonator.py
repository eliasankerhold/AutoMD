from .component import Component
from .sections import CPWStraight, CPWArc, CPWSection, CPWCap

import numpy as np


class Resonator(Component):
    """
    Implements a CPW resonator with meandering architecture. Is automatically generated within the given constraints.

    :ivar gap: Width of the gap of the CPW.
    :ivar width: Width of the conductive part of the CPW.
    :ivar arc_radius: Central curve radius of CPW curves.
    :ivar coupling_length: Length of the straight coupling segment.
    :ivar coupling_spacer: Length of CPW straight between coupling segment and first meander.
    :ivar end: Type of ending. 'straight' for end cap or 'arc' for arc and open end, 'none' for only open end.
    """
    def __init__(self, length: float, gap: float, width: float, arc_radius: float, coupling_length: float,
                 coupling_spacer: float, end: str = 'arc', **kwargs):
        super(Resonator, self).__init__(**kwargs)
        assert end in ['arc', 'straight', 'none']
        assert self.max_height > arc_radius * 2.1

        self.length = length
        self.width = width
        self.gap = gap
        self.arc_radius = arc_radius
        self.coupling_length = coupling_length
        self.coupling_spacer = coupling_spacer
        self.full_cpw_width = self.gap * 2 + self.width
        self.end = end
        self.n_segments = None

        self.arc_params = {'radius': self.arc_radius, 'width': self.width, 'gap': self.gap}
        self.straight_params = {'width': self.width, 'gap': self.gap}

    def generate(self):
        """
        Generates resonating structure.

        :return: False if generation failed.
        """
        self._generate_transmission_coupler()
        self._generate_spacer_line()
        if self._generate_meanders(final_component_len=self.gap):
            self._generate_end_cap()

        else:
            self.sections = {}
            self._sections_list = []
            return False

        self.move(shift=self.anchor)

        if np.isclose(self.length, self._actual_length):
            print(f'<{self.name}> generated, total length = {self._actual_length}')

        else:
            print(
                f'WARNING: <{self.name}> generated, actual length - target length = {self._actual_length - self.length}')

    def preview(self):
        raise NotImplementedError

    def _generate_transmission_coupler(self):
        """
        Generates straight coupling segment to transmission line.
        """
        t_coupler = CPWStraight(length=self.coupling_length, **self.straight_params, anchor=[0, 0], angle=270,
                                name='transmission line coupler')

        self._add_section(t_coupler)

    def _generate_spacer_line(self):
        """
        Generates 90-degree curve and straight spacing segment from coupler to meandering structures.
        """
        spacer_arc = CPWArc(name='spacer arc', **self.arc_params,
                            anchor=self.sections['transmission line coupler'].endpoints.left_lower,
                            angle_span=(180, 270))

        spacer_line = CPWStraight(name='spacer straight', **self.straight_params,
                                  anchor=spacer_arc.endpoints.right_upper, angle=0, length=self.coupling_spacer)

        self._add_section(spacer_arc)
        self._add_section(spacer_line)

    def _generate_meanders(self, final_component_len: float):
        """
        Computes the amount of meanders and the height of the vertical straight segments based on the target length and
        the maximum available height. Generates the meandering structure accordingly.

        :param final_component_len: Length of the components following after the meandering structure.
        :return: True if generation successful, otherwise False.
        """
        m_height = self.max_height - 2 * self.arc_radius
        count = 0
        success = False
        while not success and count < 1000:
            l_segment = np.pi * self.arc_radius + m_height

            if self.end == 'arc':
                m_len = self.length - (
                        self._actual_length + 2 * np.pi * self.arc_radius + m_height / 2 - self.arc_radius +
                        final_component_len)

            elif self.end == 'straight':
                m_len = self.length - (
                        self._actual_length + 1.5 * np.pi * self.arc_radius + m_height / 2 - self.arc_radius +
                        final_component_len)

            n_segments = int(np.floor(m_len / l_segment))

            if m_len - n_segments * l_segment <= m_height:
                last_height = m_len - n_segments * l_segment
                success = True

            else:
                m_height *= 0.95

            count += 1

        if not success:
            print(f'<{self.name}> generation failed!')
            return False

        meander_entry_arc = CPWArc(name='meander entry arc', **self.arc_params, angle_span=(270, 360),
                                   anchor=self.sections['spacer straight'].endpoints.right_upper)

        meander_entry_straight = CPWStraight(name='meander entry straight', **self.straight_params,
                                             length=m_height / 2.0 - self.arc_radius, angle=90,
                                             anchor=meander_entry_arc.endpoints.right_upper)

        self._add_section(meander_entry_arc)
        self._add_section(meander_entry_straight)

        for i in range(n_segments + 1):
            if i % 2 == 0:
                angle_span = (180, 0)
                angle = 270
                anchor = self._sections_list[-1].endpoints.right_upper

            else:
                angle_span = (180, 360)
                angle = 90
                anchor = self._sections_list[-1].endpoints.left_lower

            if i == n_segments:
                length = last_height

            else:
                length = m_height

            segment_arc = CPWArc(name=f'segment arc {i + 1}', **self.arc_params,
                                 anchor=anchor, angle_span=angle_span)

            segment_straight = CPWStraight(name=f'segment straight {i + 1}', **self.straight_params,
                                           anchor=segment_arc.endpoints.right_upper, length=length, angle=angle)

            self._add_section(segment_arc)
            self._add_section(segment_straight)

        if self.end == 'arc':
            if n_segments % 2 == 0:
                angle_span = (180, 270)
            else:
                angle_span = (180, 90)

            final_arc = CPWArc(name='final arc', **self.arc_params,
                               anchor=self._sections_list[-1].endpoints.right_upper, angle_span=angle_span)

            self._add_section(final_arc)

        self.n_segments = n_segments

        return True

    def _generate_end_cap(self):
        """
        Generates end cap to terminate meandering structure.
        """
        if self.n_segments % 2 == 0:
            angle = 270
            anchor = self._sections_list[-1].endpoints.left_lower

        else:
            angle = 90
            anchor = self._sections_list[-1].endpoints.right_upper

        end_cap = CPWCap(name='end cap', **self.straight_params, anchor=anchor, angle=angle)

        self._add_section(end_cap)
