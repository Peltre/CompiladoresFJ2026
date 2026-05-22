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

    # Manejo de operadores con precedencia

    ALTA_PREC = {'*','/'}
    BAJA_PREC = {'+','-'}
    REL = {'>', '<', '==', '!='}

    def push_operador(self, operador, cubo_semantico):
        # Mete un operador a la pila, pero antes de meterlo resuelve los operadores de mayor precedencia pendientes
        if operador in self.BAJA_PREC or operador in self.REL:
            while self.pila_operadores and self.pila_operadores[-1] in self.ALTA_PREC:
                self.generar_operacion(cubo_semantico)

        # Si llega un relacional, resolver primero cualquier aritmetico pendiente
        if operador in self.REL:
            while self.pila_operadores and self.pila_operadores[-1] in self.BAJA_PREC:
                self.generar_operacion(cubo_semantico)

        self.pila_operadores.append(operador)

    def resolver_pendientes(self, operadores_validos, cubo_semantico):
        # Resolver todos los operadores pendientes de un conjunto dado (al cerrar parentesis o terminar exp)
        while self.pila_operadores and self.pila_operadores[-1] in operadores_validos:
            self.generar_operacion(cubo_semantico)

    def push_operando(self, direccion, tipo):
        # Mete un operando a la pila (var ya declarada)
        self.pila_operandos.append(direccion)
        self.pila_tipos.append(tipo)

    def push_constante(self, valor, tipo):
        # Mete una constante a la pila, pero primero le asgigna una direccion virtual
        direccion = self.memory_manager.asignar_constante(valor, tipo)
        self.pila_operandos.append(direccion)
        self.pila_tipos.append(tipo)

    def imprimir(self):
        print("\n" + "=" * 55)
        print("  CUÁDRUPLOS GENERADOS")
        print("=" * 55)
        print(f"  {'#':<5} {'OP':<6} {'OP1':<8} {'OP2':<8} {'RES':<8}")
        print("-" * 55)
        for i, (op, op1, op2, res) in enumerate(self.cuadruplos):
            print(f"  {i:<5} {str(op):<6} {str(op1):<8} {str(op2):<8} {str(res):<8}")
        print("=" * 55)

            