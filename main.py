"""
Punto de entrada del programa
"""
from src.view.GUIConsola import GUIConsola


def main():
    objGUIConsola = GUIConsola()
    objGUIConsola.dibujar_menu()


"""LLamada al metodo main en Python"""
if __name__ == '__main__':
    main()
