from ..autocadmd.design import Design
from ..autocadmd.acad_api import Acad
from ..autocadmd.resonator import Resonator
from ..autocadmd.sample_outline import SampleOutline
from ..autocadmd.transmissionline import TransmissionLine

import numpy as np

acad = Acad()

design = Design(name='test', acad=acad)
design.initialize_acad()

t_line = TransmissionLine(name='transmission line', maximum_height=5e3, maximum_width=5e3, pad_thickness=120,
                          pad_size=[440, 520], gap=4, width=7, start=[0, 0], end=[5e3, 5e3], layer='base',
                          arc_radius=100, center_offset=400)

t_line.generate()
design.add_component(t_line)


border = SampleOutline(name='border', maximum_height=5e3, maximum_width=5e3, thickness=200, layer='base')
border.generate()
design.add_component(border)

lengths = np.array([3.24, 3.4, 3.58, 3.78, 3.678, 3.488, 3.32, 3.164]) * 1e3

spacing = 1250

for i, length in enumerate(lengths):

    res = Resonator(name=f'RES {i+1} length={length:.0f}um', layer='base', maximum_height=800, maximum_width=2000,
                    length=length, gap=7, width=4, coupling_length=100, coupling_spacer=200, arc_radius=92.5,
                    end='straight', anchor=[1000, spacing * i])

    res.generate()
    design.add_component(res)

design.initialize_acad()
design.draw_design()