from .component import Component
from .acad_api import Acad


class Design:
    def __init__(self, name: str, acad: Acad):
        self.name = name
        self.components = {}
        self.layers = {}
        self.acad = acad

    def add_component(self, component: Component):
        self.components[component.name] = component

    def initialize_acad(self):
        for comp in self.components.values():
            try:
                self.layers[comp.layer]

            except KeyError:
                self.layers[comp.layer] = self.acad.doc.Layers.Add(comp.layer)

    def draw_design(self):
        for comp in self.components.values():
            self.acad.doc.ActiveLayer = self.layers[comp.layer]
            comp.draw(acad=self.acad)
            print(f'Drew {comp.name}')

