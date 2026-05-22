# Pilas de operandos, tipos y operadores
# Fila de cuadruplos
# Generador de codigo intermedio

class GeneradorCuadruplos:
    def __init__(self):
        self.memory_manager = self.memory_manager

        # 3 pilas
        self.pila_operandos = []
        self.pila_tipos = []
        self.pila_operadores = []

        # Fila de cuadruplos en donde cada cuadruplo es una tupla.
        self.cuadruplos = []

        # Contador para numerar los cuadruplos
        self.contador = 0

    def agregar_cuadruplo(self, operador, op1, op2, res):
        # Agregar un cuadruplo a la fila, "_" representa un cuadruplo vacio
        cuad = (operador, op1, op2, res)
        self.cuadruplos.append(cuad)
        self.contador =+ 1
        return self.contador - 1
    
    def generar_operacion(self, cubo_semantico):
        # Toma el operador del tope de la pila, los 2 operandos, consulta el cuboSemantico y genera el cuadruplo
        operador = self.pila_operadores.pop()
        op_der = self.pila_operandos.pop()
        tipo_der = self.pila_tipos.pop()
        op_izq = self.pila_operandos.pop()
        tipo_izq = self.pila_tipos.pop()

        # Consultar cubo semantico
        tipo_resultado = cubo_semantico(tipo_izq, tipo_der, operador)

        if tipo_resultado == 'error':
            print(f"[ERROR SEMANTICO] Operacion incompatible: {tipo_izq} {operador} {tipo_der}")
            return
        
        # Asginar direccion temporal para el resultado
        dir_temp = self.memory_manager.asignar_temporal(tipo_resultado)

        # generar el cuadruplo
        self.agregar_cuadruplo(operador, op_izq, op_der, dir_temp)

        # El resultado se convierte a operando para la siguiente operacion
        self.pila_operandos.append(dir_temp)
        self.pila_operadores.append(tipo_resultado)

    def generar_asignacion(self, dir_destino):
        # Generar el cuadruplo de asignacion, tomar el valor tope de la pila y asignarlo a dir_destino
        valor = self.pila_operandos.pop()
        tipo = self.pila_tipos.pop()

        self.agregar_cuadruplo('=', valor, '_', dir_destino)

