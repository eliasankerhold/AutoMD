from component import Component
from sections import CPWStraight, CPWArc, CPWSection, CPWCap

import numpy as np


class Resonator(Component):
    def __init__(self, length: float, gap: float, width: float, arc_radius: float, coupling_length: float,
                 coupling_spacer: float, end: str = 'arc', **kwargs):
        super(Resonator, self).__init__(**kwargs)
        assert end in ['arc', 'straight']
        assert self.max_height > arc_radius * 2.1

        self.length = length
        self._actual_length = 0
        self.gap = gap
        self.width = width
        self.arc_radius = arc_radius
        self.coupling_length = coupling_length
        self.coupling_spacer = coupling_spacer
        self.full_cpw_width = self.width * 2 + self.gap
        self.end = end
        self.n_segments = None

        self.arc_params = {'radius': self.arc_radius, 'gap': self.gap, 'width': self.width}
        self.straight_params = {'gap': self.gap, 'width': self.width}

    def generate(self):
        self._generate_transmission_coupler()
        self._generate_spacer_line()
        if self._generate_meanders(final_component_len=self.width):
            self._generate_end_cap()

        else:
            self.sections = {}
            self._sections_list = []
            return

        self.move(shift=self.anchor)

        if np.isclose(self.length, self._actual_length):
            print(f'<{self.name}> generated, total length = {self._actual_length}')

        else:
            print(
                f'WARNING: <{self.name}> generated, actual length - target length = {self._actual_length - self.length}')

    def preview(self):
        pass

    def _generate_transmission_coupler(self):
        t_coupler = CPWStraight(length=self.coupling_length, **self.straight_params, anchor=[0, 0], angle=270,
                                name='transmission line coupler')

        self._add_section(t_coupler)

    def _generate_spacer_line(self):
        spacer_arc = CPWArc(name='spacer arc', **self.arc_params,
                            anchor=self.sections['transmission line coupler'].endpoints.left_lower,
                            angle_span=(180, 270))

        spacer_line = CPWStraight(name='spacer straight', **self.straight_params,
                                  anchor=spacer_arc.endpoints.right_upper, angle=0, length=self.coupling_spacer)

        self._add_section(spacer_arc)
        self._add_section(spacer_line)

    def _generate_meanders(self, final_component_len: float):
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

            else:
                angle_span = (180, 360)
                angle = 90

            if i == n_segments:
                length = last_height

            else:
                length = m_height

            segment_arc = CPWArc(name=f'segment arc {i + 1}', **self.arc_params,
                                 anchor=self._sections_list[-1].endpoints.right_upper, angle_span=angle_span)

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
        if self.n_segments % 2 == 0:
            angle = 270
            anchor = self._sections_list[-1].endpoints.right_upper

        else:
            angle = 90
            anchor = self._sections_list[-1].endpoints.right_upper

        end_cap = CPWCap(name='end cap', **self.straight_params, anchor=anchor, angle=angle)

        self._add_section(end_cap)
