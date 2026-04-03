"""
Demostración de las 3 clases implementadas en la Tarea 1
LIFO, FIFO y Hash Tables.
"""

from stack import Stack
from queue import Queue
from hash_table import HashTable

def separator(title):
    print(f"\n{'='*40}")
    print(f"  {title}")
    print('='*40)

# ------------- STACK (LIFO) ---------------------
separator("Stack (LIFO)")

s = Stack()
s.push("a")
s.push("b")
s.push("c")
print(s)
print("peek:", s.peek()) # c      
print("pop:", s.pop())  # c    
print("pop:", s.pop())  # b
print("is_empty:", s.is_empty()) # False
s.clear()
print("after clear, is_empty:", s.is_empty()) # True

# -------------- QUEUE (FIFO) --------------------
separator("QUEUE (FIFO)")

q = Queue()
q.addQueue("a")
q.addQueue("b")
q.addQueue("c")
print(q)
print("front:", q.front()) # a
print("rear:", q.rear()) # c
print("dequeue:", q.removeQueue()) # a
print("dequeue:", q.removeQueue()) # b

q.addQueue("d")
print(q) # Queue(front → ['c', 'd'] ← rear)

# -------------- HASH TABLE / DICT ----------------
separator("HASH TABLE / DICT")

ht = HashTable()
ht.set("nombre", "María")
ht.set("edad", 25)
ht.set("ciudad", "Monterrey")
print(ht)

print("get nombre:", ht.get("nombre")) # María
print("get país:", ht.get("país", "N/A")) # N/A (default)
print("contains 'edad':", ht.contains("edad")) # True
ht.delete("edad")
print("items:", ht.items())
ht.set("nombre", "Ana") # actualizar clave existente
print("after update nombre:", ht.get("nombre"))  # Ana