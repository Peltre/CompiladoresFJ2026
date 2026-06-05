# quadruples.py | LM: 5/29/2026 | By: Pedro Sotelo
# Generacion de cuadruplos para codigo intermedio.
# Mantiene pilas de operandos, tipos y operadores, y una fila de cuadruplos.

# PRECEDENCIA DE OPERADORES
# Conjuntos usados para comparar la precedencia al momento de meter un operador en la pila

ALTA_PREC = {'*','/'}
BAJA_PREC = {'+','-'}
REL = {'>', '<', '==', '!='}

# GENERADOR DE CUADRUPLOS
# Clase principal que maneja las 3 pilas, y la fila de cuadruplos
# Cada cuadruplo es una tupla: (operador, op1, op2, resultado)
class GeneradorCuadruplos:
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager 
        # Pilas de operandos, tipos y operadores
        self.pila_operandos = []
        self.pila_tipos = []
        self.pila_operadores = []
        # Fila de cuadruplos, "_" representa un campo vacio
        self.cuadruplos = []
        # Contador para numerar los cuadruplos
        self.contador = 0
        # Pila para manejo de saltos condicionales e incondicionales
        self.pila_saltos = []
        # Pila para guardar el inicio de ciclos while
        self.pila_ciclos = []

    # AGREGAR CUADRUPLOS
    # inserta una tupla a la fila y retorna su indice
    def agregar_cuadruplo(self, operador, op1, op2, res):
        self.cuadruplos.append((operador, op1, op2, res))
        self.contador += 1
        return self.contador - 1
    
    # CONTADOR ACTUAL
    # Retorna el indice del proximo cuadruplo (para apuntar saltos)
    def contador_actual(self):
        return len(self.cuadruplos)
    
    # PUSH OPERANDO
    # Mete una variable ya declarada a las pilas (direccion virtual + tipo)
    def push_operando(self, direccion, tipo):
        self.pila_operandos.append(direccion)
        self.pila_tipos.append(tipo)

    # PUSH CONSTANTE
    # Asigna una direccion virtual a la constante y la mete a las pilas
    def push_constante(self, valor, tipo):
        direccion = self.memory_manager.asignar_constante(valor, tipo)
        self.pila_operandos.append(direccion)
        self.pila_tipos.append(tipo)

    # PUSH OPERADOR
    # Mete un operador a la pila respetando precedencia:
    # Antes de meter, resuelve los ops de mayor precedencia pendientes
    def push_operador(self, operador, cubo_semantico):
        if operador in BAJA_PREC or operador in REL:
            while self.pila_operadores and self.pila_operadores[-1] in ALTA_PREC:
                self.generar_operacion(cubo_semantico)
        # Si llega un relacional, resolver primero cualquier aritmetico pendiente
        if operador in REL:
            while self.pila_operadores and self.pila_operadores[-1] in BAJA_PREC:
                self.generar_operacion(cubo_semantico)
        self.pila_operadores.append(operador)

    # RESOLVER PENDIENTES
    # Resuelve todos los operadores pendientes de un conjunto dado
    # Se usa al cerrar parentesis o al terminar una expresion
    def resolver_pendientes(self, operadores_validos, cubo_semantico):
        while self.pila_operadores and self.pila_operadores[-1] in operadores_validos:
            self.generar_operacion(cubo_semantico)

    # GENERAR OPERACION
    # Toma el operador del tope, los 2 operandos, consulta el cubo semantico
    # Y genera el cuadruplo. El resultado queda en un temporal nuevo
    def generar_operacion(self, cubo_semantico):
        operador = self.pila_operadores.pop()
        op_der = self.pila_operandos.pop()
        tipo_der = self.pila_tipos.pop()
        op_izq = self.pila_operandos.pop()
        tipo_izq = self.pila_tipos.pop()
        # Consultar cubo semantico para compatibilidad de tipos
        tipo_resultado = cubo_semantico(tipo_izq, tipo_der, operador)
        if tipo_resultado == 'error':
            print(f"[ERROR SEMANTICO] Operacion incompatible: {tipo_izq} {operador} {tipo_der}")
            return
        # Asginar direccion temporal para el resultado
        dir_temp = self.memory_manager.asignar_temp(tipo_resultado)
        self.agregar_cuadruplo(operador, op_izq, op_der, dir_temp)
        # El resultado se convierte a operando para la siguiente operacion
        self.pila_operandos.append(dir_temp)
        self.pila_tipos.append(tipo_resultado)

    # GENERAR ASIGNACION
    # Toma el valor del tope de la pila y genera cuadruplo de asignacion a dir_destino
    def generar_asignacion(self, dir_destino):
        valor = self.pila_operandos.pop()
        self.pila_tipos.pop()
        self.agregar_cuadruplo('=', valor, '_', dir_destino)

    # MANEJO DE SALTOS CONDICIONALES
    # Genera GOTOF con destino vacio y guarda el indice en pila_saltos para rellenar despues
    def agregar_salto_falso(self):
        condicion = self.pila_operandos.pop()
        self.pila_tipos.pop()
        indice = self.contador_actual()
        self.agregar_cuadruplo('GOTOF',condicion,'_',None)
        self.pila_saltos.append(indice)

    # MANEJO DE SALTOS INCONDICIONALES
    # Genera GOTO con destino vacio y guarda el indice en pila_saltos para rellenar despues
    def agregar_salto_incondicional(self):
        indice = self.contador_actual()
        self.agregar_cuadruplo('GOTO','_','_',None)
        self.pila_saltos.append(indice)

    # RELLENAR SALTO
    # Rellena el destino pendiente de un GOTO o GOTOF dado su indice
    # Reemplaza la tupla completa (pq las tuplas son inmutables)
    def rellenar_salto(self, indice, destino):
        op, op1, op2, _ = self.cuadruplos[indice]
        self.cuadruplos[indice] = (op, op1, op2, destino)

    # MANEJO DE CICLOS
    # Guarda el indice de inicio del ciclo justo antes de evaluar la condicion del while
    def guardar_inicio_ciclo(self):
        self.pila_ciclos.append(self.contador_actual())

    # Genera el GOTO de regreso al inicio y rellena el GOTOF pendiente al cerrar el ciclo
    def cerrar_ciclo(self):
        inicio = self.pila_ciclos.pop()
        self.agregar_cuadruplo('GOTO','_','_',inicio)
        indice_gotof = self.pila_saltos.pop()
        self.rellenar_salto(indice_gotof, self.contador_actual())

    # MANEJO DE FUNCIONES
    # ERA: marca el inicio de la activacion de una funcion (reserva su espacio de memoria)
    def agregar_era(self, nombre_func):
        self.agregar_cuadruplo('ERA',nombre_func,'_','_')
    
    # ENDFUNC: marca el final de ejecucion de una funcion
    def agregar_endfunc(self):
        self.agregar_cuadruplo('ENDFUNC', '_','_','_')

        # PARAM: pasa el valor del tope de la pila a la direccion local del parametro
    # Se genera uno por argumento antes del GOSUB
    def agregar_param(self, dir_param):
        valor = self.pila_operandos.pop()
        self.pila_tipos.pop()
        self.agregar_cuadruplo('PARAM', valor, '_', dir_param)

    # GOSUB: genera la llamada a una funcion, apuntando a su primer cuadruplo
    def agregar_gosub(self, nombre_func, indice_era):
        self.agregar_cuadruplo('GOSUB', nombre_func, indice_era, '_')

    # RETURN: toma el valor del tope de la pila y lo asigna a la variable global de retorno de la funcion
    # y luego cierra la funcion con endfunc
    def agregar_return(self, dir_var_global):
        valor = self.pila_operandos.pop()
        self.pila_tipos.pop()
        self.agregar_cuadruplo('=',valor,'_',dir_var_global)
        self.agregar_endfunc()

    # IMPRIMIR CUADRUPLOS
    # Muestra la fila completa de cuadruplos con formato de tabla
    def imprimir(self):
        print("\n" + "=" * 55)
        print("  CUÁDRUPLOS GENERADOS")
        print("=" * 55)
        print(f"  {'#':<5} {'OP':<6} {'OP1':<8} {'OP2':<8} {'RES':<8}")
        print("-" * 55)
        for i, (op, op1, op2, res) in enumerate(self.cuadruplos):
            print(f"  {i:<5} {str(op):<6} {str(op1):<8} {str(op2):<8} {str(res):<8}")
        print("=" * 55)
    

