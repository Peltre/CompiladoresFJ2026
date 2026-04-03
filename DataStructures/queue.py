""" 
Tarea 1 - FIFO - Python
"""

from collections import deque

class Queue:
    """
    Implementación del Queue FIFO First in First Out
    """
    def __init__ (self):
        self._data = deque()

    def addQueue(self, item):
        """ Agregar un tope al tope"""
        self._data.append(item)

    def removeQueue(self, item):
        """ Elimina y retorna el elemento (que entró primero)"""
        if self.is_empty():
            raise IndexError("remove - La cola está vacia")
        return self._data.popleft()
    
    def front(self):
        """ Retorna el elemento al frente de la cola """
        if self.is_empty():
            raise IndexError("front - La cola está vacia")
        return self._data[0]
    
    def rear(self):
        """ Retorna el elemento al final de la cola """
        if self.is_empty():
            raise IndexError("rear - La cola está vacia")
        return self._data[-1]
    
    def is_empty(self):
        return len(self._data) == 0
    
    def clear(self):
        self._data.clear()