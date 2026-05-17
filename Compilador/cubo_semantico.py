# Diccionario de 3 niveles que funciona como tabla de consulta.
# No es tan largo ya que solo manejamos 2 tipos de datos (FLOTANTE / INT)
# Basicamente sirve para consultar que tipo resulta de operaciones entre 2 tipos

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

