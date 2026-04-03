""" 
Tarea 1 - Hash Tables - Python
"""

class HashTable:
    """
    Implementación de una Hash Table con orden de inserción, usa un diccionario de Python
    """

    def __init__(self):
        self._data = {}

    def set(self, key, value):
        """ Inserta / actualiza un key-value """
        self._data[key] = value

    def get(self, key, default= None):
        """ Retorna el valor de la clave o default si no existe """
        return self._data.get(key, default)
    
    def delete(self, key):
        """ Elimina una clave, lanza error si no existe """
        if key not in self._data:
            raise KeyError(f"Clave '{key}' no encontrada")
        del self._data[key]

    def contains(self, key):
        """ Retorna True si la clave existe """
        return key in self._data
    
    def items(self):
        """ Retorna pares (clave, valor) en orden de inserción """
        return list(self._data.items())
    

    
