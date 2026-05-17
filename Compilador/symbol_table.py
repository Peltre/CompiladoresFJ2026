
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

# Diccionario que guarda todas las funciones del programa, y dentro de cada func, guarda su
# Tabla de variables
class DirectorioFunciones:
    def __init__(self):
        self.funciones = {}
        self.scope_actual = None

        # El programa main siempre existe como scope global
        self._agregar('global','nula')
        self.scope_actual = 'global'


    def _agregar(self, nombre, tipo):
        if nombre in self.funciones:
            raise ErrorSemantico(f"Funcion '{nombre}' ya fue declarada")
        self.funciones[nombre] = {
            'tipo': tipo,
            'variables': TablaVariables()
        }

    def agregar_funcion(self, nombre, tipo):
        # El parser llamara a esto cuando encuentra la declaracion de una funcion
        self._agregar(nombre, tipo)

    def entrar_funcion(self, nombre):
        # El parser llama esto al entrar al cuerpo de una funcion *actualiza el scope
        self.scope_actual = nombre

    def salir_funcion(self):
        # Regresar al global scope
        self.scope_actual = 'global'

    def existe_funcion(self, nombre):
        return nombre in self.funciones
    
    def agregar_var(self, nombre, tipo):
        # Agregar variable a la tabla del scope actual
        self.funciones[self.scope_actual]['variables'].agregar(nombre, tipo)

    def buscar_variable(self, nombre):
        # Buscar en tanto el scope local como en el global
        tipo = self.funciones[self.scope_actual]['variables'].buscar(nombre)
        if tipo is not None:
            return tipo
        # Si no se encontro en local, y no estamos en el scope global, buscarla en global
        if self.scope_actual != 'global':
            tipo = self.scope_actual['global']['variables'].buscar(nombre)
            if tipo is not None:
                return tipo
        return None
    
    def variable_existe(self, nombre):
        return self.buscar_variable(nombre) is not None

