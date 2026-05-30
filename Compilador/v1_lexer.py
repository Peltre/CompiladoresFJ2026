# v1_lexer.py | LM: 5/29/2026 | By: Pedro Sotelo
# Analizador lexico del compilador.
# Tokeniza el codigo fuente en palabras reservadas, identificadores,
# constantes, operadores y simbolos de puntuacion.
import ply.lex as lex

states = (
    ('invars', 'exclusive'),
)

# PALABRAS RESERVADAS
# Mapa de string -> nombre de token para detectarlas dentro de t_ID
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
    'regresa' : 'REGRESA',
}

# LISTA DE TOKENS
# Todos los tokens que el lexer puede producir
tokens = [
    'ID', 'ID_VAR', 'CTE_ENT', 'CTE_FLOT', 'CADENA',
    'ASIGNA', 'IGUAL', 'DIFERENTE',
    'SUMA', 'RESTA', 'MULT', 'DIV',
    'MAYOR', 'MENOR',
    'PUNTO_COMA', 'COMA', 'DOS_PUNTOS',
    'PAREN_IZQ', 'PAREN_DER',
    'LLAVE_IZQ', 'LLAVE_DER',
    'CORCHETE_IZQ', 'CORCHETE_DER',
] + list(reserved.values())

# REGLAS SIMPLES
# PLY asigna mayor precedencia a las funciones que a las cadenas,
# por eso IGUAL y DIFERENTE van primero que ASIGNA
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

# REGLAS CON FUNCION
# El orden importa: CTE_FLOT debe ir antes de CTE_ENT para que PLY
# no consuma la parte entera de un flotante como token separado

# Constante flotante: digitos, punto, digitos
def t_CTE_FLOT(t):
    r'[0-9]+\.[0-9]+'
    t.value = float(t.value)
    return t

# Constante entera
def t_CTE_ENT(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

# Cadena de texto entre comillas dobles
# Se eliminan las comillas del valor final
def t_CADENA(t):
    r'"[^"\n]*"'
    t.value = t.value[1:-1]
    return t

# Identificador o palabra reservada
# Si el lexema aparece en el mapa reserved, se clasifica como esa palabra,
# de lo contrario, se clasifica como ID
def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID') # revisar si es palabra reservada
    return t

# IGNORADOS
# Espacios, tabuladores y saltos de linea se descartan
t_ignore = ' \t\r\n'

# Comentarios de linea estilo // -> se descartan sin producir token
def t_COMENTARIO(t):
    r'\/\/[^\n]*'
    pass 

# MANEJO DE ERRORES
# Reporta el caracter invalido y avanza un lugar para continuar el analisis
def t_error(t):
    print(f"[LEXICO] Caracter invalido '{t.value[0]}' en linea {t.lineno}")
    t.lexer.skip(1)

# INVARS
# Manejo de declaracion de variable vs asignacion
t_invars_PUNTO_COMA = r';'
t_invars_COMA       = r','
t_invars_DOS_PUNTOS = r':'

def t_invars_ID_VAR(t):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    # Mirar hacia adelante en el input para decidir si es declaracion o no
    # Consumir espacios y ver el sig caracter no espacio
    pos = t.lexer.lexpos
    rest = t.lexer.lexdata[pos:]
    next_char = ''
    for ch in rest:
        if ch not in (' ', '\t', '\r', '\n'):
            next_char = ch
            break

    if t.value in reserved:
        # Palabra reservada: siempre cierra invars (excepto entero/flotante)
        if t.value in ('entero', 'flotante'):
            t.type = reserved[t.value]
        else:
            t.lexer.begin('INITIAL')
            t.type = reserved[t.value]
        return t
    
    # Si el siguiente caracter significativo es '=' o '(' o operadores,
    # es inicio de cuerpo, no declaracion de variable
    if next_char in ('=', '(', '+', '-', '*', '/'):
        t.lexer.begin('INITIAL')
        t.type = 'ID'  # es un ID normal (para asigna o llamada)
        return t

    # Si es ':' o ',' es declaracion de variable
        t.type = 'ID_VAR'
    return t
 
def t_invars_LLAVE_IZQ(t):
    r'\{'
    t.lexer.begin('INITIAL'); return t
def t_invars_LLAVE_DER(t):
    r'\}'
    t.lexer.begin('INITIAL'); return t
def t_invars_CORCHETE_IZQ(t):
    r'\['
    t.lexer.begin('INITIAL'); return t
def t_invars_CORCHETE_DER(t):
    r'\]'
    t.lexer.begin('INITIAL'); return t
def t_invars_PAREN_IZQ(t):
    r'\('
    t.lexer.begin('INITIAL'); return t
def t_invars_ASIGNA(t):
    r'='
    t.lexer.begin('INITIAL'); return t

t_invars_ignore = ' \t\r\n'
def t_invars_COMENTARIO(t):
    r'\/\/[^\n]*'
    pass

def t_invars_error(t):
    print(f"[LEXICO] Caracter invalido '{t.value[0]}' en linea {t.lineno}")
    t.lexer.skip(1)

# Construir el lexer
lexer = lex.lex()