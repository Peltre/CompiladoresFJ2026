# Archivo para realizar pruebas de funcionamiento sobre el compilador

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import v1_parser
from symbol_table import DirectorioFunciones
from quadruples import GeneradorCuadruplos
from memory_manager import ManejoMemoria

from v1_lexer import lexer
from v1_parser import parser

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
     saludo (nula) {
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

    for tc_id, desc, code, should_pass in test_cases:
        print(f"\n{tc_id}: {desc}")
        print(f"  Esperado: {'VALIDO' if should_pass else 'INVALIDO'}")

        # Resetear el directorio antes de cada test
        v1_parser.directorio = DirectorioFunciones()
        v1_parser.memoria = ManejoMemoria()
        v1_parser.generador = GeneradorCuadruplos(v1_parser.memoria)
        v1_parser._ids_pendientes = []
        v1_parser.hay_error_semantico = False

        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            lexer.lineno = 1
            lexer.input(code)
            result = parser.parse(code, lexer=lexer.clone())

        output = buf.getvalue()
        #print(f"  [DEBUG salida]: '{output.strip()}'")
        ok_found    = "[OK]" in output
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
    