# memory_manager | LM: 5/29/2026 | By: Pedro Sotelo
# Manejo de direcciones virtuales para variables, temporales y constantes.
# Cada variable del programa recibe un numero entero como direccion

# MAPA DE MEMORIA
# Define en donde empieza y termina cada segmento, separado por scope y tipo.
# Dada cualquier direccion, se puede saber su scope y tipo sin consultar ninguna tabla adicional
MAPA_MEMORIA = {
    'global': { 'entero': 0, 'flotante': 2000 },
    'local': { 'entero': 4000, 'flotante': 6000},
    'temporal': { 'entero': 8000, 'flotante': 10000},
    'constante': { 'entero': 12000, 'flotante': 14000},
}

LIMITES_MEMORIA = {
    'global': { 'entero': 1999, 'flotante': 3999 },
    'local': { 'entero': 5999, 'flotante': 7999},
    'temporal': { 'entero': 9999, 'flotante': 11999},
    'constante': { 'entero': 13999, 'flotante': 15999},
}

# ERROR DE MEMORIA
# Excepcion personalizada para manejo de errores de memroia
class ErrorMemoria(Exception):
    def __init__(self, mensaje):
        super().__init__(f"[ERROR de MEMORIA] {mensaje}")
        
# MANEJO DE MEMORIA
# Clase principal que mantiene contadores por segmento y tipo
# Cada vez que se asigna una direccion, el contador sube 1
class ManejoMemoria:
    def __init__(self):
        # Contadores actuales por segmento y tipo
        # Arrancan en la misma direccion que el mapa
        self.contadores = {
            'global': { 'entero': 0, 'flotante': 2000 },
            'local': { 'entero': 4000, 'flotante': 6000},
            'temporal': { 'entero': 8000, 'flotante': 10000},
            'constante': { 'entero': 12000, 'flotante': 14000},
        }

        # Guarda las constantes ya registradas para no duplicar direcciones
        # Estructura: { (valor, tipo) -> direccion }
        self.tabla_constantes = {}

    # ASIGNACION DE DIRECCIONES
    def asignar(self, scope, tipo):
            # Entrega la siguiente direccion disponible para el scope y tipo dados
            # y avanza el contador. Lanza error si el segmento esta lleno
            direccion = self.contadores[scope][tipo]
            if direccion > LIMITES_MEMORIA[scope][tipo]:
                raise ErrorMemoria(f"Memoria {scope}/{tipo} agotada en direccion {direccion}")
            self.contadores[scope][tipo] += 1
            return direccion
        
    def asignar_temp(self, tipo):
            # Atajo para asignar una variable temporal
            return self.asignar('temporal', tipo)
        
    def asignar_constante(self, valor, tipo):
            # Asigna una direccion a una constante si no existe ya
            clave = (valor, tipo)
            if clave in self.tabla_constantes:
                return self.tabla_constantes[clave] # reutilizar en caso de que ya exista
            direccion = self.asignar('constante', tipo)
            self.tabla_constantes[clave] = direccion
            return direccion
    
    # CONSULTA DE DIRECCIONES
    def tipo_direccion(self, direccion):
            # Dado un numero de direccion, retorna scope y tipo
            for scope, tipos in MAPA_MEMORIA.items():
                for tipo, inicio in tipos.items():
                    limite = LIMITES_MEMORIA[scope][tipo]
                    if inicio <= direccion <= limite:
                        return scope, tipo
            return None, None
    
    # RESET DE SEGMENTOS -> LIBERACION DE MEMORIA
    def reset_local(self):
            # liberar direcciones locales al salir de una funcion " } "
            self.contadores['local']['entero'] = 4000
            self.contadores['local']['flotante'] = 6000

    def reset_temporal(self):
            # liberar direcciones temporales al terminar de procesar una func
            self.contadores['temporal']['entero'] = 8000
            self.contadores['temporal']['flotante'] = 10000

        
