
# Clase personalizada, para resaltar errores semanticos
class ErrorSemantico(Exception):
    def __int__(self, mensaje):
        super().__init__(f"[ERROR SEMANTICO] {mensaje}")
        

class TablaVariables:
    # Diccionario / contenedor principal
    def __init__(self):
        self.variables = {}

    # Detectar si la variable ya existe, si no, guardarla
    def agregar(self, nombre, tipo):
        if nombre in self.variables:
            raise ErrorSemantico(f"Variable '{nombre}' ya fue declarada en el scope")
        self.variables[nombre] = {'tipo': tipo}
    
    # Retornar el tipo de variable o none si no existe
    def buscar(self, nombre):
        if nombre in self.variables:
            return self.variables[nombre]['tipo']
        return None
    

