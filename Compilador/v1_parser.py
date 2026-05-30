import ply.yacc as yacc
from v1_lexer import tokens
from symbol_table import DirectorioFunciones, ErrorSemantico
from semantic_cube import tipo_resultado
from memory_manager import ManejoMemoria
from quadruples import GeneradorCuadruplos

# Definir estructuras globales
directorio = DirectorioFunciones()
memoria = ManejoMemoria()
generador = GeneradorCuadruplos(memoria)

# Variable global para controlar errores de semantica
hay_error_semantico = False

# Lista auxiliar para acumular ids antes de conocer tipo
_ids_pendientes = []



# Programa principal
def p_programa(p):
    'programa : PROGRAMA ID PUNTO_COMA vars funcs INICIO cuerpo FIN'
    if not hay_error_semantico:
        print("[OK] Programa valido")
        generador.imprimir()
    else:
        print("[ERROR SEMANTICO] El programa contiene errores semanticos")

# Variables 
def p_vars(p):
    '''vars : VARS lista_vars
            | empty'''
    
def p_lista_vars(p):
    '''lista_vars : ID mas_ids DOS_PUNTOS tipo PUNTO_COMA
                  | lista_vars ID mas_ids DOS_PUNTOS tipo PUNTO_COMA'''
    
    # Guardar correctamente el tipo dependinendo de la posicion
    if len(p) == 6:
        primer_id = p[1]
        tipo      = p[4]
    else:
        primer_id = p[2]
        tipo      = p[5]

    # Agregar a ids pendientes
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
    
def p_mas_ids_multiple(p):
    'mas_ids : COMA ID mas_ids'
    # Acumular el id encontrado
    _ids_pendientes.append(p[2])

def p_mas_ids_vacio(p):
    'mas_ids : empty'
            
    
def p_tipo(p):
    '''tipo : ENTERO
            | FLOTANTE'''
    p[0] = p[1] # propagar el tipo hacia arriba para que lista vars lo vea
    
# Funciones
# Separadas en 2 reglas, header y el cuerpo completo, esto para poder realizar acciones antes
# de ejecutar el cuerpo

def p_func_header_tipo(p):
    'func_header : ID PAREN_IZQ tipo PAREN_DER'
    nombre = p[1]
    tipo = p[3]
    try:
        directorio.agregar_funcion(nombre, tipo, memoria)
        # Generar GOTO para saltar la func al ejecutar
        generador.agregar_salto_incondicional()
        # Generar ERA y guardar indice
        indice_era = generador.contador_actual()
        generador.agregar_era(nombre, indice_era)
        directorio.entrar_funcion(nombre)
    except ErrorSemantico as e:
        global hay_error_semantico
        hay_error_semantico = True
        print(e)

def p_func_header_nula(p):
    'func_header : ID PAREN_IZQ NULA PAREN_DER'
    nombre = p[1]
    try:
        directorio.agregar_funcion(nombre, 'nula', memoria)
        generador.agregar_salto_incondicional()
        indice_era = generador.contador_actual()
        generador.agregar_era(nombre, indice_era)
        directorio.entrar_funcion(nombre)
    except ErrorSemantico as e:
        print(e)

def p_funcs_func(p):
    'funcs : funcs func_header LLAVE_IZQ vars cuerpo LLAVE_DER PUNTO_COMA'
    # Generar ENDFUNC al cerrar funcion
    generador.agregar_endfunc()
    # Rellenar el GOTO que saltaba la func
    indice_goto = generador.pila_saltos.pop()
    generador.rellenar_salto(indice_goto, generador.contador_actual())
    directorio.salir_funcion()

def p_funcs_empty(p):
    'funcs : empty'
    pass

# Cuerpo
def p_cuerpo(p):
    '''cuerpo : estatuto
              | cuerpo estatuto
              | empty'''
              

# Estatuto
def p_estatuto(p):
    '''estatuto : asigna
                | condicion
                | ciclo
                | imprime
                | llamada PUNTO_COMA
                | retorna'''
    
def p_retorna(p):
    'retorna : REGRESA expresion PUNTO_COMA'
    # Buscar la variable global que guarda el retorno de la func actual
    nombre_func = directorio.scope_actual
    info = directorio.buscar_variable(nombre_func)
    if info is None:
        print(f"[ERROR SEMANTICO] La funcion '{nombre_func}' es nula, no puede retornar un valor")
        return
    # En caso de que no sea nula, generar cuadruplos de return
    generador.agregar_return(info['direccion'])

# Asignación
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

# Impresion
def p_imprime(p):
    'imprime : ESCRIBE PAREN_IZQ imp_lista PAREN_DER PUNTO_COMA'

def p_imp_lista(p):
    '''imp_lista : expresion
                 | CADENA
                 | imp_lista COMA expresion
                 | imp_lista COMA CADENA'''

# Condicionales
def p_si_header(p):
    'si_header : SI PAREN_IZQ expresion PAREN_DER'
    # La condicion ya esta en la pila, genera GOTOF con destino pendiente
    generador.agregar_salto_falso()

# if SOLO (no else)
def p_condicion_simple(p):
    'condicion : si_header CORCHETE_IZQ cuerpo CORCHETE_DER'
    # Rellenar el GOTOF con el indice actual (despues del cuerpo)
    indice_gotof = generador.pila_saltos.pop()
    generador.rellenar_salto(indice_gotof, generador.contador_actual())

# ELSE header
def p_sino_header(p):
    'sino_header : SINO'
    # Antes de entrar al else, generar GOTO para saltar el bloque else si era vd
    generador.agregar_salto_incondicional()
    # Rellenar el GOTOF del if (que apunta aqui)
    # el GOTO recienb generado queda en pila saltos [-1]
    # el GOTOF original queda en pila saltos [-2]
    indice_goto = generador.pila_saltos.pop()
    indice_gotof = generador.pila_saltos.pop()
    generador.rellenar_salto(indice_gotof, generador.contador_actual())
    generador.pila_saltos.append(indice_goto) # Devolver el GOTO para rellenarlo al final

# ELSE body
def p_condicion_sino(p):
    'condicion : si_header CORCHETE_IZQ cuerpo CORCHETE_DER sino_header CORCHETE_IZQ'
    # Rellenar el GOTO del if con el indice actual (despues del else)
    indice_goto = generador.pila_saltos.pop()
    generador.rellenar_salto(indice_goto, generador.contador_actual())

# CICLO WHILE
def p_mientras_header(p):
    # Guardar el indice actual como inicio del ciclo
    # se llama antes de evaluar la condicion
    generador.guardar_inicio_ciclo()

def p_mientras_cond(p):
    'mientas_cond : mientras_header PAREN_IZQ expresion PAREN_DER'
    # la condicion ya esta evaluada, generar GOTOF
    generador.agregar_salto_falso()

def p_ciclo(p):
    'ciclo : mientras_cond PAREN_IZQ expresion HAZ CORCHETE_IZQ cuerpo CORCHETE_DER PUNTO_COMA'
    # Generar GOTO de regreso y rellenar GOTOF pendiente
    generador.cerrar_ciclo()

# Llamada
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
    
# Expresiones
def p_expresion(p):
    '''expresion : exp
                 | exp mayor_op exp
                 | exp menor_op exp
                 | exp igual_op exp
                 | exp diferente_op exp'''
    # Al terminar la expresion, resolver operadores relacionales pendientes
    generador.resolver_pendientes({'>','<','==','!='}, tipo_resultado)
    p[0] = p[1]

def p_exp(p):
    '''exp : termino
           | exp suma_op termino
           | exp resta_op termino'''
    # Al terminar exp, resolver + y - pendientes
    generador.resolver_pendientes({'+','-'}, tipo_resultado)

def p_termino(p):
    '''termino : factor
               | termino mult_op factor
               | termino div_op factor'''
    # Al terminar un termino, resolver * y / pendientes
    generador.resolver_pendientes({'*','/'}, tipo_resultado)

def p_suma_op(p):
    'suma_op : SUMA'
    # Semantic action: meter + a la pila de operadores
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

def p_factor_paren(p):
    'factor : PAREN_IZQ expresion PAREN_DER'
    # los parentesis no generan cuadruplos, solo agrupan
    pass

def p_factor_signo_pos(p):
    'factor : SUMA cte'
    pass # signo positivo no cambia nada

def p_factor_signo_neg(p):
    'factor : RESTA cte'
    # Generar cuadruplo de negacion
    dir_menos1 = memoria.asignar_constante(-1, 'entero')
    op = generador.pila_operandos.pop()
    tip = generador.pila_tipos.pop()
    dir_temp = memoria.asignar_temporal(tip)
    generador.agregar_cuadruplo('*', dir_menos1, op, dir_temp)
    generador.pila_operandos.append(dir_temp)
    generador.pila_tipos.append(tip)

def p_factor_cte(p):
    'factor : cte'
    pass # cte ya metio el operando a la pila

def p_factor_id(p):
    'factor : ID'
    nombre = p[1]
    info = directorio.buscar_variable(nombre)
    if info is None:
        global hay_error_semantico
        hay_error_semantico = True
        print(f"[ERROR SEMANTICO] Variable '{nombre}' no declarada")
        return 
    # Meter la direccion virtual del ID a la pila
    generador.push_operando(info['direccion'], info['tipo'])

def p_cte_ent(p):
    'cte : CTE_ENT'
    # Asignar direccion a la constante y meter a la pila
    direccion = memoria.asignar_constante(p[1], 'entero')
    generador.push_operando(direccion, 'entero')
    p[0] = p[1]

def p_cte_flot(p):
    'cte : CTE_FLOT'
    direccion = memoria.asignar_constante(p[1], 'flotante')
    generador.push_operando(direccion, 'flotante')
    p[0] = p[1]


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

parser = yacc.yacc()