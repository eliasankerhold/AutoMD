from component import Component
from sections import CPWStraight, CPWArc, Pad
from numpy.typing import NDArray
from typing import Union
import numpy as np
from utils import to_deg, to_rad


class TransmissionLine(Component):
    def __init__(self, start: Union[NDArray, list], end: Union[NDArray, list], pad_size: Union[NDArray, list],
                 pad_thickness: float, gap: float, width: float, arc_radius: float, center_offset: float = 0, **kwargs):
        super(TransmissionLine, self).__init__(**kwargs)

        self.start = np.array(start)
        self.end = np.array(end)
        self.pad_size = np.array(pad_size)
        self.pad_thickness = pad_thickness
        self.center_offset = center_offset
        self.cpw_width = width
        self.cpw_gap = gap
        self.arc_radius = arc_radius

        self.cpw_params = {'gap': gap, 'width': width}

    def generate(self):
        self._generate_pads()

        path = [{'element': 'straight', 'length': 500},
                {'element': 'left', 'radius': 600, 'angle': 311},
                {'element': 'straight', 'length': 500},
                {'element': 'left', 'radius': 200, 'angle': 34},
                {'element': 'straight', 'length': 300},
                {'element': 'right', 'radius': 100, 'angle': 94},
                {'element': 'left', 'radius': 1000, 'angle': 300}]

        self._generate_cpw_from_path(path=path)

    def preview(self):
        pass

    def _generate_pads(self):
        ll_pad = Pad(name='left lower pad', pad_width=self.pad_size[0], pad_height=self.pad_size[1],
                     thickness=self.pad_thickness, adapter_len=0.25 * self.pad_size[1], angle=-32,
                     anchor=[10, 40], **self.cpw_params)

        ru_pad = Pad(name='right upper pad', pad_width=self.pad_size[0], pad_height=self.pad_size[1],
                     thickness=self.pad_thickness, adapter_len=0.25 * self.pad_size[1], angle=-90,
                     anchor=[500, 500], **self.cpw_params)

        self._add_section(ll_pad)
        self._add_section(ru_pad)

    def _generate_cpw_from_path(self, path: list[dict]):
        current_anchor = self.sections['left lower pad'].endpoints.right_upper
        current_angle = to_deg(self.sections['left lower pad'].angle)
        start_angle = current_angle
        # assert start_angle in [0, 90]

        c = 1

        for info in path:
            if info['element'] == 'straight':
                element = CPWStraight(name=f'cpw element {c}', anchor=current_anchor, angle=current_angle,
                                      length=info['length'], **self.cpw_params)

            elif info['element'] == 'right':
                angle_span = (current_angle + info['angle'] + 90, current_angle + 90)
                element = CPWArc(name=f'cpw element {c}', anchor=current_anchor, angle_span=angle_span,
                                 radius=info['radius'], straighten_other_end=True, **self.cpw_params)

                current_angle -= info['angle']

            elif info['element'] == 'left':
                angle_span = (current_angle - 90, current_angle + info['angle'] - 90)
                element = CPWArc(name=f'cpw element {c}', anchor=current_anchor, angle_span=angle_span,
                                 radius=info['radius'], straighten_other_end=False, **self.cpw_params)

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
            print(c, current_angle)
