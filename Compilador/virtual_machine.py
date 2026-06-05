# virtual_machine.py | LM: 6/4/2026 | By: Pedro Sotelo
# Maquina virtual para ejecutar el codigo intermedio generado por el compilador.
# Lee los cuadruplos y ejecuta las operaciones correspondientes, manejando la memoria virtual

class MaquinaVirtual:
    def __init__(self, cuadruplos, tabla_constantes):
        # Fila de cuadruplos generada por el compilador
        self.cuadruplos = cuadruplos

        # Contador de programa: indica que cuadruplo se esta ejecutando
        self.PC = 0

        # Memoria de ejecucion
        # Diccionario { direccion_virtual -> valor}
        # Las direcciones virtuales del compilador se usan directamente como indices, sin ninguna traduccion adicional
        self.memoria = {}

        # Cargar constantes en la memoria desde la tabla del compilador
        # tabla_constantes tiene la forma { (valor, tipo) -> direccion }
        for (valor, tipo), direccion in tabla_constantes.items():
            self.memoria[direccion] = valor

        # Pila de ejecucion para llamadas a funciones
        self.pila_llamadas = []

        # ACCESO DE MEMORIA
    def leer(self, direccion):
        # Retorna el valor almacenado en una direccion virtual
        # Si la direccion no tiene valor, retorna 0
        if direccion == '_':
            return None
        return self.memoria.get(direccion, 0)
        
    def escribir(self, direccion, valor):
        # Almacenar un valor en una direccion virtual
        if direccion == '_':
            return
        self.memoria[direccion] = valor

    # EJECUCION
    def ejecutar(self):
        # Ciclo principal: ejecuta los cuadruplos 1x1 hasta terminar
        while self.PC < len(self.cuadruplos):
            cuad = self.cuadruplos[self.PC]
            op, op1, op2, res = cuad
            self.ejecutar_cuadruplo(op, op1, op2, res)

    def ejecutar_cuadruplo(self, op, op1, op2, res):
        # Despacha cada cuadruplo con su operacion correspondiente

        # Asignacion
        if op == '=':
            valor = self.leer(op1)
            self.escribir(res, valor)
            self.PC += 1

        # Artimeticos
        elif op == '+':
            self.escribir(res, self.leer(op1) + self.leer(op2))
            self.PC += 1
        elif op == '-':
            self.escribir(res, self.leer(op1) - self.leer(op2))
            self.PC += 1
        elif op == '*':
            self.escribir(res, self.leer(op1) * self.leer(op2))
            self.PC += 1
        elif op == '/':
            if self.leer(op2) == 0:
                raise ZeroDivisionError(f"[ERROR EN EJECUCION] Division entre cero")
            self.escribir(res, self.leer(op1) / self.leer(op2))
            self.PC += 1

        # Relacionales
        # El resultado es 1 true 0 false
        elif op == '>':
            self.escribir(res, int(self.leer(op1) > self.leer(op2)))
            self.PC += 1
        elif op == '<':
            self.escribir(res, int(self.leer(op1) < self.leer(op2)))
            self.PC += 1
        elif op == '==':
            self.escribir(res, int(self.leer(op1) == self.leer(op2)))
            self.PC += 1
        elif op == '!=':
            self.escribir(res, int(self.leer(op1) != self.leer(op2)))
            self.PC += 1

        # Saltos
        elif op == 'GOTO':
            # Salto incondicional: mover el PC al destino
            self.PC = res
        elif op == 'GOTOF':
            # Salto si falso: si la condicion es 0, saltar al destino
            condicion = self.leer(op1)
            if condicion == 0:
                self.PC = res
            else:
                self.PC += 1

        # Impresion
        elif op == 'ESCRIBE':
            print(self.leer(op1), end='')
            self.PC += 1
        elif op == 'ESCRIBE_NL':
            print()
            self.PC += 1

        # Funciones
        elif op == 'ERA':
        # Preparar el contexto de la funcion, por ahora solo avanzar
            self.PC += 1

        elif op == 'GOSUB':
            # Guardar el PC de retorno en la pila de llamadas
            # op2 es el indice del ERA donde empieza la funcion
            self.pila_llamadas.append(self.PC + 1)
            self.PC = op2

        elif op == 'ENDFUNC':
            # Recuperar el PC de retorno y regresar
            if self.pila_llamadas:
                self.PC = self.pila_llamadas.pop()
            else:
                # Si la pila esta vacia, terminar ejecucion
                self.PC = len(self.cuadruplos)

        elif op == 'REGRESA':
            # El valor ya fue asignado a la var global por el compilador
            # Solo necesitamos regresar como ENDFUNC
            if self.pila_llamadas:
                self.PC = self.pila_llamadas.pop()
            else:
                self.PC = len(self.cuadruplos)

        else:
            print(f"[ERROR EN EJECUCION] Operacion desconocida: {op}")
            self.PC += 1

