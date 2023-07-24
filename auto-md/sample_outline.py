from component import Component
from sections import SampleBoundary


class SampleOutline(Component):
    def __init__(self, thickness: float, **kwargs):
        super(SampleOutline, self).__init__(**kwargs)
        self.thickness = thickness

    def generate(self):
        self._generate_borders()

    def preview(self):
        pass

    def _generate_borders(self):
        border = SampleBoundary(name='sample border', thickness=self.thickness, width=self.max_width,
                                height=self.max_height, anchor=[0, 0])

        self._add_section(section=border)
