# semantic_cube.py | LM: 5/29/2026 | By: Pedro Sotelo
# Tabla de consulta de tipos resultado para operaciones entre 2 operandos.
# Solo maneja 2 tipos: entero y flotante.

# CUBO SEMANTICO
# Diccionario de 3 niveles: tipo_izq -> tipo_der -> operador -> tipo_resultado
# Las operaciones relacionales siempre regresan entero (0 / 1)
cubo_semantico = {
    'entero': {
        'entero': { '+': 'entero', '-': 'entero', '*': 'entero', '/': 'entero',
                   '>': 'entero', '<': 'entero', '==': 'entero', '!=': 'entero'},
        'flotante': { '+': 'flotante', '-': 'flotante', '*': 'flotante', '/': 'flotante',
                   '>': 'entero', '<': 'entero', '==': 'entero', '!=': 'entero'},
    },
    'flotante': {
        'entero': { '+': 'flotante', '-': 'flotante', '*': 'flotante', '/': 'flotante',
                   '>': 'entero', '<': 'entero', '==': 'entero', '!=': 'entero'},
        'flotante': { '+': 'flotante', '-': 'flotante', '*': 'flotante', '/': 'flotante',
                   '>': 'entero', '<': 'entero', '==': 'entero', '!=': 'entero'},
    }
}

# CONSULTA DE TIPO RESULTADO
# Dados 2 tipos y un operador, retorna el tipo del resultado
# Si la combinacion no existe en el cubo, retorna 'error'
def tipo_resultado(tipo_izq, tipo_der, operador):
    try:
        return cubo_semantico[tipo_izq][tipo_der][operador]
    except KeyError:
        return 'error'


