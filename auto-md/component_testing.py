from resonator import Resonator
from acad_api import Acad

import numpy as np

acad = Acad()

lengths = np.array([3.24, 3.4, 3.58, 3.78, 3.678, 3.488, 3.32, 3.164]) * 1e3

spacing = 1250

for i, length in enumerate(lengths):

    res = Resonator(name=f'RES {i+1} length={length:.0f}um', layer='base', maximum_height=500, maximum_width=2000,
                    length=length, gap=7, width=4, coupling_length=100, coupling_spacer=200, arc_radius=92.5,
                    end='straight', anchor=[20000, spacing * i])

    res.generate()
    res.draw(acad=acad)


