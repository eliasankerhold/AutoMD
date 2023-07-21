from resonator import Resonator
from acad_api import Acad
from time import sleep
import numpy as np

test_res = Resonator(name='test res', layer='base', maximum_height=500, maximum_width=1000, length=5e3, gap=5, width=8,
                     coupling_length=300, coupling_spacer=500, arc_distance=300, arc_radius=200)

test_res.generate()

print(test_res.cpw_sections)
acad = Acad()

for cpw in test_res.cpw_sections.values():
    for el in cpw.elements:
        el.draw(acad=acad)
        # el.acad_object.setBulge(1, -np.tan(0.25 * np.pi * 0.5))
        # el.acad_object.setBulge(3, np.tan(0.25 * np.pi * 0.5))
