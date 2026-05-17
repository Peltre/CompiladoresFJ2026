# Clase que define el diccionario donde se guardaran las variables y tipos del compilador

class TablaVariables:
    # Diccionario / contenedor principal
    def __init__(self):
        self.variables = {}

    # Detectar si la variable ya existe, si no, guardarla
    def agregar(self, nombre, tipo):
        if nombre in self.variables:
            print(f"[ERROR SEMANTICO], Variable '{nombre}' ya fue declarada")
            return
        self.variables[nombre] = {'tipo': tipo}
    
    # Retornar el tipo de variable o none si no existe
    def buscar(self, nombre):
        if nombre in self.variables:
            return self.variables[nombre]['tipo']
        return None

