from abc import ABC, abstractmethod


class FiguraGeometrica(ABC):

    def __init__(self):
        # Atributos  de instancia protegidos
        self._perimetro = 0
        self._area = 0
        self._nombreFigura = " "

    @abstractmethod
    def averiguar_perimetro(self):
        pass

    @abstractmethod
    def averiguar_area(self):
        pass

    def set_perimetro(self, valor):
        self._perimetro = valor

    def set_area(self, valor):
        self._area = valor

    def get_perimetro(self):
        return self._perimetro

    def get_area(self):
        return self._area

    def get_nombre_figura(self):
        return self._nombreFigura
