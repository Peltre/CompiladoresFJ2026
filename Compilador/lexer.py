import ply.lex as lex

# Palabras reservadas

reserved = {
    'programa' : 'PROGRAMA',
    'inicio': 'INICIO',
    'fin' : 'FIN',
    'vars' : 'VARS',
    'entero' : 'ENTERO',
    'flotante' : 'FLOTANTE',
    'si' : 'SI',
    'sino' : 'SINO',
    'mientras' : 'MIENTRAS',
    'haz' : 'HAZ',
    'escribe' : 'ESCRIBE',
    'nula' : 'NULA',
}

# Lista de tokens
tokens = [
    'ID', 'CTE_ENT', 'CTE_FLOT', 'LETRERO',
    'ASIGNA', 'IGUAL', 'DIFERENTE',
    'SUMA', 'RESTA', 'MULT', 'DIV',
    'MAYOR', 'MENOR',
    'PUNTO_COMA', 'COMA', 'DOS_PUNTOS',
    'PAREN_IZQ', 'PAREN_DER',
    'LLAVE_IZQ', 'LLAVE_DER',
    'CORCHETE_IZQ', 'CORCHETE_DER',
] + list(reserved.values())

# Reglas simples 

t_IGUAL = r'=='
t_DIFERENTE = r'!='
t_ASIGNA = r'='
t_SUMA = r'\+'
t_RESTA = r'\-'
t_MULT = r'\*'
t_DIV = r'\/'
t_MAYOR = r'>'
t_MENOR = r'<'
t_PUNTO_COMA = r';'
t_COMA = r','
t_DOS_PUNTOS = r':'
t_PAREN_IZQ = r'\('
t_PAREN_DER = r'\)'
t_LLAVE_IZQ = r'\{'
t_LLAVE_DER = r'\}'
t_CORCHETE_IZQ = r'\['
t_CORCHETE_DER = r'\]'

# Reglas con funcion