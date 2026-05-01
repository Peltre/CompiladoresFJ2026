from lexer import lexer
from parser import parser

def compilar(codigo):
    parser.parse(codigo, lexer=lexer)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            compilar(f.read())
    else:
        print("Uso: python main.py programa.pat")