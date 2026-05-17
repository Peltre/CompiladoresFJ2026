# Archivo para realizar pruebas de funcionamiento sobre el compilador

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import v1_parser
from symbol_table import DirectorioFunciones

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

    ("TC-02", "Declaracion de variables",
     """
     programa test;
     vars
       x, y : entero;
       r     : flotante;
     inicio
       x = 5;
     fin
     """, True),

    ("TC-03", "Expresion aritmetica con precedencia",
     """
     programa test;
     vars
       r : entero;
     inicio
       r = 2 + 3 * 4;
     fin
     """, True),

    ("TC-04", "Condicional sin sino",
     """
     programa test;
     vars
       x : entero;
     inicio
       x = 10;
       si (x > 5) [
         escribe ("mayor");
       ]
     fin
     """, True),

    ("TC-05", "Condicional con sino",
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

    ("TC-06", "Ciclo mientras",
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

    ("TC-07", "escribe con letrero y expresion",
     """
     programa test;
     vars
       x : entero;
     inicio
       x = 42;
       escribe ("valor: ", x);
     fin
     """, True),

    ("TC-08", "Operadores relacionales == y !=",
     """
     programa test;
     vars
       a, b : entero;
     inicio
       a = 1;
       b = 2;
       si (a == b) [
         escribe ("iguales");
       ] sino [
         escribe ("distintos");
       ]
     fin
     """, True),

    ("TC-09", "Constantes flotantes",
     """
     programa test;
     vars
       f : flotante;
     inicio
       f = 3.14;
     fin
     """, True),

    ("TC-10", "Funcion con parametro entero (sin vars internas)",
     """
     programa test;
     doble (entero) {
       escribe ("ejecutando doble");
     };
     inicio
     fin
     """, True),

    ("TC-11", "Funcion nula",
     """
     programa test;
     saludo (nula) {
       escribe ("hola");
     };
     inicio
     fin
     """, True),

    ("TC-12", "Llamada a funcion",
     """
     programa test;
     miFuncion (nula) {
      escribe("hola");
     };
     inicio
      miFuncion();
     fin
     """, True),

    ("TC-13", "Expresion con parentesis",
     """
     programa test;
     vars
       r : entero;
     inicio
       r = (2 + 3) * 4;
     fin
     """, True),

    ("TC-14", "Comentario ignorado",
     """
     programa test;
     // este es un comentario
     inicio
       // otro comentario
     fin
     """, True),

    ("TC-15", "Ciclo anidado en condicional",
     """
     programa test;
     vars
       i, x : entero;
     inicio
       x = 10;
       si (x > 0) [
         mientras (i < x) haz [
           i = i + 1;
         ];
       ]
     fin
     """, True),

    # ── INVÁLIDOS ────────────────────────────────────────────────────────────
    ("TC-16", "Falta punto y coma tras programa id",
     """
     programa test
     inicio
     fin
     """, False),

    ("TC-17", "Caracter invalido @",
     """
     programa test;
     inicio
       x = 5 @ 3;
     fin
     """, False),

    ("TC-18", "Tipo invalido (booleano no existe)",
     """
     programa test;
     vars
       x : booleano;
     inicio
     fin
     """, False),

    ("TC-19", "Falta inicio",
     """
     programa test;
     fin
     """, False),

    ("TC-20", "Falta fin",
     """
     programa test;
     inicio
     """, False),
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
        v1_parser._ids_pendientes = []

        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            lexer.lineno = 1
            lexer.input(code)
            result = parser.parse(code, lexer=lexer.clone())

        output = buf.getvalue()
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
    