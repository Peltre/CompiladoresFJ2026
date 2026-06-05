# symbol_table.py | LM: 5/29/2026 | By: Pedro Sotelo
# Tabla de variables por scope y directorio de funciones del programa.

# ERROR SEMANTICO
# Excepcion personalizada para errores de tipo y declaracion
class ErrorSemantico(Exception):
    def __init__(self, mensaje):
        super().__init__(f"[ERROR SEMANTICO] {mensaje}")
        
# TABLA DE VARIABLES
# Contenedor de variables para un scope dado
# Cada entrada guarda tipo y direccion virtual
class TablaVariables:
    def __init__(self):
        self.variables = {}

    # Agregar una variable al scope; lanza error si ya fue declarada
    def agregar(self, nombre, tipo, direccion):
        if nombre in self.variables:
            raise ErrorSemantico(f"Variable '{nombre}' ya fue declarada en el scope")
        self.variables[nombre] = {'tipo': tipo, 'direccion' : direccion}

    # Retorna el diccionario {tipo, direccion} de la variable, o None si no existe    
    def buscar(self, nombre):
        if nombre in self.variables:
            return self.variables[nombre]
        return None

# DIRECTORIO DE FUNCIONES
# Diccionario principal del programa: guarda cada funcion con su tipo
# su tabla de variables, y el indice ERA para GOSUB
# El scope global siempre existe y se inicializa en el constructor
class DirectorioFunciones:
    def __init__(self):
        self.funciones = {}
        self.scope_actual = None
        # Crear scope global como punto de entrada del programa
        self._agregar('global','nula')
        self.scope_actual = 'global'

    # AGREGAR FUNCION (interno)
    # Registra un scope sin variable de retorno (global)
    def _agregar(self, nombre, tipo):
        if nombre in self.funciones:
            raise ErrorSemantico(f"Funcion '{nombre}' ya fue declarada")
        self.funciones[nombre] = {
            'tipo': tipo,
            'variables': TablaVariables()
        }

    # AGREGAR FUNCION (publico)
    # El parser llama esto al encontrar la declaracion de una func
    # Si la funcion retorna valor, registra una var global con su nombre
    # Para guardar el resultado del return
    def agregar_funcion(self, nombre, tipo, memoria):
        if nombre in self.funciones:
            raise ErrorSemantico(f"Funcion '{nombre} ya fue declarada")
        self.funciones[nombre] = {
            'tipo' : tipo,
            'variables': TablaVariables(),
            'indice_era': None # se rellena auto cuando el parser genere ERA
        }
        if tipo != 'nula':
            scope_mem = 'global'
            direccion = memoria.asignar(scope_mem, tipo)
            self.funciones['global']['variables'].agregar(nombre, tipo, direccion)

    # MANEJO DE SCOPE
    # El parser llama a estos metodos al entrar y salir del cuerpo de una funcion
    def entrar_funcion(self, nombre):
        self.scope_actual = nombre

    def salir_funcion(self):
        self.scope_actual = 'global'
    
    # CONSULTA DE FUNCIONES
    def existe_funcion(self, nombre):
        return nombre in self.funciones
    
    # MANEJO DE VARIABLES
    # Agregar una variable a la tabla del scope actual
    def agregar_var(self, nombre, tipo, direccion):
        self.funciones[self.scope_actual]['variables'].agregar(nombre, tipo, direccion)

    # Busca una variable primero en el scope local, luego en el global
    def buscar_variable(self, nombre):
        tipo = self.funciones[self.scope_actual]['variables'].buscar(nombre)
        if tipo is not None:
            return tipo
        if self.scope_actual != 'global':
            tipo = self.funciones['global']['variables'].buscar(nombre)
            if tipo is not None:
                return tipo
        return None
    
    def variable_existe(self, nombre):
        return self.buscar_variable(nombre) is not None

    # MANEJO DE INDICE ERA
    # Guarda en que cuadruplo empieza la funcion para usarlo en GOSUB
    def guardar_indice_era(self, nombre, indice):
        self.funciones[nombre]['indice_era'] = indice

    def obtener_indice_era(self, nombre):
        return self.funciones[nombre]['indice_era']
