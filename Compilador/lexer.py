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

def t_CTE_FLOT(t):
    r'[0-9]+\.[0-9]+'
    t.value = float(t.value)
    return t

def t_CTE_ENT(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

def t_CADENA(t):
    r'"[^"\n]*"'
    t.value = t.value[1:-1]
    return t

def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID') # revisar si es palabra reservada
    return t

# Ignorados (comentarios y demas)

t_ignore = ' \t\r\n'

def t_COMENTARIO(t):
    r'\/\/[^\n]*'
    pass #descartar token

# Errores
def t_error(t):
    print(f"[LEXICO] Caracter invalido '{t.value[0]}' en linea {t.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()