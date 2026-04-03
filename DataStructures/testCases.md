# Test Cases - DataStructures

## Stack
| # | Acción | Entrada | Esperado | Resultado |
|---|--------|---------|----------|-----------|
| 1 | push x3 | "a","b","c" | stack top="c" | ✅ |
| 2 | peek | — | "c" (sin modificar) | ✅ |
| 3 | pop x2 | — | "c", luego "b" | ✅ |
| 4 | isEmpty | - | "False" | ✅ | 
| 5 | clear | — | is_empty=True | ✅ |

## Queue
| # | Acción | Entrada | Esperado | Resultado |
|---|--------|---------|----------|-----------|
| 1 | addQueue x3 | "a","b","c" | front="a", rear="c" | ✅ |
| 2 | removeQueue x2 | — | "a", luego "b" | ✅ |
| 4 | addQueue tras removeQueue | "d" | front="c", rear="d" | ✅ |

## HashTable
| # | Acción | Entrada | Esperado | Resultado |
|---|--------|---------|----------|-----------|
| 1 | set x3 | nombre/edad/ciudad | 3 ítems en orden | ✅ |
| 2 | get existente | "nombre" | "María" | ✅ |
| 3 | get con default | "país" | "N/A" | ✅ |
| 4 | delete | "edad" | clave eliminada | ✅ |
| 5 | delete no existe | "foo" | KeyError | ✅ |
| 6 | update clave | "nombre"="Ana" | valor actualizado | ✅ |