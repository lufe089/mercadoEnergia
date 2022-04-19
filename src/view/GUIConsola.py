from src.model.Circulo import Circulo
from src.model.Cuadrado import Cuadrado


class GUIConsola:

    def __init__(self) -> None:
        self.figuras = []

        # Agrego un circulo y un cuadrado de pruebas
        self.figuras.append(Circulo(10))
        self.figuras.append(Cuadrado(100))
        self.figuras.append(Cuadrado(20))

    def mostrar_datos_figuras(self):
        for figura in self.figuras:
            print(f"El perimetro de la figura {figura.get_nombre_figura()} es  {figura.averiguar_perimetro()}")
            print(f"El area de la figura {figura.get_nombre_figura()} es  {figura.averiguar_area()}")

    def sumar_areas(self):
        # TODO
        print("Pendiente")

    def contar_figuras_tipo(self):
        contCirculos = 0
        contCuadrados = 0
        for figura in self.figuras:
            if isinstance(figura, Circulo):
                contCirculos += 1
            elif isinstance(figura, Cuadrado):
                contCuadrados += 1

        return contCirculos, contCuadrados

    def dibujar_menu(self):
        opcion = -1
        while (opcion != 0):
            print(" Bienvenido\n")
            print("1. Ver el perimetro y area de las figuras existentes\n")
            print("2. Suma total de todas las areas de las figuras registradas\n")
            print("3. Dibujar figuras existentes\n")
            print("0.  Salir \n")

            opcion = int(input(""))

            if opcion == 1:
                self.mostrar_datos_figuras()
            elif opcion == 2:
                print("Pendiente")
