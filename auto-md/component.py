from abc import ABC, abstractmethod


class Component(ABC):
    def __init__(self, name: str, layer: str, maximum_height: float, maximum_width: float):
        self.name = name
        self.layer = layer
        self.max_height = maximum_height
        self.max_width = maximum_width

        self.cpw_sections = {}

    @abstractmethod
    def generate(self):
        pass

    @abstractmethod
    def preview(self):
        pass