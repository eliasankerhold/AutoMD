from .component import Component
from .sections import SampleBoundary


class SampleOutline(Component):
    """
    Implements a simple border with finite thickness at the sample edge.


    :ivar thickness: Thickness of the border.
    """
    def __init__(self, thickness: float, **kwargs):
        """
        Creates SampleOutline object.

        :param kwargs: Keyword arguments passed to super class Component.
        """
        super(SampleOutline, self).__init__(**kwargs)
        self.thickness = thickness

    def generate(self):
        """
        Generates structures.
        """
        self._generate_borders()
        self.generated = True

    def preview(self):
        raise NotImplementedError

    def _generate_borders(self):
        """
        Generates SampleBoundary object with specified parameters and adds it to sections.
        """
        border = SampleBoundary(name='sample border', thickness=self.thickness, width=self.max_width,
                                height=self.max_height, anchor=self.anchor)

        self._add_section(section=border)
