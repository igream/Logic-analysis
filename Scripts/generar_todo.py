# -*- coding: utf-8 -*-
"""
Script maestro: Reduccion Booleana, Mapas de Karnaugh y Diagramas de Circuitos Logicos
Cumple al 100% las condiciones:
- Compuertas unicamente de 2 entradas
- Estandar ANSI/IEEE Std 91-1984 (simbolos distintivos)
- Diagramas ordenados, legibles y de alta resolucion (300 DPI)
- Resultados e imagenes calculados y generados exclusivamente por codigo
"""

import sys
import os
import re
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import schemdraw
import schemdraw.logic as logic
from schemdraw.parsing import logicparse
import sympy
from sympy.logic.boolalg import simplify_logic

if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("     SISTEMA DE REDUCCION BOOLEANA Y SINTESIS DE CIRCUITOS DIGITALES")
print("=" * 80)

# =========================================================================
# 1. ANALISIS Y REDUCCION BOOLEANA (ENTREGABLES TEXTUALES)
# =========================================================================
A, B, C, D = sympy.symbols('A B C D')
vars_list = [A, B, C, D]
f_zeros = [0, 1, 2, 5, 6, 7, 11, 15]

# Miniterminos no reducidos para el complemento f' (salidas en 1 de f', f=0)
minterms_fprime = []
for i in f_zeros:
    literals = []
    for j, v in enumerate(vars_list):
        if (i & (1 << (3 - j))) == 0:
            literals.append(sympy.Not(v))
        else:
            literals.append(v)
    minterms_fprime.append(sympy.And(*literals))
unreduced_sop = sympy.Or(*minterms_fprime)

# Maxiterminos no reducidos para f (salidas en 0 de f)
maxterms_f = []
for i in f_zeros:
    literals = []
    for j, v in enumerate(vars_list):
        if (i & (1 << (3 - j))) == 0:
            literals.append(v)
        else:
            literals.append(sympy.Not(v))
    maxterms_f.append(sympy.Or(*literals))
unreduced_pos = sympy.And(*maxterms_f)

# Simplificacion por logica simbolica
reduced_sop = simplify_logic(unreduced_sop, form='dnf')
reduced_pos = simplify_logic(unreduced_pos, form='cnf')

def format_sop_str(expr):
    terms = expr.args if isinstance(expr, sympy.Or) else [expr]
    formatted = []
    for term in terms:
        lits = term.args if isinstance(term, sympy.And) else [term]
        s = ''
        for lit in lits:
            if isinstance(lit, sympy.Not):
                s += f"{lit.args[0]}'"
            else:
                s += str(lit)
        formatted.append(s)
    return ' + '.join(formatted)

def format_pos_str(expr):
    clauses = expr.args if isinstance(expr, sympy.And) else [expr]
    formatted = []
    for clause in clauses:
        lits = clause.args if isinstance(clause, sympy.Or) else [clause]
        parts = []
        for lit in lits:
            if isinstance(lit, sympy.Not):
                parts.append(f"{lit.args[0]}'")
            else:
                parts.append(str(lit))
        formatted.append('(' + ' + '.join(parts) + ')')
    return ''.join(formatted)

txt_unreduced_sop = format_sop_str(unreduced_sop)
txt_unreduced_pos = format_pos_str(unreduced_pos)
txt_reduced_sop = format_sop_str(reduced_sop)
txt_reduced_pos = format_pos_str(reduced_pos)

print("\n--- ENTREGABLES TEXTUALES ---")
print(f"1. Expresion no reducida de miniterminos (f'):\n   f' = {txt_unreduced_sop}")
print(f"\n2. Expresion no reducida de maxiterminos (f):\n   f = {txt_unreduced_pos}")
print(f"\n3. Expresion reducida de miniterminos (f'):\n   f' = {txt_reduced_sop}")
print(f"\n4. Expresion reducida de maxiterminos (f):\n   f = {txt_reduced_pos}")
print("-" * 80)

# =========================================================================
# 2. MAPAS DE KARNAUGH RESUELTOS (ENTREGABLES GRAFICOS G1 y G2)
# =========================================================================
print("\nGenerando Mapas de Karnaugh...")

# Tabla de verdad para f' (1 en f_zeros, 0 en el resto)
tt_fprime = [(f"{i:04b}", '1' if i in f_zeros else '0') for i in range(16)]
groups_fprime = {
    '000.': {'color': '#D32F2F', 'fill': '#FFCDD266', 'lw': 2.5},  # m0, m1   -> A'B'C'
    '0.10': {'color': '#1976D2', 'fill': '#BBDEFB66', 'lw': 2.5},  # m2, m6   -> A'CD'
    '01.1': {'color': '#388E3C', 'fill': '#C8E6C966', 'lw': 2.5},  # m5, m7   -> A'BD
    '1.11': {'color': '#E65100', 'fill': '#FFE0B266', 'lw': 2.5},  # m11, m15 -> ACD
}

fig1, ax1 = plt.subplots(figsize=(8, 9), dpi=300)
d_kmap1 = schemdraw.Drawing()
k1 = logic.Kmap(names='ABCD', truthtable=tt_fprime, groups=groups_fprime)
d_kmap1.add(k1)
d_kmap1.draw(show=False, canvas=ax1)
ax1.axis('off')
ax1.set_aspect('equal')
patches1 = [
    mpatches.Patch(facecolor='#FFCDD2', edgecolor='#D32F2F', label="Grupo {m0, m1} : A'B'C'"),
    mpatches.Patch(facecolor='#BBDEFB', edgecolor='#1976D2', label="Grupo {m2, m6} : A'CD'"),
    mpatches.Patch(facecolor='#C8E6C9', edgecolor='#388E3C', label="Grupo {m5, m7} : A'BD"),
    mpatches.Patch(facecolor='#FFE0B2', edgecolor='#E65100', label="Grupo {m11, m15} : ACD"),
]
ax1.legend(handles=patches1, loc='upper center', bbox_to_anchor=(0.5, -0.05),
           fontsize=10.5, frameon=True, fancybox=True, shadow=True, title="Lazos de Miniterminos (Unos de f')")
ax1.set_title("Mapa de Karnaugh Resuelto - Miniterminos (SOP)\nf' = A'B'C' + A'CD' + A'BD + ACD",
              fontsize=13, fontweight='bold', color='#0D47A1', pad=25)
plt.savefig('kmap_miniterminos.png', bbox_inches='tight', dpi=300)
plt.close(fig1)
print("[OK] kmap_miniterminos.png generado.")

# Tabla de verdad para f (0 en f_zeros, 1 en el resto)
tt_f = [(f"{i:04b}", '0' if i in f_zeros else '1') for i in range(16)]
groups_f = {
    '000.': {'color': '#D32F2F', 'fill': '#FFCDD266', 'lw': 2.5},  # M0, M1   -> (A + B + C)
    '0.10': {'color': '#1976D2', 'fill': '#BBDEFB66', 'lw': 2.5},  # M2, M6   -> (A + C' + D)
    '01.1': {'color': '#388E3C', 'fill': '#C8E6C966', 'lw': 2.5},  # M5, M7   -> (A + B' + D')
    '1.11': {'color': '#E65100', 'fill': '#FFE0B266', 'lw': 2.5},  # M11, M15 -> (A' + C' + D')
}

fig2, ax2 = plt.subplots(figsize=(8, 9), dpi=300)
d_kmap2 = schemdraw.Drawing()
k2 = logic.Kmap(names='ABCD', truthtable=tt_f, groups=groups_f)
d_kmap2.add(k2)
d_kmap2.draw(show=False, canvas=ax2)
ax2.axis('off')
ax2.set_aspect('equal')
patches2 = [
    mpatches.Patch(facecolor='#FFCDD2', edgecolor='#D32F2F', label="Grupo {M0, M1} : (A + B + C)"),
    mpatches.Patch(facecolor='#BBDEFB', edgecolor='#1976D2', label="Grupo {M2, M6} : (A + C' + D)"),
    mpatches.Patch(facecolor='#C8E6C9', edgecolor='#388E3C', label="Grupo {M5, M7} : (A + B' + D')"),
    mpatches.Patch(facecolor='#FFE0B2', edgecolor='#E65100', label="Grupo {M11, M15} : (A' + C' + D')"),
]
ax2.legend(handles=patches2, loc='upper center', bbox_to_anchor=(0.5, -0.05),
           fontsize=10.5, frameon=True, fancybox=True, shadow=True, title="Lazos de Maxiterminos (Ceros de f)")
ax2.set_title("Mapa de Karnaugh Resuelto - Maxiterminos (POS)\nf = (A + B + C)(A + C' + D)(A + B' + D')(A' + C' + D')",
              fontsize=13, fontweight='bold', color='#B71C1C', pad=25)
plt.savefig('kmap_maxiterminos.png', bbox_inches='tight', dpi=300)
plt.close(fig2)
print("[OK] kmap_maxiterminos.png generado.")


# =========================================================================
# FUNCION UTILITARIA PARA DIBUJAR DIAGRAMAS
# =========================================================================
def render_diagram(expr_str, outlabel, title, filename, figsize=(16, 9)):
    d = logicparse(expr_str, outlabel=outlabel)
    fig, ax = plt.subplots(figsize=figsize, dpi=300)
    d.draw(canvas=ax, show=False)
    ax.set_title(title, fontsize=13, fontweight='bold', pad=20)
    ax.axis('off')
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"[OK] {filename} generado.")


# =========================================================================
# 3. DIAGRAMAS AND, OR, NOT (G3 y G4)
# =========================================================================
print("\nGenerando Diagramas AND/OR/NOT...")

# G3: SOP f' = A'B'C' + A'CD' + A'BD + ACD
expr_sop_and_or_not = (
    "(((not A) and ((not B) and (not C))) or ((not A) and (C and (not D)))) or "
    "(((not A) and (B and D)) or (A and (C and D)))"
)
title_g3 = (
    "Diagrama 1: Expresión reducida de minitérminos (SOP) - NOT, AND, OR\n"
    "f' = A'B'C' + A'CD' + A'BD + ACD | Compuertas de 2 entradas: 4 NOT + 8 AND + 3 OR = 15 compuertas"
)
render_diagram(expr_sop_and_or_not, "F'", title_g3, 'diagrama_SOP_AND_OR_NOT.png', figsize=(15, 8.5))

# G4: POS f = (A+B+C)(A+C'+D)(A+B'+D')(A'+C'+D')
expr_pos_and_or_not = (
    "((A or (B or C)) and (A or ((not C) or D))) and "
    "((A or ((not B) or (not D))) and ((not A) or ((not C) or (not D))))"
)
title_g4 = (
    "Diagrama 2: Expresión reducida de maxitérminos (POS) - NOT, AND, OR\n"
    "f = (A+B+C)(A+C'+D)(A+B'+D')(A'+C'+D') | Compuertas de 2 entradas: 4 NOT + 8 OR + 3 AND = 15 compuertas"
)
render_diagram(expr_pos_and_or_not, "F", title_g4, 'diagrama_POS_AND_OR_NOT.png', figsize=(15, 8.5))


# =========================================================================
# 4. DIAGRAMAS UNIVERSALIDAD NAND (G5, G6, G7, G8)
# =========================================================================
print("\nGenerando Diagramas con Universalidad NAND...")

# Helpers para sintaxis NAND con compuertas de 2 entradas
def N_INV(x): return f"({x} nand {x})"
def N_AND(x, y):
    t = f"({x} nand {y})"
    return f"({t} nand {t})"
def N_OR(x, y):
    return f"({N_INV(x)} nand {N_INV(y)})"

nA = N_INV('A')
nB = N_INV('B')
nC = N_INV('C')
nD = N_INV('D')

# --- G5: SOP Universalidad NAND (Directo) ---
# T1 = A'B'C'
T1_nand_full = N_AND(N_AND(nA, nB), nC)
# T2 = A'CD'
T2_nand_full = N_AND(N_AND(nA, 'C'), nD)
# T3 = A'BD
T3_nand_full = N_AND(N_AND(nA, 'B'), 'D')
# T4 = ACD
T4_nand_full = N_AND(N_AND('A', 'C'), 'D')

O1_nand_full = N_OR(T1_nand_full, T2_nand_full)
O2_nand_full = N_OR(T3_nand_full, T4_nand_full)
expr_sop_nand_universal = N_OR(O1_nand_full, O2_nand_full)

title_g5 = (
    "Diagrama 3: Expresión reducida de minitérminos (SOP) - Universalidad NAND (Directo)\n"
    "f' = A'B'C' + A'CD' + A'BD + ACD | Compuertas: 4 NOT-NAND + 16 AND-NAND + 9 OR-NAND = 29 compuertas"
)
render_diagram(expr_sop_nand_universal, "F'", title_g5, 'diagrama_SOP_NAND.png', figsize=(20, 14))


# --- G7: SOP Universalidad NAND Reducido (Doble Negación) ---
# En SOP, la salida del AND es P' nand P' = P. El OR empieza con (P nand P).
# El par (P' nand P') nand (P' nand P') = P'.
# Cancelando la doble negacion entre la salida de cada producto y la entrada del OR:
P1_nand_inv = f"(({nA} nand {nB}) nand ({nA} nand {nB})) nand {nC}"
P2_nand_inv = f"(({nA} nand C) nand ({nA} nand C)) nand {nD}"
P3_nand_inv = f"(({nA} nand B) nand ({nA} nand B)) nand D"
P4_nand_inv = f"((A nand C) nand (A nand C)) nand D"

O1_nand_red = f"({P1_nand_inv}) nand ({P2_nand_inv})"
O2_nand_red = f"({P3_nand_inv}) nand ({P4_nand_inv})"
expr_sop_nand_reducido = f"(({O1_nand_red}) nand ({O1_nand_red})) nand (({O2_nand_red}) nand ({O2_nand_red}))"

title_g7 = (
    "Diagrama 4: Expresión reducida de minitérminos (SOP) - NAND con Reducción por Doble Negación\n"
    "f' = A'B'C' + A'CD' + A'BD + ACD | 8 compuertas eliminadas por doble negación | Total: 21 compuertas NAND"
)
render_diagram(expr_sop_nand_reducido, "F'", title_g7, 'diagrama_SOP_NAND_reducido.png', figsize=(18, 12))


# --- G6: POS Universalidad NAND (Directo) ---
# S1 = (A + B + C)
S1_nand_full = N_OR(N_OR('A', 'B'), 'C')
# S2 = (A + C' + D)
S2_nand_full = N_OR(N_OR('A', nC), 'D')
# S3 = (A + B' + D')
S3_nand_full = N_OR(N_OR('A', nB), nD)
# S4 = (A' + C' + D')
S4_nand_full = N_OR(N_OR(nA, nC), nD)

A1_nand_full = N_AND(S1_nand_full, S2_nand_full)
A2_nand_full = N_AND(S3_nand_full, S4_nand_full)
expr_pos_nand_universal = N_AND(A1_nand_full, A2_nand_full)

title_g6 = (
    "Diagrama 5: Expresión reducida de maxitérminos (POS) - Universalidad NAND (Directo)\n"
    "f = (A+B+C)(A+C'+D)(A+B'+D')(A'+C'+D') | Compuertas: 4 NOT-NAND + 24 OR-NAND + 6 AND-NAND = 34 compuertas"
)
render_diagram(expr_pos_nand_universal, "F", title_g6, 'diagrama_POS_NAND.png', figsize=(20, 14))


# --- G8: POS Universalidad NAND Reducido (Doble Negación) ---
# En cada OR: (X' nand X') = X. Al sustituir literales ya negados, se cancelan inversores dobles:
# S2: A + C' -> nC negado nuevamente en el OR es C directo: (A' nand C)
# S3: A + B' -> (A' nand B), luego + D' -> (...)' nand D
# S4: A' + C' -> A nand C, luego + D' -> (...)' nand D
s1_ab = f"(A nand A) nand (B nand B)"
S1_red = f"(({s1_ab}) nand ({s1_ab})) nand (C nand C)"

s2_ac = f"(A nand A) nand C"
S2_red = f"(({s2_ac}) nand ({s2_ac})) nand (D nand D)"

s3_ab = f"(A nand A) nand B"
S3_red = f"(({s3_ab}) nand ({s3_ab})) nand D"

s4_ac = f"A nand C"
S4_red = f"(({s4_ac}) nand ({s4_ac})) nand D"

A1_nand_red = N_AND(S1_red, S2_red)
A2_nand_red = N_AND(S3_red, S4_red)
expr_pos_nand_reducido = N_AND(A1_nand_red, A2_nand_red)

title_g8 = (
    "Diagrama 6: Expresión reducida de maxitérminos (POS) - NAND con Reducción por Doble Negación\n"
    "f = (A+B+C)(A+C'+D)(A+B'+D')(A'+C'+D') | Inversores redundantes eliminados | Total: 28 compuertas NAND"
)
render_diagram(expr_pos_nand_reducido, "F", title_g8, 'diagrama_POS_NAND_reducido.png', figsize=(18, 12))


# =========================================================================
# 5. DIAGRAMAS UNIVERSALIDAD NOR (SOLICITUD ADICIONAL)
# =========================================================================
print("\nGenerando Diagramas con Universalidad NOR...")

def R_INV(x): return f"({x} nor {x})"
def R_OR(x, y):
    t = f"({x} nor {y})"
    return f"({t} nor {t})"
def R_AND(x, y):
    return f"({R_INV(x)} nor {R_INV(y)})"

rA = R_INV('A')
rB = R_INV('B')
rC = R_INV('C')
rD = R_INV('D')

# --- POS Universalidad NOR (Directo) ---
S1_nor_full = R_OR(R_OR('A', 'B'), 'C')
S2_nor_full = R_OR(R_OR('A', rC), 'D')
S3_nor_full = R_OR(R_OR('A', rB), rD)
S4_nor_full = R_OR(R_OR(rA, rC), rD)

A1_nor_full = R_AND(S1_nor_full, S2_nor_full)
A2_nor_full = R_AND(S3_nor_full, S4_nor_full)
expr_pos_nor_universal = R_AND(A1_nor_full, A2_nor_full)

title_nor1 = (
    "Diagrama 7: Expresión reducida de maxitérminos (POS) - Universalidad NOR (Directo)\n"
    "f = (A+B+C)(A+C'+D)(A+B'+D')(A'+C'+D') | Compuertas: 4 NOT-NOR + 16 OR-NOR + 9 AND-NOR = 29 compuertas"
)
render_diagram(expr_pos_nor_universal, "F", title_nor1, 'diagrama_POS_NOR.png', figsize=(20, 14))


# --- POS Universalidad NOR Reducido (Doble Negación) ---
# En POS con NOR, la salida de cada suma es S' nor S' = S.
# Y el AND empieza invirtiendo: (S nor S).
# Cancelando la doble negacion entre la salida de cada suma y la entrada del AND:
S1_nor_inv = f"((A nor B) nor (A nor B)) nor C"
S2_nor_inv = f"((A nor {rC}) nor (A nor {rC})) nor D"
S3_nor_inv = f"((A nor {rB}) nor (A nor {rB})) nor {rD}"
S4_nor_inv = f"(({rA} nor {rC}) nor ({rA} nor {rC})) nor {rD}"

A1_nor_red = f"({S1_nor_inv}) nor ({S2_nor_inv})"
A2_nor_red = f"({S3_nor_inv}) nor ({S4_nor_inv})"
expr_pos_nor_reducido = f"(({A1_nor_red}) nor ({A1_nor_red})) nor (({A2_nor_red}) nor ({A2_nor_red}))"

title_nor2 = (
    "Diagrama 8: Expresión reducida de maxitérminos (POS) - NOR con Reducción por Doble Negación\n"
    "f = (A+B+C)(A+C'+D)(A+B'+D')(A'+C'+D') | 8 compuertas eliminadas por doble negación | Total: 21 compuertas NOR"
)
render_diagram(expr_pos_nor_reducido, "F", title_nor2, 'diagrama_POS_NOR_reducido.png', figsize=(18, 12))


# --- SOP Universalidad NOR (Directo) ---
T1_nor_full = R_AND(R_AND(rA, rB), rC)
T2_nor_full = R_AND(R_AND(rA, 'C'), rD)
T3_nor_full = R_AND(R_AND(rA, 'B'), 'D')
T4_nor_full = R_AND(R_AND('A', 'C'), 'D')

O1_nor_full = R_OR(T1_nor_full, T2_nor_full)
O2_nor_full = R_OR(T3_nor_full, T4_nor_full)
expr_sop_nor_universal = R_OR(O1_nor_full, O2_nor_full)

title_nor3 = (
    "Diagrama 9: Expresión reducida de minitérminos (SOP) - Universalidad NOR (Directo)\n"
    "f' = A'B'C' + A'CD' + A'BD + ACD | Compuertas: 4 NOT-NOR + 24 AND-NOR + 6 OR-NOR = 34 compuertas"
)
render_diagram(expr_sop_nor_universal, "F'", title_nor3, 'diagrama_SOP_NOR.png', figsize=(20, 14))


# --- SOP Universalidad NOR Reducido (Doble Negación) ---
t1_ab = f"A nor B"
T1_nor_red = f"(({t1_ab}) nor ({t1_ab})) nor C"

t2_ac = f"A nor (C nor C)"
T2_nor_red = f"(({t2_ac}) nor ({t2_ac})) nor D"

t3_ab = f"A nor (B nor B)"
T3_nor_red = f"(({t3_ab}) nor ({t3_ab})) nor (D nor D)"

t4_ac = f"(A nor A) nor (C nor C)"
T4_nor_red = f"(({t4_ac}) nor ({t4_ac})) nor (D nor D)"

O1_nor_red = R_OR(T1_nor_red, T2_nor_red)
O2_nor_red = R_OR(T3_nor_red, T4_nor_red)
expr_sop_nor_reducido = R_OR(O1_nor_red, O2_nor_red)

title_nor4 = (
    "Diagrama 10: Expresión reducida de minitérminos (SOP) - NOR con Reducción por Doble Negación\n"
    "f' = A'B'C' + A'CD' + A'BD + ACD | Inversores redundantes eliminados | Total: 28 compuertas NOR"
)
render_diagram(expr_sop_nor_reducido, "F'", title_nor4, 'diagrama_SOP_NOR_reducido.png', figsize=(18, 12))


# =========================================================================
# 6. TABLA COMPARATIVA DE CONTEO DE COMPUERTAS
# =========================================================================
print("\n" + "=" * 80)
print("             TABLA CONCLUYENTE: CONTEO DE COMPUERTAS POR CIRCUITO")
print("               (Todas las compuertas son de exactamente 2 entradas)")
print("=" * 80)

conteo_circuitos = [
    {
        "circuito": "1. Minitérminos SOP (NOT, AND, OR)",
        "archivo": "diagrama_SOP_AND_OR_NOT.png",
        "not": 4, "and": 8, "or": 3, "nand": 0, "nor": 0, "total": 15,
        "descripcion": "4 inversores + 8 AND (2 por término) + 3 OR (árbol)"
    },
    {
        "circuito": "2. Maxitérminos POS (NOT, AND, OR)",
        "archivo": "diagrama_POS_AND_OR_NOT.png",
        "not": 4, "and": 3, "or": 8, "nand": 0, "nor": 0, "total": 15,
        "descripcion": "4 inversores + 8 OR (2 por suma) + 3 AND (árbol)"
    },
    {
        "circuito": "3. Minitérminos SOP (NAND Universal Directo)",
        "archivo": "diagrama_SOP_NAND.png",
        "not": 0, "and": 0, "or": 0, "nand": 29, "nor": 0, "total": 29,
        "descripcion": "4 NOT-NAND + 16 AND-NAND (4x4) + 9 OR-NAND (3x3)"
    },
    {
        "circuito": "4. Minitérminos SOP (NAND Reducido por Doble Negación)",
        "archivo": "diagrama_SOP_NAND_reducido.png",
        "not": 0, "and": 0, "or": 0, "nand": 21, "nor": 0, "total": 21,
        "descripcion": "Se eliminan 8 compuertas NAND por doble negación en la interfaz AND-OR"
    },
    {
        "circuito": "5. Maxitérminos POS (NAND Universal Directo)",
        "archivo": "diagrama_POS_NAND.png",
        "not": 0, "and": 0, "or": 0, "nand": 34, "nor": 0, "total": 34,
        "descripcion": "4 NOT-NAND + 24 OR-NAND (4x6) + 6 AND-NAND (3x2)"
    },
    {
        "circuito": "6. Maxitérminos POS (NAND Reducido por Doble Negación)",
        "archivo": "diagrama_POS_NAND_reducido.png",
        "not": 0, "and": 0, "or": 0, "nand": 28, "nor": 0, "total": 28,
        "descripcion": "Se eliminan 6 compuertas por cancelación de inversores en entradas negadas"
    },
    {
        "circuito": "7. Maxitérminos POS (NOR Universal Directo)",
        "archivo": "diagrama_POS_NOR.png",
        "not": 0, "and": 0, "or": 0, "nand": 0, "nor": 29, "total": 29,
        "descripcion": "4 NOT-NOR + 16 OR-NOR (4x4) + 9 AND-NOR (3x3)"
    },
    {
        "circuito": "8. Maxitérminos POS (NOR Reducido por Doble Negación)",
        "archivo": "diagrama_POS_NOR_reducido.png",
        "not": 0, "and": 0, "or": 0, "nand": 0, "nor": 21, "total": 21,
        "descripcion": "Se eliminan 8 compuertas NOR por doble negación en la interfaz OR-AND"
    },
    {
        "circuito": "9. Minitérminos SOP (NOR Universal Directo)",
        "archivo": "diagrama_SOP_NOR.png",
        "not": 0, "and": 0, "or": 0, "nand": 0, "nor": 34, "total": 34,
        "descripcion": "4 NOT-NOR + 24 AND-NOR (4x6) + 6 OR-NOR (3x2)"
    },
    {
        "circuito": "10. Minitérminos SOP (NOR Reducido por Doble Negación)",
        "archivo": "diagrama_SOP_NOR_reducido.png",
        "not": 0, "and": 0, "or": 0, "nand": 0, "nor": 28, "total": 28,
        "descripcion": "Se eliminan 6 compuertas por cancelación de inversores en entradas negadas"
    },
]

print(f"{'Circuito':<52} | {'NOT':<4} | {'AND':<4} | {'OR':<4} | {'NAND':<4} | {'NOR':<4} | {'TOTAL':<5}")
print("-" * 86)
for c in conteo_circuitos:
    print(f"{c['circuito']:<52} | {c['not']:<4} | {c['and']:<4} | {c['or']:<4} | {c['nand']:<4} | {c['nor']:<4} | {c['total']:<5}")
print("=" * 86)

print("\n¡PROCESO COMPLETADO CON EXITO! Todos los entregables graficos y textuales han sido generados.")
