# Archivo para realizar pruebas de funcionamiento sobre el compilador

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import v1_parser
from symbol_table import DirectorioFunciones
from quadruples import GeneradorCuadruplos
from memory_manager import ManejoMemoria
from v1_lexer import lexer

# ─────────────────────────────────────────────────────────────────────────────
# Casos de prueba
# Cada caso: (id, descripcion, codigo, debe_pasar)
#
# Gramática estricta del diagrama:
#   <PROGRAMA>   →  programa id ; VARS FUNCS inicio CUERPO fin
#   <CUERPO>     →  { ESTATUTO* }          ← siempre llaves, incluso en inicio
#   <FUNCS>      →  (nula|TIPO) id ( params ) { VARS CUERPO } ;
#                   ← la función tiene sus { }, y CUERPO adentro tiene sus propias { }
#   <CONDICIÓN>  →  si ( EXP ) CUERPO [ sino CUERPO ] ;
#   <CICLO>      →  mientras ( EXP ) haz CUERPO ;
#   <ASIGNA>     →  id = EXP ;
#   <LLAMADA>    →  id ( [EXP {, EXP}] ) ;
#   <IMPRIME>    →  escribe ( EXP|letrero {, ...} ) ;
# ─────────────────────────────────────────────────────────────────────────────

test_cases = [

    # ── VÁLIDOS ──────────────────────────────────────────────────────────────
    ("TC-01", "Programa minimo",
     """
     programa minimo;
     inicio
     {
     }
     fin
     """, True),

    ("TC-02", "Declaracion de variables y asignacion",
     """
     programa test;
     vars
       x, y : entero;
       r     : flotante;
     inicio
     {
       x = 5;
     }
     fin
     """, True),

    ("TC-03", "Condicional con sino",
     """
     programa test;
     vars
       x : entero;
     inicio
     {
       x = 10;
       si (x > 5) {
         escribe ("mayor");
       } sino {
         escribe ("menor o igual");
       } ;
     }
     fin
     """, True),

    ("TC-04", "Ciclo mientras",
     """
     programa test;
     vars
       i : entero;
     inicio
     {
       i = 0;
       mientras (i < 5) haz {
         i = i + 1;
       } ;
     }
     fin
     """, True),

    ("TC-05", "Funcion nula y llamada",
     """
     programa test;
     nula saludo () {
       {
         escribe ("hola");
       }
     } ;
     inicio
     {
       saludo();
     }
     fin
     """, True),

    # ── INVÁLIDOS ─────────────────────────────────────────────────────────────
    ("TC-06", "Falta punto y coma tras programa id",
     """
     programa test
     inicio
     {
     }
     fin
     """, False),

    ("TC-07", "Caracter invalido @",
     """
     programa test;
     inicio
     {
       x = 5 @ 3;
     }
     fin
     """, False),

    ("TC-08", "Tipo invalido booleano",
     """
     programa test;
     vars
       x : booleano;
     inicio
     {
     }
     fin
     """, False),

    ("TC-09", "Variable no declarada",
     """
     programa test;
     inicio
     {
       z = 10;
     }
     fin
     """, False),

    ("TC-10", "Funcion no declarada",
     """
     programa test;
     inicio
     {
       fantasma();
     }
     fin
     """, False),

    # ── CUÁDRUPLOS ────────────────────────────────────────────────────────────
    ("TC-11", "Cuadruplos: asignacion simple",
     """
     programa test;
     vars
       r : entero;
     inicio
     {
       r = 5;
     }
     fin
     """, True),

    ("TC-12", "Cuadruplos: precedencia aritmetica",
     """
     programa test;
     vars
       r : entero;
     inicio
     {
       r = 2 + 3 * 4;
     }
     fin
     """, True),

    ("TC-13", "Cuadruplos: parentesis alteran precedencia",
     """
     programa test;
     vars
       r : entero;
     inicio
     {
       r = (2 + 3) * 4;
     }
     fin
     """, True),

    ("TC-14", "Cuadruplos: operador relacional",
     """
     programa test;
     vars
       a, b, r : entero;
     inicio
     {
       a = 1;
       b = 2;
       r = a != b;
     }
     fin
     """, True),

    ("TC-15", "Cuadruplos: expresion mixta entero y flotante",
     """
     programa test;
     vars
       x : entero;
       y : flotante;
       r : flotante;
     inicio
     {
       x = 3;
       y = 1.5;
       r = x + y;
     }
     fin
     """, True),

    # ── EJECUCION: EXPRESIONES ────────────────────────────────────────────────
    ("TC-16", "Ejecucion: asignacion y escribe",
     """
     programa test;
     vars
       x : entero;
     inicio
     {
       x = 42;
       escribe (x);
     }
     fin
     """, True),
    # Salida esperada: 42

    ("TC-17", "Ejecucion: operacion aritmetica",
     """
     programa test;
     vars
       r : entero;
     inicio
     {
       r = 10 + 5 * 2;
       escribe (r);
     }
     fin
     """, True),
    # Salida esperada: 20  (precedencia: 5*2=10, 10+10=20)

    ("TC-18", "Ejecucion: condicional verdadero",
     """
     programa test;
     vars
       x : entero;
     inicio
     {
       x = 10;
       si (x > 5) {
         escribe ("mayor que 5");
       } sino {
         escribe ("menor o igual");
       } ;
     }
     fin
     """, True),
    # Salida esperada: mayor que 5

    ("TC-19", "Ejecucion: ciclo factorial",
     """
     programa test;
     vars
       n, resultado, i : entero;
     inicio
     {
       n = 5;
       resultado = 1;
       i = 1;
       mientras (i < n + 1) haz {
         resultado = resultado * i;
         i = i + 1;
       } ;
       escribe (resultado);
     }
     fin
     """, True),
    # Salida esperada: 120

    ("TC-20", "Ejecucion: fibonacci ciclico",
     """
     programa test;
     vars
       a, b, temp, i : entero;
     inicio
     {
       a = 0;
       b = 1;
       i = 0;
       mientras (i < 8) haz {
         temp = a + b;
         a = b;
         b = temp;
         i = i + 1;
       } ;
       escribe (a);
     }
     fin
     """, True),
    # Salida esperada: 34  (8vo numero de fibonacci)

    # ── EJECUCION: FUNCIONES ──────────────────────────────────────────────────
    ("TC-21", "Ejecucion: funcion nula con escribe",
     """
     programa test;
     nula saluda () {
       {
         escribe ("hola mundo");
       }
     } ;
     inicio
     {
       saluda();
     }
     fin
     """, True),
    # Salida esperada: hola mundo

    ("TC-22", "Ejecucion: funcion con retorno entero",
     """
    programa test;
    vars            
      r : entero;
    entero duplica () {
      vars
        x : entero;
      {
        x = 4;
        regresa x + x;
      }
    } ;
    inicio
    {
      duplica();
      r = duplica;
      escribe (r);
    }
    fin
     """, True),
    # Salida esperada: 8

    # ── ERRORES SEMANTICOS ────────────────────────────────────────────────────
    ("TC-23", "Error: variable redeclarada en mismo scope",
     """
     programa test;
     vars
       x : entero;
       x : flotante;
     inicio
     {
     }
     fin
     """, False),

    ("TC-24", "Error: funcion redeclarada",
     """
     programa test;
     nula foo () {
       {
         escribe ("primera");
       }
     } ;
     nula foo () {
       {
         escribe ("segunda");
       }
     } ;
     inicio
     {
       foo();
     }
     fin
     """, False),

    # ── ANIDAMIENTO ───────────────────────────────────────────────────────────
    ("TC-25", "Ciclos anidados",
     """
     programa test;
     vars
       i, j, r : entero;
     inicio
     {
       i = 0;
       r = 0;
       mientras (i < 3) haz {
         j = 0;
         mientras (j < 3) haz {
           r = r + 1;
           j = j + 1;
         } ;
         i = i + 1;
       } ;
       escribe (r);
     }
     fin
     """, True),
    # Salida esperada: 9  (3x3 iteraciones)
]

# ─────────────────────────────────────────────────────────────────────────────
# Runner
# ─────────────────────────────────────────────────────────────────────────────
def run_tests():
    passed = 0
    failed = 0
    results = []

    print("=" * 60)
    print("  TEST PLAN — Compilador Patito (Etapa 1)")
    print("=" * 60)

    import io, contextlib

    for tc_id, desc, code, should_pass in test_cases:
        print(f"\n{tc_id}: {desc}")
        print(f"  Esperado: {'VALIDO' if should_pass else 'INVALIDO'}")

        v1_parser.directorio          = DirectorioFunciones()
        v1_parser.memoria             = ManejoMemoria()
        v1_parser.generador           = GeneradorCuadruplos(v1_parser.memoria)
        v1_parser._ids_pendientes     = []
        v1_parser.hay_error_semantico = False

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            fresh_lexer = lexer.clone()
            fresh_lexer.lineno = 1
            result = v1_parser.parser.parse(code, lexer=fresh_lexer)

        output = buf.getvalue()
        ok_found  = "[OK]" in output
        err_found = "[ERROR" in output or "[SINTAXIS]" in output or "[LEXICO]" in output

        if should_pass:
            if ok_found and not err_found:
              print(f"  Resultado: PASS ✓")
              if output.strip():
                  for line in output.strip().splitlines():
                      if not line.startswith("[DEBUG"):
                          print(f"  Output VM: {line}")  # ← agregar esto
              passed += 1
            else:
                print(f"  Resultado: FAIL ✗  (se esperaba OK pero hubo error)")
                if output.strip():
                    for line in output.strip().splitlines():
                        if not line.startswith("[DEBUG"):
                            print(f"  Salida: {line}")
                failed += 1
                results.append((tc_id, desc, "FAIL"))
        else:
            if err_found and not ok_found:
                print(f"  Resultado: PASS ✓  (error detectado correctamente)")
                passed += 1
                results.append((tc_id, desc, "PASS"))
            else:
                print(f"  Resultado: FAIL ✗  (se esperaba error pero no se detecto)")
                failed += 1
                results.append((tc_id, desc, "FAIL"))

    print("\n" + "=" * 60)
    print(f"  RESULTADO FINAL: {passed}/{len(test_cases)} tests pasaron")
    if failed:
        print(f"  FALLIDOS: {failed}")
    print("=" * 60)
    return results

if __name__ == '__main__':
    run_tests()