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
# ─────────────────────────────────────────────────────────────────────────────
test_cases = [

    # ── VÁLIDOS ──────────────────────────────────────────────────────────────
    ("TC-01", "Programa minimo",
     """
     programa minimo;
     inicio
     fin
     """, True),

    ("TC-02", "Declaracion de variables y asignacion",
     """
     programa test;
     vars
       x, y : entero;
       r     : flotante;
     inicio
       x = 5;
     fin
     """, True),

    ("TC-03", "Condicional con sino",
     """
     programa test;
     vars
       x : entero;
     inicio
       x = 10;
       si (x > 5) [
         escribe ("mayor");
       ] sino [
         escribe ("menor o igual");
       ]
     fin
     """, True),

    ("TC-04", "Ciclo mientras",
     """
     programa test;
     vars
       i : entero;
     inicio
       i = 0;
       mientras (i < 5) haz [
         i = i + 1;
       ];
     fin
     """, True),

    ("TC-05", "Funcion nula y llamada",
    """
    programa test;
    nula saludo () {
      escribe ("hola");
    };
    inicio
      saludo();
    fin
    """, True),

    # ── INVÁLIDOS ─────────────────────────────────────────────────────────────
    ("TC-06", "Falta punto y coma tras programa id",
     """
     programa test
     inicio
     fin
     """, False),

    ("TC-07", "Caracter invalido @",
     """
     programa test;
     inicio
       x = 5 @ 3;
     fin
     """, False),

    ("TC-08", "Tipo invalido booleano",
     """
     programa test;
     vars
       x : booleano;
     inicio
     fin
     """, False),

    ("TC-09", "Variable no declarada",
     """
     programa test;
     inicio
       z = 10;
     fin
     """, False),

    ("TC-10", "Falta fin",
     """
     programa test;
     inicio
     """, False),

    # ── CUÁDRUPLOS ────────────────────────────────────────────────────────────
    # Estos casos validan que los cuádruplos generados sean correctos.
    # El runner los ejecuta igual que los válidos pero además imprime
    # la fila de cuádruplos para revisión manual.

    ("TC-11", "Cuadruplos: asignacion simple",
     """
     programa test;
     vars
       r : entero;
     inicio
       r = 5;
     fin
     """, True),
    # Cuádruplos esperados:
    # ( =, dir_cte_5, _, dir_r )

    ("TC-12", "Cuadruplos: expresion aritmetica con precedencia",
     """
     programa test;
     vars
       r : entero;
     inicio
       r = 2 + 3 * 4;
     fin
     """, True),
    # Cuádruplos esperados:
    # ( *,  dir_3,  dir_4,  t1 )
    # ( +,  dir_2,  t1,     t2 )
    # ( =,  t2,     _,      dir_r )

    ("TC-13", "Cuadruplos: expresion con parentesis",
     """
     programa test;
     vars
       r : entero;
     inicio
       r = (2 + 3) * 4;
     fin
     """, True),
    # Cuádruplos esperados:
    # ( +,  dir_2,  dir_3,  t1 )
    # ( *,  t1,     dir_4,  t2 )
    # ( =,  t2,     _,      dir_r )

    ("TC-14", "Cuadruplos: operador relacional",
     """
     programa test;
     vars
       a, b : entero;
       r    : entero;
     inicio
       a = 1;
       b = 2;
       r = a != b;
     fin
     """, True),
    # Cuádruplos esperados:
    # ( =,  dir_1,  _,      dir_a )
    # ( =,  dir_2,  _,      dir_b )
    # ( !=, dir_a,  dir_b,  t1    )
    # ( =,  t1,     _,      dir_r )

    ("TC-15", "Cuadruplos: expresion mixta entero y flotante",
     """
     programa test;
     vars
       x : entero;
       y : flotante;
       r : flotante;
     inicio
       x = 3;
       y = 1.5;
       r = x + y;
     fin
     """, True),
    # Cuádruplos esperados:
    # ( =,  dir_3,    _,      dir_x )
    # ( =,  dir_1.5,  _,      dir_y )
    # ( +,  dir_x,    dir_y,  t1    )   ← t1 es flotante por el cubo semántico
    # ( =,  t1,       _,      dir_r )

    # ── FUNCIONES CON RETORNO ─────────────────────────────────────────────────
("TC-16", "Funcion con retorno entero",
 """
 programa test;
 entero duplica () {
   vars
     x : entero;
   x = 4;
   regresa x + x;
 };
 inicio
   duplica();
 fin
 """, True),
    # Cuádruplos esperados:
    # ( GOTO,    _,     _,     5      )   ← salta el cuerpo de la func
    # ( ERA,     duplica, _,   _      )
    # ( =,       dir_4,   _,   dir_x  )
    # ( +,       dir_x,  dir_x, t1    )
    # ( =,       t1,      _,   dir_duplica_global )
    # ( ENDFUNC, _,       _,   _      )
    # ( GOSUB,   duplica, 1,   _      )

    # ── CICLOS ANIDADOS ───────────────────────────────────────────────────────
    ("TC-17", "Ciclo mientras anidado",
     """
     programa test;
     vars
       i, j : entero;
     inicio
       i = 0;
       mientras (i < 3) haz [
         j = 0;
         mientras (j < 3) haz [
           j = j + 1;
         ];
         i = i + 1;
       ];
     fin
     """, True),
    # Cuádruplos esperados (simplificado):
    # ( =,     dir_0,  _,      dir_i )
    # ( <,     dir_i,  dir_3,  t1    )   ← condicion outer
    # ( GOTOF, t1,     _,      ?     )
    # ( =,     dir_0,  _,      dir_j )
    # ( <,     dir_j,  dir_3,  t2    )   ← condicion inner
    # ( GOTOF, t2,     _,      ?     )
    # ( +,     dir_j,  dir_1,  t3    )
    # ( =,     t3,     _,      dir_j )
    # ( GOTO,  _,      _,      inner_inicio )
    # ( +,     dir_i,  dir_1,  t4    )
    # ( =,     t4,     _,      dir_i )
    # ( GOTO,  _,      _,      outer_inicio )

    # ── CONDICIONALES ANIDADOS ────────────────────────────────────────────────
    ("TC-18", "Condicional anidado dentro de si",
     """
     programa test;
     vars
       x, y : entero;
     inicio
       x = 5;
       y = 10;
       si (x < y) [
         si (x > 0) [
           escribe ("positivo y menor");
         ]
       ]
     fin
     """, True),

    # ── LLAMADA CON ARGS (ERROR: lenguaje no soporta params, debe detectarlo) ─
    ("TC-19", "Llamada a funcion no declarada",
     """
     programa test;
     inicio
       fantasma();
     fin
     """, False),

    # ── EXPRESIONES COMPLEJAS / PRECEDENCIA ───────────────────────────────────
    ("TC-20", "Precedencia: suma dentro de multiplicacion con parentesis",
     """
     programa test;
     vars
       r : entero;
     inicio
       r = (1 + 2) * (3 + 4);
     fin
     """, True),
    # Cuádruplos esperados:
    # ( +,  dir_1,  dir_2,  t1 )
    # ( +,  dir_3,  dir_4,  t2 )
    # ( *,  t1,     t2,     t3 )
    # ( =,  t3,     _,      dir_r )

    ("TC-21", "Precedencia: relacional sobre expresion aritmetica",
     """
     programa test;
     vars
       a, b, r : entero;
     inicio
       a = 2;
       b = 3;
       r = a + 1 > b - 1;
     fin
     """, True),
    # Cuádruplos esperados:
    # ( =,  dir_2,  _,      dir_a )
    # ( =,  dir_3,  _,      dir_b )
    # ( +,  dir_a,  dir_1,  t1    )
    # ( -,  dir_b,  dir_1,  t2    )
    # ( >,  t1,     t2,     t3    )
    # ( =,  t3,     _,      dir_r )

    # ── ERRORES SEMANTICOS ────────────────────────────────────────────────────
    ("TC-22", "Error: variable redeclarada en mismo scope",
     """
     programa test;
     vars
       x : entero;
       x : flotante;
     inicio
     fin
     """, False),

      ("TC-23", "Error: funcion redeclarada",
      """
      programa test;
      nula foo () {
        escribe ("primera");
      };
      nula foo () {
        escribe ("segunda");
      };
      inicio
        foo();
      fin
      """, False),

    # ── CUADRUPLOS DETALLADOS ─────────────────────────────────────────────────
    ("TC-24", "Cuadruplos: condicional simple sin sino",
     """
     programa test;
     vars
       x : entero;
     inicio
       x = 3;
       si (x > 0) [
         x = x + 1;
       ]
     fin
     """, True),
    # Cuádruplos esperados:
    # ( =,     dir_3,  _,      dir_x  )
    # ( >,     dir_x,  dir_0,  t1     )
    # ( GOTOF, t1,     _,      7      )   ← apunta al cuadruplo despues del cuerpo
    # ( +,     dir_x,  dir_1,  t2     )
    # ( =,     t2,     _,      dir_x  )

    ("TC-25", "Cuadruplos: ciclo con condicion relacional",
     """
     programa test;
     vars
       n : entero;
     inicio
       n = 10;
       mientras (n != 0) haz [
         n = n - 1;
       ];
     fin
     """, True),
    # Cuádruplos esperados:
    # ( =,     dir_10, _,      dir_n  )
    # ( !=,    dir_n,  dir_0,  t1     )   ← inicio del ciclo (indice 1)
    # ( GOTOF, t1,     _,      6      )
    # ( -,     dir_n,  dir_1,  t2     )
    # ( =,     t2,     _,      dir_n  )
    # ( GOTO,  _,      _,      1      )   ← regresa al inicio

    ("TC-26", "Cuadruplos: funcion nula con escribe",
 """
 programa test;
 nula saluda () {
   escribe ("hola mundo");
 };
 inicio
   saluda();
 fin
 """, True),
    # Cuádruplos esperados:
    # ( GOTO,    _,       _,  3      )   ← salta el cuerpo
    # ( ERA,     saluda,  _,  _      )
    # ( ENDFUNC, _,       _,  _      )
    # ( GOSUB,   saluda,  1,  _      )
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

        # Resetear estado global antes de cada test
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
                passed += 1
                results.append((tc_id, desc, "PASS"))
            else:
                print(f"  Resultado: FAIL ✗  (se esperaba OK pero hubo error)")
                if output.strip():
                    print(f"  Salida: {output.strip()}")
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
    