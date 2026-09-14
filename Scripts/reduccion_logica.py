'''
Reductor de Expresiones Logicas Booleanas en Python
Expresion: (A+B+C+D)(A+B+C+D')(A+B+C'+D)(A+B'+C+D')(A+B'+C'+D)(A+B'+C'+D')(A'+B+C'+D')(A'+B'+C'+D')
'''

import sys
import subprocess

# 1. Verificacion e instalacion automatica de la libreria SymPy
try:
    import sympy
except ImportError:
    print("[*] La libreria 'sympy' no esta instalada. Instalando automaticamente con pip...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "sympy"])
    import sympy

from sympy.logic.boolalg import Or, And, Not, simplify_logic
from sympy.abc import A, B, C, D


def sort_key_literal(lit):
    """Ordena las variables alfabeticamente (A, B, C, D)."""
    sym = lit.args[0] if isinstance(lit, Not) else lit
    return (str(sym), 1 if isinstance(lit, Not) else 0)


def format_pos(expr):
    """Formatea una expresion booleana CNF/POS con notacion clasica: (A + B + C)..."""
    clauses = expr.args if isinstance(expr, And) else [expr]
    formatted_clauses = []
    
    for clause in clauses:
        literals = list(clause.args) if isinstance(clause, Or) else [clause]
        literals.sort(key=sort_key_literal)
        terms = [f"{lit.args[0]}'" if isinstance(lit, Not) else str(lit) for lit in literals]
        formatted_clauses.append(f"({' + '.join(terms)})")
        
    return "".join(formatted_clauses)


def format_sop(expr):
    """Formatea una expresion booleana DNF/SOP con notacion clasica: AB'C + ..."""
    clauses = expr.args if isinstance(expr, Or) else [expr]
    formatted_clauses = []
    
    for clause in clauses:
        literals = list(clause.args) if isinstance(clause, And) else [clause]
        literals.sort(key=sort_key_literal)
        terms = [f"{lit.args[0]}'" if isinstance(lit, Not) else str(lit) for lit in literals]
        formatted_clauses.append("".join(terms))
        
    return " + ".join(formatted_clauses)


def main():
    print("=" * 72)
    print("      REDUCCION DE EXPRESION BOOLEANA CON PYTHON Y SYMPY")
    print("=" * 72)

    # Expresion original (Producto de Sumas / Maxiterminos):
    # F = (A+B+C+D)(A+B+C+D')(A+B+C'+D)(A+B'+C+D')(A+B'+C'+D)(A+B'+C'+D')(A'+B+C'+D')(A'+B'+C'+D')
    expr_original = And(
        Or(A, B, C, D),        # M0  = (0,0,0,0)
        Or(A, B, C, ~D),       # M1  = (0,0,0,1)
        Or(A, B, ~C, D),       # M2  = (0,0,1,0)
        Or(A, ~B, C, ~D),      # M5  = (0,1,0,1)
        Or(A, ~B, ~C, D),      # M6  = (0,1,1,0)
        Or(A, ~B, ~C, ~D),     # M7  = (0,1,1,1)
        Or(~A, B, ~C, ~D),     # M11 = (1,0,1,1)
        Or(~A, ~B, ~C, ~D)     # M15 = (1,1,1,1)
    )

    print("\n1. EXPRESION ORIGINAL:")
    print("   (A+B+C+D)(A+B+C+D')(A+B+C'+D)(A+B'+C+D')(A+B'+C'+D)(A+B'+C'+D')(A'+B+C'+D')(A'+B'+C'+D')")
    print(f"   Representacion interna: {expr_original}")

    # Reduccion a forma Producto de Sumas (POS / CNF)
    pos_minima = simplify_logic(expr_original, form="cnf")

    # Reduccion a forma Suma de Productos (SOP / DNF)
    sop_minima = simplify_logic(expr_original, form="dnf")

    print("\n2. EXPRESION MINIMIZADA:")
    print("   " + "-" * 66)
    print("   [A] Forma Producto de Sumas (POS / CNF):")
    print(f"       Resultado : {format_pos(pos_minima)}")
    print(f"       En SymPy  : {pos_minima}")
    print("   " + "-" * 66)
    print("   [B] Forma Suma de Productos (SOP / DNF):")
    print(f"       Resultado : {format_sop(sop_minima)}")
    print(f"       En SymPy  : {sop_minima}")
    print("   " + "-" * 66)

    # Maxiterminos (donde F = 0) y Miniterminos (donde F = 1)
    maxterminos = [0, 1, 2, 5, 6, 7, 11, 15]
    minterminos = [i for i in range(16) if i not in maxterminos]

    print("\n3. DETALLE DE TERMINOS CANONICOS:")
    print(f"   Maxiterminos (F = 0) : M({', '.join(map(str, maxterminos))})")
    print(f"   Miniterminos (F = 1) : m({', '.join(map(str, minterminos))})")

    print("\n4. MAPA DE KARNAUGH Y AGRUPAMIENTOS (Para los ceros de F):")
    print("   Se agrupan los 8 ceros en 4 lazos/pares de 2 celdas:")
    print("   - Lazos con A = 0:")
    print("     * {M0, M1}   (0000, 0001) -> (A + B + C)")
    print("     * {M2, M6}   (0010, 0110) -> (A + C' + D)")
    print("     * {M5, M7}   (0101, 0111) -> (A + B' + D')")
    print("   - Lazo con A = 1:")
    print("     * {M11, M15} (1011, 1111) -> (A' + C' + D')")
    print(f"\n   -> Expresion minima POS final: {format_pos(pos_minima)}")

    print("\n5. TABLA DE VERDAD COMPLETA:")
    print("   +---+---+---+---+---+")
    print("   | A | B | C | D | F |")
    print("   +---+---+---+---+---+")
    for i in range(16):
        a_val = (i >> 3) & 1
        b_val = (i >> 2) & 1
        c_val = (i >> 1) & 1
        d_val = i & 1
        f_val = 0 if i in maxterminos else 1
        print(f"   | {a_val} | {b_val} | {c_val} | {d_val} | {f_val} |")
    print("   +---+---+---+---+---+")
    print("=" * 72)


if __name__ == "__main__":
    main()
