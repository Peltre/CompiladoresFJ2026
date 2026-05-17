import ply.yacc as yacc
from v1_lexer import tokens
from symbol_table import DirectorioFunciones, ErrorSemantico

# Definir estructuras globales
directorio = DirectorioFunciones()

# Lista auxiliar para acumular ids antes de conocer tipo
_ids_pendientes = []

# Programa principal
def p_programa(p):
    'programa : PROGRAMA ID PUNTO_COMA vars funcs INICIO cuerpo FIN'
    print("[OK] Programa valido")

# Variables 
def p_vars(p):
    '''vars : VARS lista_vars
            | empty'''
    
def p_lista_vars(p):
    '''lista_vars : ID mas_ids DOS_PUNTOS tipo PUNTO_COMA
                  | lista_vars ID mas_ids DOS_PUNTOS tipo PUNTO_COMA'''
    
    # Identificar el tipo (en este caso su posicion siempre es 4 o 5)
    tipo = p[4] if len(p) == 6 else p[5]

    for nombre in _ids_pendientes:
        try:
            directorio.agregar_var(nombre, tipo)
        except ErrorSemantico as e:
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
        directorio.agregar_funcion(nombre, tipo)
        directorio.entrar_funcion(nombre)
    except ErrorSemantico as e:
        print(e)

def p_func_header_nula(p):
    'func_header : ID PAREN_IZQ NULA PAREN_DER'
    nombre = p[1]
    try:
        directorio.agregar_funcion(nombre, 'nula')
        directorio.entrar_funcion(nombre)
    except ErrorSemantico as e:
        print(e)

def p_funcs_func(p):
    'funcs : funcs func_header LLAVE_IZQ vars cuerpo LLAVE_DER PUNTO_COMA'
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
                | llamada PUNTO_COMA'''
    
# Asignación
def p_asigna(p):
    'asigna : ID ASIGNA expresion PUNTO_COMA'
    nombre = p[1]
    if not directorio.variable_existe(nombre):
        print(f"[ERROR SEMANTICO] Variable '{nombre}' no declarada (linea {p.lineno(1)})")

# Impresion
def p_imprime(p):
    'imprime : ESCRIBE PAREN_IZQ imp_lista PAREN_DER PUNTO_COMA'

def p_imp_lista(p):
    '''imp_lista : expresion
                 | CADENA
                 | imp_lista COMA expresion
                 | imp_lista COMA CADENA'''

# Condición 
def p_condicion(p):
    '''condicion : SI PAREN_IZQ expresion PAREN_DER CORCHETE_IZQ cuerpo CORCHETE_DER
                 | SI PAREN_IZQ expresion PAREN_DER CORCHETE_IZQ cuerpo CORCHETE_DER SINO CORCHETE_IZQ cuerpo CORCHETE_DER'''

# Ciclo
def p_ciclo(p):
    'ciclo : MIENTRAS PAREN_IZQ expresion PAREN_DER HAZ CORCHETE_IZQ cuerpo CORCHETE_DER PUNTO_COMA'

# Llamada
def p_llamada(p):
    'llamada : ID PAREN_IZQ args PAREN_DER'
    nombre = p[1]
    if not directorio.existe_funcion(nombre):
        print(f"[ERROR SEMANTICO] Funcion '{nombre}' no declarada (linea {p.lineno(1)})")

def p_args(p):
    '''args : expresion
            | args COMA expresion
            | empty'''
    
# Expresiones
def p_expresion(p):
    '''expresion : exp
                 | exp MAYOR exp
                 | exp MENOR exp
                 | exp IGUAL exp
                 | exp DIFERENTE exp'''

def p_exp(p):
    '''exp : termino
           | exp SUMA termino
           | exp RESTA termino'''

def p_termino(p):
    '''termino : factor
               | termino MULT factor
               | termino DIV factor'''

def p_factor(p):
    '''factor : PAREN_IZQ expresion PAREN_DER
              | SUMA cte
              | RESTA cte
              | cte
              | ID'''
    # Filtrado de factores posibles para caso de (ID) y verificar existencia
    if len(p) == 2 and isinstance(p[1], str):
        nombre = p[1]
        if not directorio.variable_existe(nombre):
            print(f"[ERROR SEMANTICO] Variable '{nombre}' no declarada")

def p_cte(p):
    '''cte : CTE_ENT
           | CTE_FLOT'''

# Epsilon (vació)
def p_empty(p):
    'empty :'
    pass

# Error de sintaxis
def p_error(p):
    if p:
        print(f"[SINTAXIS] Token inesperado '{p.value}' en linea {p.lineno}")
    else:
        print("[SINTAXIS] Error: fin de archivo inesperado")

parser = yacc.yacc()