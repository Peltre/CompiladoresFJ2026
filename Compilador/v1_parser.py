import ply.yacc as yacc
from v1_lexer import tokens

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
    
def p_mas_ids(p):
    '''mas_ids : COMA ID mas_ids
               | empty'''
    
def p_tipo(p):
    '''tipo : ENTERO
            | FLOTANTE'''
    
# Funciones
def p_funcs(p):
    '''funcs : funcs ID PAREN_IZQ tipo PAREN_DER LLAVE_IZQ vars cuerpo LLAVE_DER PUNTO_COMA
             | funcs ID PAREN_IZQ NULA PAREN_DER LLAVE_IZQ vars cuerpo LLAVE_DER PUNTO_COMA
             | empty'''
    
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