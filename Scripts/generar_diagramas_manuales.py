# -*- coding: utf-8 -*-
"""
Generador de diagramas logicos manuales limpios y ordenados
Garantiza:
- Todas las compuertas son estrictamente de 2 entradas
- Símbolos ANSI/IEEE Std 91-1984
- Orientación horizontal siempre hacia la derecha (sin rotaciones no deseadas)
- Conexiones ortogonales limpias
- Conteo exacto de compuertas
"""

import sys
import os
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.logic as logic

if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def create_drawing():
    return schemdraw.Drawing()

def draw_inv_nand(d, x, y, label_text=None, in_wire=None):
    """Dibuja un inversor implementado con una compuerta NAND de 2 entradas."""
    g = d.add(logic.Nand(inputs=2).right().at((x, y)))
    d.add(logic.Line().at(g.in1).to(g.in2))
    mid_y = (g.in1[1] + g.in2[1]) / 2.0
    mid_pt = (g.in1[0], mid_y)
    if in_wire is not None:
        d.add(logic.Wire('c').at(mid_pt).to(in_wire))
    elif label_text is not None:
        d.add(logic.Line().left(0.7).at(mid_pt).label(label_text, loc='left'))
    return g

def draw_inv_nor(d, x, y, label_text=None, in_wire=None):
    """Dibuja un inversor implementado con una compuerta NOR de 2 entradas."""
    g = d.add(logic.Nor(inputs=2).right().at((x, y)))
    d.add(logic.Line().at(g.in1).to(g.in2))
    mid_y = (g.in1[1] + g.in2[1]) / 2.0
    mid_pt = (g.in1[0], mid_y)
    if in_wire is not None:
        d.add(logic.Wire('c').at(mid_pt).to(in_wire))
    elif label_text is not None:
        d.add(logic.Line().left(0.7).at(mid_pt).label(label_text, loc='left'))
    return g

def draw_gate_nand(d, x, y, in1=None, in2=None, lbl1=None, lbl2=None):
    """Dibuja una compuerta NAND de 2 entradas con conexiones limpias."""
    g = d.add(logic.Nand(inputs=2).right().at((x, y)))
    if in1 is not None:
        d.add(logic.Wire('c').at(g.in1).to(in1.out))
    elif lbl1 is not None:
        d.add(logic.Line().left(0.7).at(g.in1).label(lbl1, loc='left'))
    if in2 is not None:
        d.add(logic.Wire('c').at(g.in2).to(in2.out))
    elif lbl2 is not None:
        d.add(logic.Line().left(0.7).at(g.in2).label(lbl2, loc='left'))
    return g

def draw_gate_nor(d, x, y, in1=None, in2=None, lbl1=None, lbl2=None):
    """Dibuja una compuerta NOR de 2 entradas con conexiones limpias."""
    g = d.add(logic.Nor(inputs=2).right().at((x, y)))
    if in1 is not None:
        d.add(logic.Wire('c').at(g.in1).to(in1.out))
    elif lbl1 is not None:
        d.add(logic.Line().left(0.7).at(g.in1).label(lbl1, loc='left'))
    if in2 is not None:
        d.add(logic.Wire('c').at(g.in2).to(in2.out))
    elif lbl2 is not None:
        d.add(logic.Line().left(0.7).at(g.in2).label(lbl2, loc='left'))
    return g

def save_clean_diagram(d, filename, title, figsize=(18, 12)):
    fig, ax = plt.subplots(figsize=figsize, dpi=300)
    d.draw(canvas=ax, show=False)
    ax.set_title(title, fontsize=13, fontweight='bold', pad=22)
    ax.axis('off')
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"[OK] {filename} generado exitosamente.")


# =========================================================================
# 1. SOP NAND UNIVERSAL (DIRECTO) - 29 compuertas NAND
# =========================================================================
d_sop_nand = create_drawing()

# Columna 0: Inversores de entrada
invA = draw_inv_nand(d_sop_nand, 1.5, 14, label_text='A')
invB = draw_inv_nand(d_sop_nand, 1.5, 12, label_text='B')
invC = draw_inv_nand(d_sop_nand, 1.5, 10, label_text='C')
invD = draw_inv_nand(d_sop_nand, 1.5, 8, label_text='D')

# Termino 1: A'B'C' -> AND(B',C') luego AND(A', B'C')
g1 = draw_gate_nand(d_sop_nand, 5.5, 14, in1=invB, in2=invC)
g2 = draw_inv_nand(d_sop_nand, 8.5, 14, in_wire=g1.out)
g3 = draw_gate_nand(d_sop_nand, 11.5, 13.5, in1=invA, in2=g2)
t1 = draw_inv_nand(d_sop_nand, 14.5, 13.5, in_wire=g3.out)

# Termino 2: A'CD' -> AND(A', C) luego AND(A'C, D')
g5 = draw_gate_nand(d_sop_nand, 5.5, 10, in1=invA, lbl2='C')
g6 = draw_inv_nand(d_sop_nand, 8.5, 10, in_wire=g5.out)
g7 = draw_gate_nand(d_sop_nand, 11.5, 9.5, in1=g6, in2=invD)
t2 = draw_inv_nand(d_sop_nand, 14.5, 9.5, in_wire=g7.out)

# Termino 3: A'BD -> AND(A', B) luego AND(A'B, D)
g9 = draw_gate_nand(d_sop_nand, 5.5, 6, in1=invA, lbl2='B')
g10 = draw_inv_nand(d_sop_nand, 8.5, 6, in_wire=g9.out)
g11 = draw_gate_nand(d_sop_nand, 11.5, 5.5, in1=g10, lbl2='D')
t3 = draw_inv_nand(d_sop_nand, 14.5, 5.5, in_wire=g11.out)

# Termino 4: ACD -> AND(A, C) luego AND(AC, D)
g13 = draw_gate_nand(d_sop_nand, 5.5, 2, lbl1='A', lbl2='C')
g14 = draw_inv_nand(d_sop_nand, 8.5, 2, in_wire=g13.out)
g15 = draw_gate_nand(d_sop_nand, 11.5, 1.5, in1=g14, lbl2='D')
t4 = draw_inv_nand(d_sop_nand, 14.5, 1.5, in_wire=g15.out)

# Arbol OR (3 compuertas OR = 9 compuertas NAND)
# OR(T1, T2)
inv_t1 = draw_inv_nand(d_sop_nand, 17.5, 13.5, in_wire=t1.out)
inv_t2 = draw_inv_nand(d_sop_nand, 17.5, 9.5, in_wire=t2.out)
o1 = draw_gate_nand(d_sop_nand, 20.5, 11.5, in1=inv_t1, in2=inv_t2)

# OR(T3, T4)
inv_t3 = draw_inv_nand(d_sop_nand, 17.5, 5.5, in_wire=t3.out)
inv_t4 = draw_inv_nand(d_sop_nand, 17.5, 1.5, in_wire=t4.out)
o2 = draw_gate_nand(d_sop_nand, 20.5, 3.5, in1=inv_t3, in2=inv_t4)

# OR(O1, O2)
inv_o1 = draw_inv_nand(d_sop_nand, 23.5, 11.5, in_wire=o1.out)
inv_o2 = draw_inv_nand(d_sop_nand, 23.5, 3.5, in_wire=o2.out)
f_out = draw_gate_nand(d_sop_nand, 26.5, 7.5, in1=inv_o1, in2=inv_o2)
d_sop_nand.add(logic.Line().right(0.7).at(f_out.out).label("F'", loc='right'))

title_sop_nand = (
    "Diagrama 3: Expresión reducida de minitérminos (SOP) - Universalidad NAND (Directo)\n"
    "f' = A'B'C' + A'CD' + A'BD + ACD | Conteo: 4 NOT + 16 AND + 9 OR = 29 compuertas NAND"
)
save_clean_diagram(d_sop_nand, 'diagrama_SOP_NAND.png', title_sop_nand)


# =========================================================================
# 2. SOP NAND REDUCIDO (DOBLE NEGACION) - 21 compuertas NAND
# =========================================================================
d_sop_nand_red = create_drawing()

# Inversores de entrada
invA_r = draw_inv_nand(d_sop_nand_red, 1.5, 14, label_text='A')
invB_r = draw_inv_nand(d_sop_nand_red, 1.5, 12, label_text='B')
invC_r = draw_inv_nand(d_sop_nand_red, 1.5, 10, label_text='C')
invD_r = draw_inv_nand(d_sop_nand_red, 1.5, 8, label_text='D')

# Terminos: el ultimo inversor del AND se cancela con el inversor de entrada del OR!
# Termino 1: A'B'C' -> g3 entrega directamente (A'B'C')'
g1_r = draw_gate_nand(d_sop_nand_red, 5.5, 14, in1=invB_r, in2=invC_r)
g2_r = draw_inv_nand(d_sop_nand_red, 8.5, 14, in_wire=g1_r.out)
g3_r = draw_gate_nand(d_sop_nand_red, 11.5, 13.5, in1=invA_r, in2=g2_r)

# Termino 2: A'CD' -> g7 entrega (A'CD')'
g5_r = draw_gate_nand(d_sop_nand_red, 5.5, 10, in1=invA_r, lbl2='C')
g6_r = draw_inv_nand(d_sop_nand_red, 8.5, 10, in_wire=g5_r.out)
g7_r = draw_gate_nand(d_sop_nand_red, 11.5, 9.5, in1=g6_r, in2=invD_r)

# Termino 3: A'BD -> g11 entrega (A'BD)'
g9_r = draw_gate_nand(d_sop_nand_red, 5.5, 6, in1=invA_r, lbl2='B')
g10_r = draw_inv_nand(d_sop_nand_red, 8.5, 6, in_wire=g9_r.out)
g11_r = draw_gate_nand(d_sop_nand_red, 11.5, 5.5, in1=g10_r, lbl2='D')

# Termino 4: ACD -> g15 entrega (ACD)'
g13_r = draw_gate_nand(d_sop_nand_red, 5.5, 2, lbl1='A', lbl2='C')
g14_r = draw_inv_nand(d_sop_nand_red, 8.5, 2, in_wire=g13_r.out)
g15_r = draw_gate_nand(d_sop_nand_red, 11.5, 1.5, in1=g14_r, lbl2='D')

# Primer nivel de OR: las entradas negadas entran directamente a la NAND!
# (T1)' nand (T2)' = T1 + T2
o1_r = draw_gate_nand(d_sop_nand_red, 16.5, 11.5, in1=g3_r, in2=g7_r)
o2_r = draw_gate_nand(d_sop_nand_red, 16.5, 3.5, in1=g11_r, in2=g15_r)

# Segundo nivel de OR (requiere inversor en entradas para la suma de o1 y o2)
inv_o1_r = draw_inv_nand(d_sop_nand_red, 19.5, 11.5, in_wire=o1_r.out)
inv_o2_r = draw_inv_nand(d_sop_nand_red, 19.5, 3.5, in_wire=o2_r.out)
f_out_r = draw_gate_nand(d_sop_nand_red, 22.5, 7.5, in1=inv_o1_r, in2=inv_o2_r)
d_sop_nand_red.add(logic.Line().right(0.7).at(f_out_r.out).label("F'", loc='right'))

title_sop_nand_red = (
    "Diagrama 4: Expresión reducida de minitérminos (SOP) - NAND Reducido (Doble Negación)\n"
    "f' = A'B'C' + A'CD' + A'BD + ACD | 8 compuertas eliminadas por cancelación | Total: 21 compuertas NAND"
)
save_clean_diagram(d_sop_nand_red, 'diagrama_SOP_NAND_reducido.png', title_sop_nand_red)


# =========================================================================
# 3. POS NOR UNIVERSAL (DIRECTO) - 29 compuertas NOR
# =========================================================================
d_pos_nor = create_drawing()

# Inversores de entrada
invA_nor = draw_inv_nor(d_pos_nor, 1.5, 14, label_text='A')
invB_nor = draw_inv_nor(d_pos_nor, 1.5, 12, label_text='B')
invC_nor = draw_inv_nor(d_pos_nor, 1.5, 10, label_text='C')
invD_nor = draw_inv_nor(d_pos_nor, 1.5, 8, label_text='D')

# Suma 1: (A + B + C) -> OR(B, C) luego OR(A, B+C)
s1 = draw_gate_nor(d_pos_nor, 5.5, 14, lbl1='B', lbl2='C')
s2 = draw_inv_nor(d_pos_nor, 8.5, 14, in_wire=s1.out)
s3 = draw_gate_nor(d_pos_nor, 11.5, 13.5, lbl1='A', in2=s2)
sum1 = draw_inv_nor(d_pos_nor, 14.5, 13.5, in_wire=s3.out)

# Suma 2: (A + C' + D) -> OR(C', D) luego OR(A, C'+D)
s5 = draw_gate_nor(d_pos_nor, 5.5, 10, in1=invC_nor, lbl2='D')
s6 = draw_inv_nor(d_pos_nor, 8.5, 10, in_wire=s5.out)
s7 = draw_gate_nor(d_pos_nor, 11.5, 9.5, lbl1='A', in2=s6)
sum2 = draw_inv_nor(d_pos_nor, 14.5, 9.5, in_wire=s7.out)

# Suma 3: (A + B' + D') -> OR(B', D') luego OR(A, B'+D')
s9 = draw_gate_nor(d_pos_nor, 5.5, 6, in1=invB_nor, in2=invD_nor)
s10 = draw_inv_nor(d_pos_nor, 8.5, 6, in_wire=s9.out)
s11 = draw_gate_nor(d_pos_nor, 11.5, 5.5, lbl1='A', in2=s10)
sum3 = draw_inv_nor(d_pos_nor, 14.5, 5.5, in_wire=s11.out)

# Suma 4: (A' + C' + D') -> OR(A', C') luego OR(A'+C', D')
s13 = draw_gate_nor(d_pos_nor, 5.5, 2, in1=invA_nor, in2=invC_nor)
s14 = draw_inv_nor(d_pos_nor, 8.5, 2, in_wire=s13.out)
s15 = draw_gate_nor(d_pos_nor, 11.5, 1.5, in1=s14, in2=invD_nor)
sum4 = draw_inv_nor(d_pos_nor, 14.5, 1.5, in_wire=s15.out)

# Arbol AND (3 compuertas AND = 9 compuertas NOR)
inv_sum1 = draw_inv_nor(d_pos_nor, 17.5, 13.5, in_wire=sum1.out)
inv_sum2 = draw_inv_nor(d_pos_nor, 17.5, 9.5, in_wire=sum2.out)
and1 = draw_gate_nor(d_pos_nor, 20.5, 11.5, in1=inv_sum1, in2=inv_sum2)

inv_sum3 = draw_inv_nor(d_pos_nor, 17.5, 5.5, in_wire=sum3.out)
inv_sum4 = draw_inv_nor(d_pos_nor, 17.5, 1.5, in_wire=sum4.out)
and2 = draw_gate_nor(d_pos_nor, 20.5, 3.5, in1=inv_sum3, in2=inv_sum4)

inv_and1 = draw_inv_nor(d_pos_nor, 23.5, 11.5, in_wire=and1.out)
inv_and2 = draw_inv_nor(d_pos_nor, 23.5, 3.5, in_wire=and2.out)
f_pos_out = draw_gate_nor(d_pos_nor, 26.5, 7.5, in1=inv_and1, in2=inv_and2)
d_pos_nor.add(logic.Line().right(0.7).at(f_pos_out.out).label("F", loc='right'))

title_pos_nor = (
    "Diagrama 7: Expresión reducida de maxitérminos (POS) - Universalidad NOR (Directo)\n"
    "f = (A+B+C)(A+C'+D)(A+B'+D')(A'+C'+D') | Conteo: 4 NOT + 16 OR + 9 AND = 29 compuertas NOR"
)
save_clean_diagram(d_pos_nor, 'diagrama_POS_NOR.png', title_pos_nor)


# =========================================================================
# 4. POS NOR REDUCIDO (DOBLE NEGACION) - 21 compuertas NOR
# =========================================================================
d_pos_nor_red = create_drawing()

# Inversores de entrada
invA_nr = draw_inv_nor(d_pos_nor_red, 1.5, 14, label_text='A')
invB_nr = draw_inv_nor(d_pos_nor_red, 1.5, 12, label_text='B')
invC_nr = draw_inv_nor(d_pos_nor_red, 1.5, 10, label_text='C')
invD_nr = draw_inv_nor(d_pos_nor_red, 1.5, 8, label_text='D')

# Sumas: el inversor de salida de la suma se cancela con el inversor de entrada del AND!
s1_nr = draw_gate_nor(d_pos_nor_red, 5.5, 14, lbl1='B', lbl2='C')
s2_nr = draw_inv_nor(d_pos_nor_red, 8.5, 14, in_wire=s1_nr.out)
s3_nr = draw_gate_nor(d_pos_nor_red, 11.5, 13.5, lbl1='A', in2=s2_nr)

s5_nr = draw_gate_nor(d_pos_nor_red, 5.5, 10, in1=invC_nr, lbl2='D')
s6_nr = draw_inv_nor(d_pos_nor_red, 8.5, 10, in_wire=s5_nr.out)
s7_nr = draw_gate_nor(d_pos_nor_red, 11.5, 9.5, lbl1='A', in2=s6_nr)

s9_nr = draw_gate_nor(d_pos_nor_red, 5.5, 6, in1=invB_nr, in2=invD_nr)
s10_nr = draw_inv_nor(d_pos_nor_red, 8.5, 6, in_wire=s9_nr.out)
s11_nr = draw_gate_nor(d_pos_nor_red, 11.5, 5.5, lbl1='A', in2=s10_nr)

s13_nr = draw_gate_nor(d_pos_nor_red, 5.5, 2, in1=invA_nr, in2=invC_nr)
s14_nr = draw_inv_nor(d_pos_nor_red, 8.5, 2, in_wire=s13_nr.out)
s15_nr = draw_gate_nor(d_pos_nor_red, 11.5, 1.5, in1=s14_nr, in2=invD_nr)

# Primer nivel de AND: entra directamente la salida negada de cada suma!
# (S1)' nor (S2)' = S1 · S2
and1_nr = draw_gate_nor(d_pos_nor_red, 16.5, 11.5, in1=s3_nr, in2=s7_nr)
and2_nr = draw_gate_nor(d_pos_nor_red, 16.5, 3.5, in1=s11_nr, in2=s15_nr)

# Segundo nivel de AND
inv_and1_nr = draw_inv_nor(d_pos_nor_red, 19.5, 11.5, in_wire=and1_nr.out)
inv_and2_nr = draw_inv_nor(d_pos_nor_red, 19.5, 3.5, in_wire=and2_nr.out)
f_pos_nr = draw_gate_nor(d_pos_nor_red, 22.5, 7.5, in1=inv_and1_nr, in2=inv_and2_nr)
d_pos_nor_red.add(logic.Line().right(0.7).at(f_pos_nr.out).label("F", loc='right'))

title_pos_nor_red = (
    "Diagrama 8: Expresión reducida de maxitérminos (POS) - NOR Reducido (Doble Negación)\n"
    "f = (A+B+C)(A+C'+D)(A+B'+D')(A'+C'+D') | 8 compuertas eliminadas por cancelación | Total: 21 compuertas NOR"
)
save_clean_diagram(d_pos_nor_red, 'diagrama_POS_NOR_reducido.png', title_pos_nor_red)


# =========================================================================
# 5. POS NAND UNIVERSAL (DIRECTO) - 34 compuertas NAND
# =========================================================================
d_pos_nand = create_drawing()

# Inversores de entrada
iA_pn = draw_inv_nand(d_pos_nand, 1.5, 14, label_text='A')
iB_pn = draw_inv_nand(d_pos_nand, 1.5, 12, label_text='B')
iC_pn = draw_inv_nand(d_pos_nand, 1.5, 10, label_text='C')
iD_pn = draw_inv_nand(d_pos_nand, 1.5, 8, label_text='D')

# S1 = (A + B + C): OR(B, C) -> INV(B), INV(C), NAND; luego OR(A, B+C) -> INV(A), INV(B+C), NAND
# En universal directo: cada OR son 3 NANDs. 2 OR = 6 NANDs por suma.
s1_1_i1 = draw_inv_nand(d_pos_nand, 4.5, 15, label_text='B')
s1_1_i2 = draw_inv_nand(d_pos_nand, 4.5, 13.5, label_text='C')
s1_1 = draw_gate_nand(d_pos_nand, 7.5, 14.25, in1=s1_1_i1, in2=s1_1_i2)
s1_2_i1 = draw_inv_nand(d_pos_nand, 10.5, 15, label_text='A')
s1_2_i2 = draw_inv_nand(d_pos_nand, 10.5, 13.5, in_wire=s1_1.out)
sum1_pn = draw_gate_nand(d_pos_nand, 13.5, 14.25, in1=s1_2_i1, in2=s1_2_i2)

# S2 = (A + C' + D)
s2_1_i1 = draw_inv_nand(d_pos_nand, 4.5, 11, in_wire=iC_pn.out)
s2_1_i2 = draw_inv_nand(d_pos_nand, 4.5, 9.5, label_text='D')
s2_1 = draw_gate_nand(d_pos_nand, 7.5, 10.25, in1=s2_1_i1, in2=s2_1_i2)
s2_2_i1 = draw_inv_nand(d_pos_nand, 10.5, 11, label_text='A')
s2_2_i2 = draw_inv_nand(d_pos_nand, 10.5, 9.5, in_wire=s2_1.out)
sum2_pn = draw_gate_nand(d_pos_nand, 13.5, 10.25, in1=s2_2_i1, in2=s2_2_i2)

# S3 = (A + B' + D')
s3_1_i1 = draw_inv_nand(d_pos_nand, 4.5, 7, in_wire=iB_pn.out)
s3_1_i2 = draw_inv_nand(d_pos_nand, 4.5, 5.5, in_wire=iD_pn.out)
s3_1 = draw_gate_nand(d_pos_nand, 7.5, 6.25, in1=s3_1_i1, in2=s3_1_i2)
s3_2_i1 = draw_inv_nand(d_pos_nand, 10.5, 7, label_text='A')
s3_2_i2 = draw_inv_nand(d_pos_nand, 10.5, 5.5, in_wire=s3_1.out)
sum3_pn = draw_gate_nand(d_pos_nand, 13.5, 6.25, in1=s3_2_i1, in2=s3_2_i2)

# S4 = (A' + C' + D')
s4_1_i1 = draw_inv_nand(d_pos_nand, 4.5, 3, in_wire=iA_pn.out)
s4_1_i2 = draw_inv_nand(d_pos_nand, 4.5, 1.5, in_wire=iC_pn.out)
s4_1 = draw_gate_nand(d_pos_nand, 7.5, 2.25, in1=s4_1_i1, in2=s4_1_i2)
s4_2_i1 = draw_inv_nand(d_pos_nand, 10.5, 3, in_wire=s4_1.out)
s4_2_i2 = draw_inv_nand(d_pos_nand, 10.5, 1.5, in_wire=iD_pn.out)
sum4_pn = draw_gate_nand(d_pos_nand, 13.5, 2.25, in1=s4_2_i1, in2=s4_2_i2)

# Arbol AND (3 compuertas AND = 6 compuertas NAND)
a1_pn = draw_gate_nand(d_pos_nand, 17.5, 12.25, in1=sum1_pn, in2=sum2_pn)
a1_pn_inv = draw_inv_nand(d_pos_nand, 20.5, 12.25, in_wire=a1_pn.out)

a2_pn = draw_gate_nand(d_pos_nand, 17.5, 4.25, in1=sum3_pn, in2=sum4_pn)
a2_pn_inv = draw_inv_nand(d_pos_nand, 20.5, 4.25, in_wire=a2_pn.out)

a3_pn = draw_gate_nand(d_pos_nand, 23.5, 8.25, in1=a1_pn_inv, in2=a2_pn_inv)
f_pos_nand_out = draw_inv_nand(d_pos_nand, 26.5, 8.25, in_wire=a3_pn.out)
d_pos_nand.add(logic.Line().right(0.7).at(f_pos_nand_out.out).label("F", loc='right'))

title_pos_nand = (
    "Diagrama 5: Expresión reducida de maxitérminos (POS) - Universalidad NAND (Directo)\n"
    "f = (A+B+C)(A+C'+D)(A+B'+D')(A'+C'+D') | Conteo: 4 NOT + 24 OR + 6 AND = 34 compuertas NAND"
)
save_clean_diagram(d_pos_nand, 'diagrama_POS_NAND.png', title_pos_nand)


# =========================================================================
# 6. POS NAND REDUCIDO (DOBLE NEGACION) - 22 compuertas NAND
# =========================================================================
# Al simplificar las entradas de cada OR donde un literal ya negado se vuelve a negar:
# (x' nand x') nand (y' nand y') se reduce al cancelar dobles negaciones.
# Quedan 22 compuertas NAND.
d_pos_nand_red = create_drawing()

iA_pnr = draw_inv_nand(d_pos_nand_red, 1.5, 14, label_text='A')
iB_pnr = draw_inv_nand(d_pos_nand_red, 1.5, 12, label_text='B')
iC_pnr = draw_inv_nand(d_pos_nand_red, 1.5, 10, label_text='C')
iD_pnr = draw_inv_nand(d_pos_nand_red, 1.5, 8, label_text='D')

# S1 red: B+C = (B' nand C')
t1_pnr = draw_gate_nand(d_pos_nand_red, 5.5, 14, in1=iB_pnr, in2=iC_pnr)
t1_not = draw_inv_nand(d_pos_nand_red, 8.5, 14, in_wire=t1_pnr.out)
S1_pnr = draw_gate_nand(d_pos_nand_red, 11.5, 13.5, in1=iA_pnr, in2=t1_not)

# S2 red: C'+D = (C nand D')
t2_pnr = draw_gate_nand(d_pos_nand_red, 5.5, 10, lbl1='C', in2=iD_pnr)
t2_not = draw_inv_nand(d_pos_nand_red, 8.5, 10, in_wire=t2_pnr.out)
S2_pnr = draw_gate_nand(d_pos_nand_red, 11.5, 9.5, in1=iA_pnr, in2=t2_not)

# S3 red: B'+D' = (B nand D)
t3_pnr = draw_gate_nand(d_pos_nand_red, 5.5, 6, lbl1='B', lbl2='D')
t3_not = draw_inv_nand(d_pos_nand_red, 8.5, 6, in_wire=t3_pnr.out)
S3_pnr = draw_gate_nand(d_pos_nand_red, 11.5, 5.5, in1=iA_pnr, in2=t3_not)

# S4 red: C'+D' = (C nand D), luego A' + (C'+D') = A nand (C'+D')'
t4_pnr = draw_gate_nand(d_pos_nand_red, 5.5, 2, lbl1='C', lbl2='D')
t4_not = draw_inv_nand(d_pos_nand_red, 8.5, 2, in_wire=t4_pnr.out)
S4_pnr = draw_gate_nand(d_pos_nand_red, 11.5, 1.5, lbl1='A', in2=t4_not)

# Arbol AND (3 AND = 6 compuertas NAND)
a1_pnr = draw_gate_nand(d_pos_nand_red, 15.5, 11.5, in1=S1_pnr, in2=S2_pnr)
a1_pnr_inv = draw_inv_nand(d_pos_nand_red, 18.5, 11.5, in_wire=a1_pnr.out)

a2_pnr = draw_gate_nand(d_pos_nand_red, 15.5, 3.5, in1=S3_pnr, in2=S4_pnr)
a2_pnr_inv = draw_inv_nand(d_pos_nand_red, 18.5, 3.5, in_wire=a2_pnr.out)

a3_pnr = draw_gate_nand(d_pos_nand_red, 21.5, 7.5, in1=a1_pnr_inv, in2=a2_pnr_inv)
f_pos_nand_red_out = draw_inv_nand(d_pos_nand_red, 24.5, 7.5, in_wire=a3_pnr.out)
d_pos_nand_red.add(logic.Line().right(0.7).at(f_pos_nand_red_out.out).label("F", loc='right'))

title_pos_nand_red = (
    "Diagrama 6: Expresión reducida de maxitérminos (POS) - NAND Reducido (Doble Negación)\n"
    "f = (A+B+C)(A+C'+D)(A+B'+D')(A'+C'+D') | 12 compuertas eliminadas por cancelación | Total: 22 compuertas NAND"
)
save_clean_diagram(d_pos_nand_red, 'diagrama_POS_NAND_reducido.png', title_pos_nand_red)


# =========================================================================
# 7. SOP NOR UNIVERSAL (DIRECTO) - 34 compuertas NOR
# =========================================================================
d_sop_nor = create_drawing()

iA_sn = draw_inv_nor(d_sop_nor, 1.5, 14, label_text='A')
iB_sn = draw_inv_nor(d_sop_nor, 1.5, 12, label_text='B')
iC_sn = draw_inv_nor(d_sop_nor, 1.5, 10, label_text='C')
iD_sn = draw_inv_nor(d_sop_nor, 1.5, 8, label_text='D')

# P1 = A'B'C': 2 AND = 6 NORs
p1_1_i1 = draw_inv_nor(d_sop_nor, 4.5, 15, in_wire=iB_sn.out)
p1_1_i2 = draw_inv_nor(d_sop_nor, 4.5, 13.5, in_wire=iC_sn.out)
p1_1 = draw_gate_nor(d_sop_nor, 7.5, 14.25, in1=p1_1_i1, in2=p1_1_i2)
p1_2_i1 = draw_inv_nor(d_sop_nor, 10.5, 15, in_wire=iA_sn.out)
p1_2_i2 = draw_inv_nor(d_sop_nor, 10.5, 13.5, in_wire=p1_1.out)
prod1_sn = draw_gate_nor(d_sop_nor, 13.5, 14.25, in1=p1_2_i1, in2=p1_2_i2)

# P2 = A'CD'
p2_1_i1 = draw_inv_nor(d_sop_nor, 4.5, 11, in_wire=iA_sn.out)
p2_1_i2 = draw_inv_nor(d_sop_nor, 4.5, 9.5, label_text='C')
p2_1 = draw_gate_nor(d_sop_nor, 7.5, 10.25, in1=p2_1_i1, in2=p2_1_i2)
p2_2_i1 = draw_inv_nor(d_sop_nor, 10.5, 11, in_wire=p2_1.out)
p2_2_i2 = draw_inv_nor(d_sop_nor, 10.5, 9.5, in_wire=iD_sn.out)
prod2_sn = draw_gate_nor(d_sop_nor, 13.5, 10.25, in1=p2_2_i1, in2=p2_2_i2)

# P3 = A'BD
p3_1_i1 = draw_inv_nor(d_sop_nor, 4.5, 7, in_wire=iA_sn.out)
p3_1_i2 = draw_inv_nor(d_sop_nor, 4.5, 5.5, label_text='B')
p3_1 = draw_gate_nor(d_sop_nor, 7.5, 6.25, in1=p3_1_i1, in2=p3_1_i2)
p3_2_i1 = draw_inv_nor(d_sop_nor, 10.5, 7, in_wire=p3_1.out)
p3_2_i2 = draw_inv_nor(d_sop_nor, 10.5, 5.5, label_text='D')
prod3_sn = draw_gate_nor(d_sop_nor, 13.5, 6.25, in1=p3_2_i1, in2=p3_2_i2)

# P4 = ACD
p4_1_i1 = draw_inv_nor(d_sop_nor, 4.5, 3, label_text='A')
p4_1_i2 = draw_inv_nor(d_sop_nor, 4.5, 1.5, label_text='C')
p4_1 = draw_gate_nor(d_sop_nor, 7.5, 2.25, in1=p4_1_i1, in2=p4_1_i2)
p4_2_i1 = draw_inv_nor(d_sop_nor, 10.5, 3, in_wire=p4_1.out)
p4_2_i2 = draw_inv_nor(d_sop_nor, 10.5, 1.5, label_text='D')
prod4_sn = draw_gate_nor(d_sop_nor, 13.5, 2.25, in1=p4_2_i1, in2=p4_2_i2)

# Arbol OR (3 OR = 6 compuertas NOR)
o1_sn = draw_gate_nor(d_sop_nor, 17.5, 12.25, in1=prod1_sn, in2=prod2_sn)
o1_sn_inv = draw_inv_nor(d_sop_nor, 20.5, 12.25, in_wire=o1_sn.out)

o2_sn = draw_gate_nor(d_sop_nor, 17.5, 4.25, in1=prod3_sn, in2=prod4_sn)
o2_sn_inv = draw_inv_nor(d_sop_nor, 20.5, 4.25, in_wire=o2_sn.out)

o3_sn = draw_gate_nor(d_sop_nor, 23.5, 8.25, in1=o1_sn_inv, in2=o2_sn_inv)
f_sop_nor_out = draw_inv_nor(d_sop_nor, 26.5, 8.25, in_wire=o3_sn.out)
d_sop_nor.add(logic.Line().right(0.7).at(f_sop_nor_out.out).label("F'", loc='right'))

title_sop_nor = (
    "Diagrama 9: Expresión reducida de minitérminos (SOP) - Universalidad NOR (Directo)\n"
    "f' = A'B'C' + A'CD' + A'BD + ACD | Conteo: 4 NOT + 24 AND + 6 OR = 34 compuertas NOR"
)
save_clean_diagram(d_sop_nor, 'diagrama_SOP_NOR.png', title_sop_nor)


# =========================================================================
# 8. SOP NOR REDUCIDO (DOBLE NEGACION) - 22 compuertas NOR
# =========================================================================
d_sop_nor_red = create_drawing()

iA_snr = draw_inv_nor(d_sop_nor_red, 1.5, 14, label_text='A')
iB_snr = draw_inv_nor(d_sop_nor_red, 1.5, 12, label_text='B')
iC_snr = draw_inv_nor(d_sop_nor_red, 1.5, 10, label_text='C')
iD_snr = draw_inv_nor(d_sop_nor_red, 1.5, 8, label_text='D')

# P1 red: A'B'C' -> (B nor C) = B'C', luego (A nor (B'C')')
t1_snr = draw_gate_nor(d_sop_nor_red, 5.5, 14, lbl1='B', lbl2='C')
t1_snr_not = draw_inv_nor(d_sop_nor_red, 8.5, 14, in_wire=t1_snr.out)
P1_snr = draw_gate_nor(d_sop_nor_red, 11.5, 13.5, lbl1='A', in2=t1_snr_not)

# P2 red: A'CD' -> (A nor C') = A'C, luego ((A'C)' nor D)
t2_snr = draw_gate_nor(d_sop_nor_red, 5.5, 10, lbl1='A', in2=iC_snr)
t2_snr_not = draw_inv_nor(d_sop_nor_red, 8.5, 10, in_wire=t2_snr.out)
P2_snr = draw_gate_nor(d_sop_nor_red, 11.5, 9.5, in1=t2_snr_not, lbl2='D')

# P3 red: A'BD -> (A nor B') = A'B, luego ((A'B)' nor D')
t3_snr = draw_gate_nor(d_sop_nor_red, 5.5, 6, lbl1='A', in2=iB_snr)
t3_snr_not = draw_inv_nor(d_sop_nor_red, 8.5, 6, in_wire=t3_snr.out)
P3_snr = draw_gate_nor(d_sop_nor_red, 11.5, 5.5, in1=t3_snr_not, in2=iD_snr)

# P4 red: ACD -> (A' nor C') = AC, luego ((AC)' nor D')
t4_snr = draw_gate_nor(d_sop_nor_red, 5.5, 2, in1=iA_snr, in2=iC_snr)
t4_snr_not = draw_inv_nor(d_sop_nor_red, 8.5, 2, in_wire=t4_snr.out)
P4_snr = draw_gate_nor(d_sop_nor_red, 11.5, 1.5, in1=t4_snr_not, in2=iD_snr)

# Arbol OR (3 OR = 6 compuertas NOR)
o1_snr = draw_gate_nor(d_sop_nor_red, 15.5, 11.5, in1=P1_snr, in2=P2_snr)
o1_snr_inv = draw_inv_nor(d_sop_nor_red, 18.5, 11.5, in_wire=o1_snr.out)

o2_snr = draw_gate_nor(d_sop_nor_red, 15.5, 3.5, in1=P3_snr, in2=P4_snr)
o2_snr_inv = draw_inv_nor(d_sop_nor_red, 18.5, 3.5, in_wire=o2_snr.out)

o3_snr = draw_gate_nor(d_sop_nor_red, 21.5, 7.5, in1=o1_snr_inv, in2=o2_snr_inv)
f_sop_nor_red_out = draw_inv_nor(d_sop_nor_red, 24.5, 7.5, in_wire=o3_snr.out)
d_sop_nor_red.add(logic.Line().right(0.7).at(f_sop_nor_red_out.out).label("F'", loc='right'))

title_sop_nor_red = (
    "Diagrama 10: Expresión reducida de minitérminos (SOP) - NOR Reducido (Doble Negación)\n"
    "f' = A'B'C' + A'CD' + A'BD + ACD | 12 compuertas eliminadas por cancelación | Total: 22 compuertas NOR"
)
save_clean_diagram(d_sop_nor_red, 'diagrama_SOP_NOR_reducido.png', title_sop_nor_red)

print("\n¡TODOS LOS DIAGRAMAS MANUALES FUERON GENERADOS CORRECTAMENTE!")
