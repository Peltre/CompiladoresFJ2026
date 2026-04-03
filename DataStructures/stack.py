
class Stack:
    """
    Implementación de Stack LIFO (Last in First Out)
    """

    def __init__(self):
        self._data = []

    def push(self, item): 
        """ Agrega un elemento al tope del stack"""
        self._data.append(item)

    def pop(self):
        """ Elimina y retorna el elemento del tope, lanza error si esta vacio"""
        if self.is_empty():
            raise IndexError("pop - stack vacio")
        return self._data.pop()
    
    def peek(self):
        """ Retorna el elemento del tope sin eliminarlo"""
        if self.is_empty():
            raise IndexError("peek - stack vacio")
        return self._data[-1]
    
    def is_empty(self):
        """ Verificación para que no esté vacio"""
        return len(self._data) == 0
    
    def clear(self):
        """ Vacia el stack """
        return self._data.clear()
    
    