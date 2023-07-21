from .component import Component


class Resonator(Component):
    def __init__(self, length: float, gap: float, width: float, arc_radius: float, coupling_length: float,
                 coupling_distance: float, arc_distance: float, **kwargs):

        super(Resonator, self).__init__(**kwargs)
        self.length = length
        self.gap = gap
        self.width = width
        self.arc_radius = arc_radius
        self.coupling_length = coupling_length
        self.coupling_distance = coupling_distance
        self.arc_distance = arc_distance
        


