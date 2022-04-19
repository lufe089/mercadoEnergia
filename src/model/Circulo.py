from src.model.FiguraGeometrica import FiguraGeometrica


class Circulo(FiguraGeometrica):
    def __init__(self, radio):
        # Invocacion constructor clase padre
        FiguraGeometrica.__init__(self)

        self._radio = radio
        self._nombreFigura = "Circulo"
        self._PI = 3.1416

    def averiguar_perimetro(self):
        perimetro = 2 * self._PI * self._radio
        return perimetro

    def averiguar_area(self):
        area = (pow(self._radio, 2)) * self._PI
        return area
