from resonator import Resonator
from acad_api import Acad

test_res = Resonator(name='test res', layer='base', maximum_height=500, maximum_width=2000, length=5e3, gap=7, width=4,
                     coupling_length=100, coupling_spacer=500, arc_radius=92.5, end='straight', anchor=[0, 0])

test_res.generate()

acad = Acad()

for cpw in test_res.cpw_sections.values():
    for el in cpw.elements:
        el.draw(acad=acad)
