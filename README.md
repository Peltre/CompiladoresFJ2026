---

## Etapa 0 — Definicion de Gramatica

Se disenaron las expresiones regulares y la gramatica libre de contexto del
lenguaje. Los elementos principales del lexico son:

- Identificador: `[a-zA-Z][a-zA-Z0-9_]*`
- Constante entera: `[0-9]+`
- Constante flotante: "[0-9]+regex[0-9]+"
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

*README generado a partir de documentacion personal utilizando Claude(Sonnet 4.6)*
