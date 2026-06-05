## Etapa 0 — Definicion de Gramatica

Se disenaron las expresiones regulares y la gramatica libre de contexto del
lenguaje. Los elementos principales del lexico son:

- Identificador: `[a-zA-Z][a-zA-Z0-9_]*`
- Constante entera: `[0-9]+`
- Constante flotante: `[0-9]+\.[0-9]+`
- Cadena: `"[^"\n]*"`
- Palabras reservadas: `programa | inicio | fin | vars | entero | flotante |
  si | sino | mientras | haz | escribe | nula`

El lenguaje reconoce 34 tokens en total, incluyendo operadores aritmeticos
`+ - * /`, relacionales `> < == !=`, y delimitadores `. ; , : ( ) { } [ ]`.

La gramatica cubre las construcciones principales: declaracion de variables,
funciones, condicionales, ciclos, impresion y expresiones aritmeticas y
relacionales con precedencia correcta.

---

## Etapa 1 — Scanner y Parser

Se evaluo el uso de PLY, ANTLR, Lark y SLY como herramientas de generacion
automatica. Se selecciono PLY porque es Python puro, su estructura refleja
directamente la teoria de compiladores, y cuenta con la mejor documentacion
para el alcance del proyecto.

Las reglas lexicas se declaran como funciones o variables con prefijo `t_`,
usando expresiones regulares como patron. Las reglas gramaticales se declaran
como funciones con prefijo `p_`, con la produccion BNF en el docstring.

Se disenaron 20 casos de prueba: 15 validos y 5 invalidos. Resultado: 20/20.

---

## Etapa 2 — Semantica de Variables

Se implementaron tres estructuras principales, todas basadas en diccionarios
de Python por su busqueda e insercion en O(1).

**Cubo semantico:** diccionario de tres niveles `cubo[tipo_izq][tipo_der][op]`
que determina el tipo resultante de cualquier operacion entre dos tipos. Se
consulta unicamente durante el analisis de expresiones.

**Tabla de Variables:** diccionario `{ nombre -> { tipo, direccion } }` por
cada scope. Detecta variables doblemente declaradas al momento de insertar.

**Directorio de Funciones:** diccionario `{ nombre -> { tipo, TablaVariables } }`
que agrupa todas las funciones del programa. Mantiene un atributo `scope_actual`
para saber en que funcion esta parado el parser en cada momento.

Los semantic actions mas importantes en esta etapa fueron: registrar funciones
y cambiar scope al reconocer su header, regresar a global al cerrar `}`,
registrar variables al reconocer su declaracion, y verificar existencia al
usar una variable o llamar una funcion.

---

## Etapa 3 — Generacion de Codigo Intermedio

Se implemento un mapa de memoria virtual separado por scope y tipo:

| Segmento  | Entero       | Flotante       |
|-----------|-------------|----------------|
| Global    | 0 - 1999    | 2000 - 3999    |
| Local     | 4000 - 5999 | 6000 - 7999    |
| Temporal  | 8000 - 9999 | 10000 - 11999  |
| Constante | 12000 - 13999 | 14000 - 15999 |

Cada variable, temporal y constante recibe una direccion virtual en lugar de
un nombre. Dada cualquier direccion se puede saber su scope y tipo sin consultar
ninguna tabla adicional.

Para generar los cuadruplos se implementaron tres pilas (operandos, tipos,
operadores) y una fila de cuadruplos en `quadruples.py`. Cada cuadruplo es una
tupla de cuatro campos:

## Etapa 4 — Estatutos, Funciones y Código Intermedio Completo

### Lo que ya existía desde Etapa 3

El mapa de direcciones virtuales, la clase `ManejoMemoria`, y la generación
de cuádruplos para expresiones aritméticas, relacionales y asignaciones
simples ya estaban implementados desde la entrega anterior.

### Lo nuevo en esta etapa

**Direcciones virtuales completas**
Las constantes literales se registran en el segmento constante con
`asignar_constante(valor, tipo)`, reutilizando la misma dirección si la
constante ya fue vista. Cada operación intermedia genera una dirección
temporal nueva con `asignar_temp(tipo)`.

**Cuádruplos para condicionales y ciclos**
El `si` genera un `GOTOF` con destino vacío al evaluar la condición, cuyo
índice se guarda en `pila_saltos` para rellenarse al cerrar el bloque. El
`sino` intercala un `GOTO` incondicional antes de su bloque. El `mientras`
guarda el índice de inicio en `pila_ciclos` y genera `GOTOF` + `GOTO` de
regreso al cerrar.

**Cuádruplos para funciones**
Al declarar una función se genera `GOTO` para saltarla, seguido de `ERA`.
Al cerrarla se genera `ENDFUNC` y se rellena el `GOTO`. Al invocarla se
genera `GOSUB` apuntando al índice `ERA`. Las funciones con valor de retorno
usan una variable global con su nombre para depositar el resultado del
`regresa`.

### Distribución de Direcciones Virtuales

| Segmento  | Entero        | Flotante       |
|-----------|---------------|----------------|
| Global    | 0 – 1999      | 2000 – 3999    |
| Local     | 4000 – 5999   | 6000 – 7999    |
| Temporal  | 8000 – 9999   | 10000 – 11999  |
| Constante | 12000 – 13999 | 14000 – 15999  |

Dada cualquier dirección se puede determinar su scope y tipo sin consultar
ninguna tabla adicional.

### Resultados

26/26 casos de prueba exitosos.

## Etapa 5 — Maquina Virtual y Parametros de Funciones
 
### Maquina Virtual
 
Se implemento `virtual_machine.py`, que recibe la fila de cuadruplos generada
por el compilador y la ejecuta instruccion por instruccion. La memoria de
ejecucion es un diccionario `{ direccion_virtual -> valor }`, por lo que las
mismas direcciones asignadas en tiempo de compilacion se usan directamente en
tiempo de ejecucion sin ninguna traduccion adicional.
 
Las constantes se cargan en memoria al inicializar la VM desde `tabla_constantes`
del compilador. El contador de programa `PC` avanza secuencialmente excepto
cuando se ejecuta un salto. Los opcodes soportados son:
 
- Aritmeticos y relacionales: `+ - * / > < == !=`
- Asignacion: `=`
- Saltos: `GOTO`, `GOTOF`
- Impresion: `ESCRIBE`
- Funciones: `ERA`, `GOSUB`, `ENDFUNC`, `PARAM`
Para las llamadas a funciones se usa una `pila_llamadas` que guarda el `PC`
de retorno al ejecutar `GOSUB` y lo recupera al ejecutar `ENDFUNC`.
 
### Parametros de Funciones
 
Se agrego soporte completo para declarar y pasar parametros a funciones.
Los cambios se distribuyeron en cuatro archivos:
 
**`symbol_table.py`:** el directorio de funciones ahora guarda una lista
ordenada `params` por funcion. El nuevo metodo `agregar_param` registra cada
parametro tanto en esa lista como en la tabla de variables locales, para que
sea accesible como variable dentro del cuerpo de la funcion.
 
**`quadruples.py`:** nuevo metodo `agregar_param(dir_param)` que emite el
cuadruplo `(PARAM, valor, _, dir_param)`, generado una vez por argumento
antes del `GOSUB`.
 
**`virtual_machine.py`:** nuevo caso `PARAM` que copia el valor del argumento
a la direccion local del parametro, equivalente a una asignacion de memoria.
 
**`v1_parser.py`:** el cambio mas importante fue resolver un problema de orden
de ejecucion propio de los parsers LR. Las acciones semanticas de una regla
padre se ejecutan despues de que todos sus hijos ya fueron reducidos, por lo
que al momento de procesar `params_decl` el scope todavia era `global`. La
solucion fue introducir el no-terminal intermedio `func_registrar`, que
consume `TIPO func_nombre PAREN_IZQ` y ejecuta `agregar_funcion` +
`entrar_funcion` de inmediato, garantizando que `params_decl` ya vea el scope
correcto de la funcion. En `p_llamada` se valida la cantidad de argumentos,
la compatibilidad de tipos contra los parametros declarados, y se emite un
cuadruplo `PARAM` por cada argumento antes del `GOSUB`.
 
### Resultados
 
28/28 casos de prueba exitosos.
 
*README generado a partir de documentacion personal utilizando Claude(Sonnet 4.6)*

