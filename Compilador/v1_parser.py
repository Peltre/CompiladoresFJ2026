# v1_parser.py | LM: 5/29/2026 | By: Pedro Sotelo
# Parser del compilador. Define la gramatica del lenguaje y las acciones
# semanticas que generan cuadruplos durante el analisis sintactico.

import ply.yacc as yacc
from v1_lexer import tokens
from symbol_table import DirectorioFunciones, ErrorSemantico
from semantic_cube import tipo_resultado
from memory_manager import ManejoMemoria
from quadruples import GeneradorCuadruplos

# ESTRUCTURAS GLOBALES
# Se inicializan una sola vez y son compartidas por todas las reglas
directorio = DirectorioFunciones()
memoria = ManejoMemoria()
generador = GeneradorCuadruplos(memoria)

# Bandera global para acumular errores sin detener el analisis
hay_error_semantico = False

# Lista auxiliar para acumular IDs antes de conocer tipo en lista_vars
_ids_pendientes = []

# ===========================================================================
# PROGRAMA
# ===========================================================================

def p_programa(p):
    'programa : PROGRAMA ID PUNTO_COMA vars funcs INICIO cuerpo FIN'
    if not hay_error_semantico:
        print("[OK] Programa valido")
        generador.imprimir()
    else:
        print("[ERROR SEMANTICO] El programa contiene errores semanticos")

# ===========================================================================
# VARIABLES
# ===========================================================================

def p_vars(p):
    '''vars : VARS lista_vars
            | empty'''

# Soporta una o varias lineas de declaracion: ID, ID : tipo ;
def p_lista_vars(p):
    '''lista_vars : ID mas_ids DOS_PUNTOS tipo PUNTO_COMA
                  | lista_vars ID mas_ids DOS_PUNTOS tipo PUNTO_COMA'''
    # La pos del primer ID y del tipo cambia segun alternativa usada
    if len(p) == 6:
        primer_id = p[1]
        tipo      = p[4]
    else:
        primer_id = p[2]
        tipo      = p[5]
    # Incluir el primer ID junto a los acumulados en ids_pendientes
    _ids_pendientes.insert(0, primer_id)
    for nombre in _ids_pendientes:
        try:
            # Asignar direccion virtual y pasar memoria al registrar variable
            scope_mem = 'global' if directorio.scope_actual == 'global' else 'local'
            direccion = memoria.asignar(scope_mem, tipo)
            directorio.agregar_var(nombre, tipo, direccion)
        except ErrorSemantico as e:
            global hay_error_semantico
            hay_error_semantico = True
            print(e)
    _ids_pendientes.clear()

# Acumular IDs adicionales separados paor coma en la lista auxiliar
def p_mas_ids_multiple(p):
    'mas_ids : COMA ID mas_ids'
    _ids_pendientes.append(p[2])

def p_mas_ids_vacio(p):
    'mas_ids : empty'

# Propaga el tipo hacia arriba para que lista_vars lo reciba     
def p_tipo(p):
    '''tipo : ENTERO
            | FLOTANTE'''
    p[0] = p[1] 
    
# ===========================================================================
# FUNCIONES
# ===========================================================================

# Marker que se reduce justo cuando se ve el ID, antes del resto del header
def p_func_nombre(p):
    'func_nombre : ID'
    nombre = p[1]
    p[0] = nombre

# Header de la funcion con tipo de retorno
# Registra la funcion, genera ERA y GOTO de salto antes de entrar al cuerpo
def p_func_header_tipo(p):
    'func_header : func_nombre PAREN_IZQ tipo PAREN_DER'
    nombre = p[1]
    tipo = p[3]
    p[0] = None # marca de fallo por default
    try:
        directorio.agregar_funcion(nombre, tipo, memoria)
        # Generar GOTO para saltar la func al ejecutar
        generador.agregar_salto_incondicional()
        # Generar ERA y guardar indice
        indice_era = generador.contador_actual()
        generador.agregar_era(nombre)
        directorio.guardar_indice_era(nombre, indice_era)
        directorio.entrar_funcion(nombre)
        p[0] = nombre # Marca de exito
    except ErrorSemantico as e:
        global hay_error_semantico
        hay_error_semantico = True
        print(e)

# Header de funcion sin retorno
def p_func_header_nula(p):
    'func_header : func_nombre PAREN_IZQ NULA PAREN_DER'
    nombre = p[1]
    p[0] = None # marca de fallo por default
    try:
        directorio.agregar_funcion(nombre, 'nula', memoria)
        generador.agregar_salto_incondicional()
        indice_era = generador.contador_actual()
        generador.agregar_era(nombre)
        directorio.guardar_indice_era(nombre, indice_era)
        directorio.entrar_funcion(nombre)
        p[0] = nombre # Marca de exito
    except ErrorSemantico as e:
        global hay_error_semantico
        hay_error_semantico = True
        print(e)

# Cuerpo completo de una funcion
# Al cerrar genera ENDFUNC y rellena el GOTO que la saltaba
def p_funcs_func(p):
    'funcs : funcs func_header LLAVE_IZQ vars cuerpo LLAVE_DER PUNTO_COMA'
    generador.agregar_endfunc()
    # Solo hacer pop si el header se registro correctamente
    if p[2] is not None:
        indice_goto = generador.pila_saltos.pop()
        generador.rellenar_salto(indice_goto, generador.contador_actual())
    directorio.salir_funcion()

def p_funcs_empty(p):
    'funcs : empty'
    pass

# ===========================================================================
# CUERPO Y ESTATUTOS
# ===========================================================================

def p_cuerpo(p):
    '''cuerpo : estatuto
              | cuerpo estatuto
              | empty'''
              
def p_estatuto(p):
    '''estatuto : asigna
                | condicion
                | ciclo
                | imprime
                | llamada PUNTO_COMA
                | retorna'''
    
# RETURN
# Busca la variable global que guarda el retorno y genera el cuadruplo 
def p_retorna(p):
    'retorna : REGRESA expresion PUNTO_COMA'
    nombre_func = directorio.scope_actual
    info = directorio.buscar_variable(nombre_func)
    if info is None:
        print(f"[ERROR SEMANTICO] La funcion '{nombre_func}' es nula, no puede retornar un valor")
        return
    # En caso de que no sea nula, generar cuadruplos de return
    generador.agregar_return(info['direccion'])

# ===========================================================================
# ASIGNACION
# ===========================================================================

def p_asigna(p):
    'asigna : ID ASIGNA expresion PUNTO_COMA'
    nombre = p[1]
    info = directorio.buscar_variable(nombre)
    if info is None:
        global hay_error_semantico
        hay_error_semantico = True
        print(f"[ERROR SEMANTICO] Variable '{nombre}' no declarada (linea {p.lineno(1)})")
        return
    # Generar cuadruplo de asignacion
    generador.generar_asignacion(info['direccion'])

# ===========================================================================
# IMPRESION
# ===========================================================================

def p_imprime(p):
    'imprime : ESCRIBE PAREN_IZQ imp_lista PAREN_DER PUNTO_COMA'

def p_imp_lista(p):
    '''imp_lista : expresion
                 | CADENA
                 | imp_lista COMA expresion
                 | imp_lista COMA CADENA'''

# ===========================================================================
# CONDICIONALES
# ===========================================================================

# IF header: evalua la condicion y genera GOTOF con destino pendiente
def p_si_header(p):
    'si_header : SI PAREN_IZQ expresion PAREN_DER'
    generador.agregar_salto_falso()

# IF sin ELSE: rellena el GOTOF al terminar el cuerpo
def p_condicion_simple(p):
    'condicion : si_header CORCHETE_IZQ cuerpo CORCHETE_DER'
    indice_gotof = generador.pila_saltos.pop()
    generador.rellenar_salto(indice_gotof, generador.contador_actual())

# ELSE header: genera GOTO para saltar el bloque si la condicion es true,
# Luego rellena el GOTOF del IF para que apunte aqui
def p_sino_header(p):
    'sino_header : SINO'
    generador.agregar_salto_incondicional()
    indice_goto = generador.pila_saltos.pop() # GOTO recien generado
    indice_gotof = generador.pila_saltos.pop() # GOTOF del IF
    generador.rellenar_salto(indice_gotof, generador.contador_actual())
    generador.pila_saltos.append(indice_goto) # Devolver el GOTO para rellenarlo al final

# IF con ELSE: rellena el GOTO al terminar el bloque else
def p_condicion_sino(p):
    'condicion : si_header CORCHETE_IZQ cuerpo CORCHETE_DER sino_header CORCHETE_IZQ'
    indice_goto = generador.pila_saltos.pop()
    generador.rellenar_salto(indice_goto, generador.contador_actual())


# ===========================================================================
# CICLO WHILE
# ===========================================================================

# Guarda el indice de inicio ANTES de evaluar la condicion
def p_mientras_header(p):
    'mientras_header : MIENTRAS'
    generador.guardar_inicio_ciclo()

# Evalua la condicion y genera GOTOF pendiente
def p_mientras_cond(p):
    'mientras_cond : mientras_header PAREN_IZQ expresion PAREN_DER'
    generador.agregar_salto_falso()

# Cierra el ciclo: genera GOTO al inicio y rellena el GOTOF
def p_ciclo(p):
    'ciclo : mientras_cond HAZ CORCHETE_IZQ cuerpo CORCHETE_DER PUNTO_COMA'
    generador.cerrar_ciclo()

# ===========================================================================
# LLAMADA A FUNCION
# ===========================================================================

def p_llamada(p):
    'llamada : ID PAREN_IZQ args PAREN_DER'
    nombre = p[1]
    if not directorio.existe_funcion(nombre):
        global hay_error_semantico
        hay_error_semantico = True
        print(f"[ERROR SEMANTICO] Funcion '{nombre}' no declarada (linea {p.lineno(1)})")
        return
    # generar GOSUB
    indice_era = directorio.obtener_indice_era(nombre)
    generador.agregar_gosub(nombre, indice_era)

def p_args(p):
    '''args : expresion
            | args COMA expresion
            | empty'''

# ===========================================================================
# EXPRESIONES
# ===========================================================================

# Nivel 3: operadores relacionales
def p_expresion(p):
    '''expresion : exp
                 | exp mayor_op exp
                 | exp menor_op exp
                 | exp igual_op exp
                 | exp diferente_op exp'''
    generador.resolver_pendientes({'>','<','==','!='}, tipo_resultado)
    p[0] = p[1]

# Nivel 2: suma y resta
def p_exp(p):
    '''exp : termino
           | exp suma_op termino
           | exp resta_op termino'''
    # Al terminar exp, resolver + y - pendientes
    generador.resolver_pendientes({'+','-'}, tipo_resultado)

# Nivel 1: multiplicacion y division
def p_termino(p):
    '''termino : factor
               | termino mult_op factor
               | termino div_op factor'''
    # Al terminar un termino, resolver * y / pendientes
    generador.resolver_pendientes({'*','/'}, tipo_resultado)

# OPERADORES (cada uno mete un operador a la pila antes de parsear el siguiente operando)
def p_suma_op(p):
    'suma_op : SUMA'
    generador.push_operador('+', tipo_resultado)

def p_resta_op(p):
    'resta_op : RESTA'
    generador.push_operador('-', tipo_resultado)

def p_mult_op(p):
    'mult_op : MULT'
    generador.push_operador('*', tipo_resultado)

def p_div_op(p):
    'div_op : DIV'
    generador.push_operador('/', tipo_resultado)

def p_mayor_op(p):
    'mayor_op : MAYOR'
    generador.push_operador('>', tipo_resultado)

def p_menor_op(p):
    'menor_op : MENOR'
    generador.push_operador('<', tipo_resultado)

def p_igual_op(p):
    'igual_op : IGUAL'
    generador.push_operador('==', tipo_resultado)

def p_diferente_op(p):
    'diferente_op : DIFERENTE'
    generador.push_operador('!=', tipo_resultado)

# ===========================================================================
# FACTORES
# ===========================================================================

# Parentesis: agrupan sin generar cuadruplos
def p_factor_paren(p):
    'factor : PAREN_IZQ expresion PAREN_DER'
    pass

# Signo positivo: no cambia nada
def p_factor_signo_pos(p):
    'factor : SUMA cte'
    pass 

# Signo negativo: multiplica la constante por -1
def p_factor_signo_neg(p):
    'factor : RESTA cte'
    # Generar cuadruplo de negacion
    dir_menos1 = memoria.asignar_constante(-1, 'entero')
    op = generador.pila_operandos.pop()
    tip = generador.pila_tipos.pop()
    dir_temp = memoria.asignar_temp(tip)
    generador.agregar_cuadruplo('*', dir_menos1, op, dir_temp)
    generador.pila_operandos.append(dir_temp)
    generador.pila_tipos.append(tip)

def p_factor_cte(p):
    'factor : cte'
    pass # cte ya metio el operando a la pila

# Variable: busca la direccion virtual y la mete a la pila
def p_factor_id(p):
    'factor : ID'
    nombre = p[1]
    info = directorio.buscar_variable(nombre)
    if info is None:
        global hay_error_semantico
        hay_error_semantico = True
        print(f"[ERROR SEMANTICO] Variable '{nombre}' no declarada")
        return 
    generador.push_operando(info['direccion'], info['tipo'])

# CONSTANTES
# Asignan direccion virtual y meten el valor a la pila de operandos
def p_cte_ent(p):
    'cte : CTE_ENT'
    direccion = memoria.asignar_constante(p[1], 'entero')
    generador.push_operando(direccion, 'entero')
    p[0] = p[1]

def p_cte_flot(p):
    'cte : CTE_FLOT'
    direccion = memoria.asignar_constante(p[1], 'flotante')
    generador.push_operando(direccion, 'flotante')
    p[0] = p[1]

# ===========================================================================
# UTILIDADES
# ===========================================================================

# Epsilon (vació)
def p_empty(p):
    'empty :'
    pass

# Error de sintaxis
def p_error(p):
    if p:
        global hay_error_semantico
        hay_error_semantico = True
        print(f"[SINTAXIS] Token inesperado '{p.value}' en linea {p.lineno}")
    else:
        print("[SINTAXIS] Error: fin de archivo inesperado")

# Construir el parser
parser = yacc.yacc()