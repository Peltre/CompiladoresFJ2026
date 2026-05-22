# Archivo para el manejo de las direcciones virtuales para cada variable temporal y constante del programa

# Mapa de memoria, separado por tipo (propuesto en clase 5/21/2026)
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
    'constante': { 'entero': 13999, 'flotante': 1599},
}

# Clase personalizada, para resaltar errores semanticos
class ErrorMemoria(Exception):
    def __int__(self, mensaje):
        super().__init__(f"[ERROR de MEMORIA] {mensaje}")
        

class ManejoMemoria:
    def __init__(self):
        # Inicializar contadores por segmento y tipo, cada vez que se asigna una direccion, contador sube
        self.contadores = {
            'global': { 'entero': 0, 'flotante': 2000 },
            'local': { 'entero': 4000, 'flotante': 6000},
            'temporal': { 'entero': 8000, 'flotante': 10000},
            'constante': { 'entero': 12000, 'flotante': 14000},
        }

        # Tabla de constantes ya registradas para no duplicar direcciones
        self.tabla_constantes = {}

        def asignar(self, scope, tipo):
            # Asignar la sig direccion disponible para el scope y tipo de datos
            direccion = self.contadores[scope][tipo]

            # Verificar que estemos dentro del rango
            if direccion > LIMITES_MEMORIA[scope][tipo]:
                raise ErrorMemoria(f"Memoria {scope}/{tipo} agotada en direccion {direccion}")
            
            # avanzar el contador para la siguiente asignacion
            self.contadores[scope][tipo] += 1

            return direccion
        
        def asignar_temp(self, tipo):
            # Atajo para asignar una variable temporal
            return self.asignar('temporal', tipo)
        
        def asginar_constante(self, valor, tipo):
            # Asigna una direccion para una constante, y si ya fue registrada, retorna la misma direccion
            clave = (valor, tipo)
            if clave in self.tabla_constantes:
                return self.tabla_constantes[clave] # reutilizar en caso de que ya exista
            
            # Si es nueva, asignar dir y registrar
            direccion = self.asignar('constante', tipo)
            self.tabla_constantes[clave] = direccion
            return direccion
        
        def tipo_direccion(self, direccion):
            # Dada una direccion retornar su scope y tipo
            for scope, tipos in MAPA_MEMORIA.items():
                for tipo, inicio in tipos.items():
                    limite = LIMITES_MEMORIA[scope][tipo]
                    if inicio <= direccion <= limite:
                        return scope, tipo
                    
            return None, None
        
        def reset_local(self):
            # liberar direcciones locales al salir de una funcion " } "
            self.contadores['local']['entero'] = 4000
            self.contadores['local']['flotante'] = 6000

        def reset_temporal(self):
            # liberar direcciones temporales al terminar de procesar una func
            self.contadores['temporal']['entero'] = 8000
            self.contadores['temporal']['flotante'] = 10000

        
