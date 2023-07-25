from .component import Component
from .sections import CPWStraight, CPWArc, Pad
from numpy.typing import NDArray
from typing import Union
import numpy as np
from .utils import to_deg, sort_endpoints


class TransmissionLine(Component):
    """
    Implements automatically generated basic transmission line and provides tool to generate more complex architectures
    using simplified pseudo-code.

    :ivar start: Anchor of start Pad. Will automatically be chosen to be the leftmost-lower one.
    :ivar end: Anchor of end Pad. Will automatically be chosen to be the rightmost-upper one.
    :ivar pad_size: Dimensions of the soldering pads, only including its rectangular part.
    :ivar pad_thickness: Thickness of border around soldering pads.
    :ivar center_offset: Offset from the center line of the sample.
    :ivar cpw_width: Width of the conductive part of the CPW.
    :ivar cpw_gap: Width of the gaps of the CPW.
    :ivar arc_radius: Center radius of curves of the CPW.
    :ivar path: Pseudocode dictionaries used to generate the CPW.
    """
    def __init__(self, start: Union[NDArray, list], end: Union[NDArray, list], pad_size: Union[NDArray, list],
                 pad_thickness: float, width: float, gap: float, arc_radius: float, center_offset: float = 0, **kwargs):
        super(TransmissionLine, self).__init__(**kwargs)

        self.start, self.end = sort_endpoints(np.array(start), np.array(end))
        print(self.start, self.end)
        self.pad_size = np.array(pad_size)
        self.pad_thickness = pad_thickness
        self.center_offset = center_offset
        self.cpw_gap = gap
        self.cpw_width = width
        self.arc_radius = arc_radius

        self.path = []

        self._cpw_params = {'width': width, 'gap': gap}

    def generate(self):
        """
        Generates soldering pads and standard transmission line.
        """
        self._generate_pads()

        self._generate_standard_path()
        self._generate_cpw_from_path(path=self.path)

        print(f'<{self.name}> generated, total length = {self._actual_length}')

    def preview(self):
        raise NotImplementedError

    def _generate_pads(self):
        """
        Generates soldering pads and adds them to sections.
        """
        ll_pad = Pad(name='left lower pad', pad_width=self.pad_size[0], pad_height=self.pad_size[1],
                     thickness=self.pad_thickness, adapter_len=0.25 * self.pad_size[1], angle=90,
                     anchor=self.start, **self._cpw_params)

        ru_pad = Pad(name='right upper pad', pad_width=self.pad_size[0], pad_height=self.pad_size[1],
                     thickness=self.pad_thickness, adapter_len=0.25 * self.pad_size[1], angle=270,
                     anchor=self.end, **self._cpw_params)

        self._add_section(ll_pad)
        self._add_section(ru_pad)

    def _generate_standard_path(self):
        """
        Uses peudocde to generate standard S-shaped transmission line path.
        """
        dist = self.end - self.start
        assert np.abs(dist[0]) >= self.arc_radius * 2 or np.isclose(dist[0], 0)
        assert np.abs(dist[1]) >= self.arc_radius * 2 or np.isclose(dist[1], 0)
        assert not np.isclose(np.sum(dist), 0)
        assert 45 < to_deg(self.sections['left lower pad']._angle) < 135
        assert 225 < to_deg(self.sections['right upper pad']._angle) < 315

        center_dist_start = np.array([self.max_width / 2.0, self.max_height / 2.0]) - self.start

        assert (center_dist_start[0] - self.center_offset) > self.arc_radius * 2

        path = [{'element': 'right', 'radius': self.arc_radius, 'angle': 90},
                {'element': 'straight', 'length': center_dist_start[0] - self.center_offset - 2 * self.arc_radius},
                {'element': 'left', 'radius': self.arc_radius, 'angle': 90},
                {'element': 'straight', 'length': np.abs(dist[1]) - 4 * self.arc_radius},
                {'element': 'right', 'radius': self.arc_radius, 'angle': 90},
                {'element': 'straight', 'length': center_dist_start[0] + self.center_offset - 2 * self.arc_radius},
                {'element': 'left', 'radius': self.arc_radius, 'angle': 90}]

        self.path = path

    def _generate_cpw_from_path(self, path: list[dict]):
        """
        Converts pseudocode dictionaries into CPW sections. Can generate three types of CPW sections: A straight, a
        left turn and a right turn, encoded by the 'element' keyword as 'straight', 'left' and 'right'. For a straight,
        'length' has to be supplied, for turns, the radius and angle of the turn as 'radius' and 'angle', the latter in
        degree. Individual sections will automatically be aligned and connected.

        Example: {'element': 'left', 'radius': 200, 'angle': 90} or {'element': 'straight', 'length': 500}

        :param path: List of dictionaries specifying CPW sections to be added.
        """
        current_anchor = self.sections['left lower pad'].endpoints.right_upper
        current_angle = to_deg(self.sections['left lower pad']._angle)

        c = 1

        for info in path:
            if info['element'] == 'straight':
                element = CPWStraight(name=f'cpw element {c}', anchor=current_anchor, angle=current_angle,
                                      length=info['length'], **self._cpw_params)

            elif info['element'] == 'right':
                angle_span = (current_angle + info['angle'] + 90, current_angle + 90)
                element = CPWArc(name=f'cpw element {c}', anchor=current_anchor, angle_span=angle_span,
                                 radius=info['radius'], straighten_other_end=True, **self._cpw_params)

                current_angle -= info['angle']

            elif info['element'] == 'left':
                angle_span = (current_angle - 90, current_angle + info['angle'] - 90)
                element = CPWArc(name=f'cpw element {c}', anchor=current_anchor, angle_span=angle_span,
                                 radius=info['radius'], straighten_other_end=False, **self._cpw_params)

                current_angle += info['angle']

            if c == 1:
                self.sections['left lower pad'].endpoints.connect(current_anchor)

            else:
                self._sections_list[-1].endpoints.connect(current_anchor)

            element.endpoints.connect(current_anchor)
            current_anchor, _ = element.endpoints.get_unconnected()
            assert current_anchor is not None

            c += 1

            self._add_section(section=element)
