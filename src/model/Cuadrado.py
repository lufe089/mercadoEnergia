from src.model.FiguraGeometrica import FiguraGeometrica


class Cuadrado(FiguraGeometrica):
    def __init__(self, lado):
        # Invocacion constructor clase padre
        FiguraGeometrica.__init__(self)

        self._lado = lado
        self._nombreFigura = "Cuadrado"

    def averiguar_perimetro(self):
        # Si no se ha calculado previamente se calcula
        if self.get_perimetro() == 0:
            perimetro = self._lado * 4
            # Inicializa el perimetro
            self.set_perimetro(perimetro)
        return self.get_perimetro()

    def averiguar_area(self):
        if self.get_area() == 0:
            area = pow(self._lado, 2)
            self.set_area(area)
        return self.get_area()
