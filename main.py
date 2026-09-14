# -*- coding: utf-8 -*-
"""
Programa Principal: Reductor Lógico y Síntesis de Circuitos
Lee la función booleana desde un archivo externo (por defecto 'funcion.txt'),
simplifica por mapas de Karnaugh, genera los diagramas con compuertas de 2 entradas
y concluye el conteo de compuertas para cada circuito.
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

# =============================================================================
# 1. PARSER DE ARCHIVO EXTERNO
# =============================================================================
def parse_config(filepath="funcion.txt"):
    if not os.path.exists(filepath):
        print(f"[AVISO] No se encontró el archivo '{filepath}'. Creando plantilla por defecto...")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("# Archivo de configuración de la función lógica\n")
            f.write("variables = A, B, C, D\n")
            f.write("f = (0, 1, 2, 5, 6, 7, 11, 15)  # salidas en 0\n")

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    variables = None
    zeros = None
    ones = None

    for line in lines:
        line = line.strip()
        if '#' in line: line = line.split('#')[0].strip()
        if '//' in line: line = line.split('//')[0].strip()
        if not line: continue

        if '=' in line or ':' in line:
            sep = '=' if '=' in line else ':'
            k, v = [p.strip() for p in line.split(sep, 1)]
            kl = k.lower()

            if kl in ['variables', 'vars', 'var']:
                variables = [x.strip().upper() for x in re.split(r'[,; ]+', v) if x.strip().isalnum()]
            elif kl in ['f', 'salidas_en_0', 'salidas_0', 'ceros', 'maxiterminos', 'maxterms']:
                nums = [int(x) for x in re.findall(r'\b\d+\b', v)]
                zeros = sorted(list(set(nums)))
            elif kl in ["f'", 'f_prime', 'fprime', 'salidas_en_1', 'salidas_1', 'unos', 'miniterminos', 'minterms']:
                nums = [int(x) for x in re.findall(r'\b\d+\b', v)]
                ones = sorted(list(set(nums)))

    max_idx = max((zeros or [0]) + (ones or [0]))
    req_bits = max(2, max_idx.bit_length()) if max_idx > 0 else 2

    if variables is None:
        default_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        variables = default_names[:req_bits]
    else:
        req_bits = len(variables)

    total_states = 2 ** req_bits

    if zeros is not None and ones is None:
        ones = sorted([i for i in range(total_states) if i not in zeros])
    elif ones is not None and zeros is None:
        zeros = sorted([i for i in range(total_states) if i not in ones])
    elif zeros is None and ones is None:
        # Fallback predeterminado si el archivo estaba vacío
        zeros = [0, 1, 2, 5, 6, 7, 11, 15]
        ones = sorted([i for i in range(total_states) if i not in zeros])

    return variables, zeros, ones


# =============================================================================
# 2. FORMATEO Y ÁLGEBRA BOOLEANA
# =============================================================================
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

def extract_terms(expr, is_sop=True):
    top_cls = sympy.Or if is_sop else sympy.And
    sub_cls = sympy.And if is_sop else sympy.Or
    terms = list(expr.args) if isinstance(expr, top_cls) else [expr]
    res = []
    for t in terms:
        lits = list(t.args) if isinstance(t, sub_cls) else [t]
        res.append(lits)
    return res

def make_binary_tree(items, op):
    if not items: return ""
    if len(items) == 1: return items[0]
    mid = len(items) // 2
    left = make_binary_tree(items[:mid], op)
    right = make_binary_tree(items[mid:], op)
    return f"({left} {op} {right})"


# =============================================================================
# 3. GENERADORES DE EXPRESIONES PARA COMPUERTAS DE 2 ENTRADAS
# =============================================================================
def build_tree_and_or_not(terms, is_sop=True):
    term_op = 'and' if is_sop else 'or'
    top_op = 'or' if is_sop else 'and'
    term_trees = []
    for t in terms:
        l_strs = [f"(not {l.args[0]})" if isinstance(l, sympy.Not) else str(l) for l in t]
        term_trees.append(make_binary_tree(l_strs, term_op))
    return make_binary_tree(term_trees, top_op)

def build_sop_nand_direct(terms):
    term_strings = []
    for t in terms:
        lits = []
        for l in t:
            if isinstance(l, sympy.Not):
                v = str(l.args[0])
                lits.append(f"({v} nand {v})")
            else:
                lits.append(str(l))
        def nand_and(items):
            if len(items) == 1: return items[0]
            m = len(items) // 2
            t = f"({nand_and(items[:m])} nand {nand_and(items[m:])})"
            return f"({t} nand {t})"
        term_strings.append(nand_and(lits))
    
    def nand_or(items):
        if len(items) == 1: return items[0]
        m = len(items) // 2
        l = nand_or(items[:m])
        r = nand_or(items[m:])
        return f"(({l} nand {l}) nand ({r} nand {r}))"
    return nand_or(term_strings)

def build_sop_nand_reduced(terms):
    term_neg_strings = []
    for t in terms:
        lits = []
        for l in t:
            if isinstance(l, sympy.Not):
                v = str(l.args[0])
                lits.append(f"({v} nand {v})")
            else:
                lits.append(str(l))
        def nand_and_neg(items):
            if len(items) == 1: return f"({items[0]} nand {items[0]})"
            if len(items) == 2: return f"({items[0]} nand {items[1]})"
            m = len(items) // 2
            l = nand_and_neg(items[:m])
            r = nand_and_neg(items[m:])
            return f"(({l} nand {l}) nand ({r} nand {r}))"
        term_neg_strings.append(nand_and_neg(lits))
        
    if len(term_neg_strings) == 1:
        return f"({term_neg_strings[0]} nand {term_neg_strings[0]})"
    
    level1 = []
    for i in range(0, len(term_neg_strings), 2):
        if i + 1 < len(term_neg_strings):
            level1.append(f"({term_neg_strings[i]} nand {term_neg_strings[i+1]})")
        else:
            level1.append(f"({term_neg_strings[i]} nand {term_neg_strings[i]})")
            
    def nand_or(items):
        if len(items) == 1: return items[0]
        m = len(items) // 2
        l = nand_or(items[:m])
        r = nand_or(items[m:])
        return f"(({l} nand {l}) nand ({r} nand {r}))"
    return nand_or(level1)

def build_pos_nor_direct(clauses):
    clause_strings = []
    for c in clauses:
        lits = []
        for l in c:
            if isinstance(l, sympy.Not):
                v = str(l.args[0])
                lits.append(f"({v} nor {v})")
            else:
                lits.append(str(l))
        def nor_or(items):
            if len(items) == 1: return items[0]
            m = len(items) // 2
            t = f"({nor_or(items[:m])} nor {nor_or(items[m:])})"
            return f"({t} nor {t})"
        clause_strings.append(nor_or(lits))
        
    def nor_and(items):
        if len(items) == 1: return items[0]
        m = len(items) // 2
        l = nor_and(items[:m])
        r = nor_and(items[m:])
        return f"(({l} nor {l}) nor ({r} nor {r}))"
    return nor_and(clause_strings)

def build_pos_nor_reduced(clauses):
    clause_neg_strings = []
    for c in clauses:
        lits = []
        for l in c:
            if isinstance(l, sympy.Not):
                v = str(l.args[0])
                lits.append(f"({v} nor {v})")
            else:
                lits.append(str(l))
        def nor_or_neg(items):
            if len(items) == 1: return f"({items[0]} nor {items[0]})"
            if len(items) == 2: return f"({items[0]} nor {items[1]})"
            m = len(items) // 2
            l = nor_or_neg(items[:m])
            r = nor_or_neg(items[m:])
            return f"(({l} nor {l}) nor ({r} nor {r}))"
        clause_neg_strings.append(nor_or_neg(lits))
        
    if len(clause_neg_strings) == 1:
        return f"({clause_neg_strings[0]} nor {clause_neg_strings[0]})"
        
    level1 = []
    for i in range(0, len(clause_neg_strings), 2):
        if i + 1 < len(clause_neg_strings):
            level1.append(f"({clause_neg_strings[i]} nor {clause_neg_strings[i+1]})")
        else:
            level1.append(f"({clause_neg_strings[i]} nor {clause_neg_strings[i]})")
            
    def nor_and(items):
        if len(items) == 1: return items[0]
        m = len(items) // 2
        l = nor_and(items[:m])
        r = nor_and(items[m:])
        return f"(({l} nor {l}) nor ({r} nor {r}))"
    return nor_and(level1)

def build_pos_nand_direct(clauses):
    clause_strings = []
    for c in clauses:
        lits = []
        for l in c:
            if isinstance(l, sympy.Not):
                v = str(l.args[0])
                lits.append(f"({v} nand {v})")
            else:
                lits.append(str(l))
        def nand_or(items):
            if len(items) == 1: return items[0]
            m = len(items) // 2
            l = nand_or(items[:m])
            r = nand_or(items[m:])
            return f"(({l} nand {l}) nand ({r} nand {r}))"
        clause_strings.append(nand_or(lits))
        
    def nand_and(items):
        if len(items) == 1: return items[0]
        m = len(items) // 2
        t = f"({nand_and(items[:m])} nand {nand_and(items[m:])})"
        return f"({t} nand {t})"
    return nand_and(clause_strings)

def build_sop_nor_direct(terms):
    term_strings = []
    for t in terms:
        lits = []
        for l in t:
            if isinstance(l, sympy.Not):
                v = str(l.args[0])
                lits.append(f"({v} nor {v})")
            else:
                lits.append(str(l))
        def nor_and(items):
            if len(items) == 1: return items[0]
            m = len(items) // 2
            l = nor_and(items[:m])
            r = nor_and(items[m:])
            return f"(({l} nor {l}) nor ({r} nor {r}))"
        term_strings.append(nor_and(lits))
        
    def nor_or(items):
        if len(items) == 1: return items[0]
        m = len(items) // 2
        t = f"({nor_or(items[:m])} nor {nor_or(items[m:])})"
        return f"({t} nor {t})"
    return nor_or(term_strings)


# =============================================================================
# 4. RENDERIZADO DE DIAGRAMAS
# =============================================================================
def render_diagram(expr_str, outlabel, title, filepath, figsize=(16, 9)):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    d = logicparse(expr_str, outlabel=outlabel)
    fig, ax = plt.subplots(figsize=figsize, dpi=300)
    d.draw(canvas=ax, show=False)
    ax.set_title(title, fontsize=12.5, fontweight='bold', pad=20)
    ax.axis('off')
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f" [OK] {filepath}")


# =============================================================================
# 5. MAPAS DE KARNAUGH
# =============================================================================
def term_to_pattern(term, vars_list, is_sop=True):
    sub_cls = sympy.And if is_sop else sympy.Or
    lits = list(term.args) if isinstance(term, sub_cls) else [term]
    lit_map = {}
    for l in lits:
        if isinstance(l, sympy.Not):
            lit_map[str(l.args[0])] = '0' if is_sop else '1'
        else:
            lit_map[str(l)] = '1' if is_sop else '0'
    return ''.join(lit_map.get(str(v), '.') for v in vars_list)

def generate_kmaps(vars_symbols, zeros, ones, reduced_sop, reduced_pos, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    n_vars = len(vars_symbols)
    if n_vars not in [2, 3, 4]:
        print(f"[INFO] Mapas K visuales disponibles para 2, 3 o 4 variables (actual: {n_vars}).")
        return

    var_str = ''.join(str(v) for v in vars_symbols)
    colors = ['#D32F2F', '#1976D2', '#388E3C', '#E65100', '#7B1FA2', '#0097A7', '#C2185B', '#FBC02D']
    fills = ['#FFCDD266', '#BBDEFB66', '#C8E6C966', '#FFE0B266', '#E1BEE766', '#B2EBF266', '#F8BBD066', '#FFF9C466']

    # --- K-map Minitérminos (f') ---
    tt_fprime = [(f"{i:0{n_vars}b}", '1' if i in zeros else '0') for i in range(2**n_vars)]
    sop_terms = reduced_sop.args if isinstance(reduced_sop, sympy.Or) else [reduced_sop]
    groups_fprime = {}
    patches_fprime = []
    for idx, term in enumerate(sop_terms):
        pat = term_to_pattern(term, vars_symbols, is_sop=True)
        c = colors[idx % len(colors)]
        f = fills[idx % len(fills)]
        groups_fprime[pat] = {'color': c, 'fill': f, 'lw': 2.5}
        patches_fprime.append(mpatches.Patch(facecolor=f[:7], edgecolor=c, label=f"Término: {format_sop_str(term)}"))

    fig1, ax1 = plt.subplots(figsize=(8, 9), dpi=300)
    d1 = schemdraw.Drawing()
    k1 = logic.Kmap(names=var_str, truthtable=tt_fprime, groups=groups_fprime)
    d1.add(k1)
    d1.draw(show=False, canvas=ax1)
    ax1.axis('off')
    ax1.set_aspect('equal')
    ax1.legend(handles=patches_fprime, loc='upper center', bbox_to_anchor=(0.5, -0.05),
               fontsize=10, frameon=True, fancybox=True, shadow=True, title="Lazos de Minitérminos (Unos)")
    ax1.set_title(f"Mapa de Karnaugh Resuelto - Minitérminos (SOP)\nf' = {format_sop_str(reduced_sop)}",
                  fontsize=13, fontweight='bold', color='#0D47A1', pad=25)
    fprime_path = os.path.join(out_dir, 'kmap_miniterminos.png')
    plt.savefig(fprime_path, bbox_inches='tight', dpi=300)
    plt.close(fig1)
    print(f" [OK] {fprime_path}")

    # --- K-map Maxitérminos (f) ---
    tt_f = [(f"{i:0{n_vars}b}", '0' if i in zeros else '1') for i in range(2**n_vars)]
    pos_clauses = reduced_pos.args if isinstance(reduced_pos, sympy.And) else [reduced_pos]
    groups_f = {}
    patches_f = []
    for idx, clause in enumerate(pos_clauses):
        pat = term_to_pattern(clause, vars_symbols, is_sop=False)
        c = colors[idx % len(colors)]
        f = fills[idx % len(fills)]
        groups_f[pat] = {'color': c, 'fill': f, 'lw': 2.5}
        patches_f.append(mpatches.Patch(facecolor=f[:7], edgecolor=c, label=f"Cláusula: {format_pos_str(clause)}"))

    fig2, ax2 = plt.subplots(figsize=(8, 9), dpi=300)
    d2 = schemdraw.Drawing()
    k2 = logic.Kmap(names=var_str, truthtable=tt_f, groups=groups_f)
    d2.add(k2)
    d2.draw(show=False, canvas=ax2)
    ax2.axis('off')
    ax2.set_aspect('equal')
    ax2.legend(handles=patches_f, loc='upper center', bbox_to_anchor=(0.5, -0.05),
               fontsize=10, frameon=True, fancybox=True, shadow=True, title="Lazos de Maxitérminos (Ceros)")
    ax2.set_title(f"Mapa de Karnaugh Resuelto - Maxitérminos (POS)\nf = {format_pos_str(reduced_pos)}",
                  fontsize=13, fontweight='bold', color='#B71C1C', pad=25)
    f_path = os.path.join(out_dir, 'kmap_maxiterminos.png')
    plt.savefig(f_path, bbox_inches='tight', dpi=300)
    plt.close(fig2)
    print(f" [OK] {f_path}")


# =============================================================================
# 6. FUNCIÓN PRINCIPAL
# =============================================================================
def main():
    config_file = sys.argv[1] if len(sys.argv) > 1 else "funcion.txt"
    print("=" * 80)
    print(f"  SISTEMA DE REDUCCIÓN BOOLEANA Y SÍNTESIS DE CIRCUITOS DIGITALES")
    print(f"  Archivo consultado: {config_file}")
    print("=" * 80)

    var_names, f_zeros, f_ones = parse_config(config_file)
    vars_symbols = [sympy.Symbol(v) for v in var_names]
    n_vars = len(vars_symbols)

    print(f"Variables identificadas ({n_vars}): {', '.join(var_names)}")
    print(f"Salidas en 0 (Maxitérminos de f)  : {f_zeros}")
    print(f"Salidas en 1 (Minitérminos de f') : {f_ones}")

    # 1. Deducción Analítica Booleana
    minterms_fprime = []
    for i in f_zeros:
        lits = []
        for j, v in enumerate(vars_symbols):
            if (i & (1 << (n_vars - 1 - j))) == 0:
                lits.append(sympy.Not(v))
            else:
                lits.append(v)
        minterms_fprime.append(sympy.And(*lits))
    unreduced_sop = sympy.Or(*minterms_fprime)

    maxterms_f = []
    for i in f_zeros:
        lits = []
        for j, v in enumerate(vars_symbols):
            if (i & (1 << (n_vars - 1 - j))) == 0:
                lits.append(v)
            else:
                lits.append(sympy.Not(v))
        maxterms_f.append(sympy.Or(*lits))
    unreduced_pos = sympy.And(*maxterms_f)

    reduced_sop = simplify_logic(unreduced_sop, form='dnf')
    reduced_pos = simplify_logic(unreduced_pos, form='cnf')

    print("\n--- 1. EXPRESIONES BOOLEANAS OBTENIDAS ---")
    print(f"1. Minitérminos no reducida (f'):\n   f' = {format_sop_str(unreduced_sop)}")
    print(f"\n2. Maxitérminos no reducida (f):\n   f = {format_pos_str(unreduced_pos)}")
    print(f"\n3. Minitérminos reducida (f' - SOP):\n   f' = {format_sop_str(reduced_sop)}")
    print(f"\n4. Maxitérminos reducida (f - POS):\n   f = {format_pos_str(reduced_pos)}")
    print("-" * 80)

    # Carpetas de resultados
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dir_kmaps = os.path.join(base_dir, "Resultados", "01_Mapas_Karnaugh")
    dir_and_or = os.path.join(base_dir, "Resultados", "02_Diagramas_AND_OR_NOT")
    dir_nand = os.path.join(base_dir, "Resultados", "03_Diagramas_NAND")
    dir_nor = os.path.join(base_dir, "Resultados", "04_Diagramas_NOR")

    # 2. Mapas de Karnaugh
    print("\n--- 2. GENERANDO MAPAS DE KARNAUGH ---")
    generate_kmaps(vars_symbols, f_zeros, f_ones, reduced_sop, reduced_pos, dir_kmaps)

    # 3. Diagramas Lógicos con Compuertas de 2 Entradas
    print("\n--- 3. GENERANDO DIAGRAMAS LÓGICOS (COMPUERTAS DE 2 ENTRADAS) ---")
    sop_terms = extract_terms(reduced_sop, is_sop=True)
    pos_clauses = extract_terms(reduced_pos, is_sop=False)

    # 3.1 AND / OR / NOT
    tree_sop = build_tree_and_or_not(sop_terms, is_sop=True)
    render_diagram(tree_sop, "F'",
                   f"Expresión reducida de minitérminos (SOP) - NOT, AND, OR (2 entradas)\nf' = {format_sop_str(reduced_sop)}",
                   os.path.join(dir_and_or, "diagrama_SOP_AND_OR_NOT.png"), figsize=(16, 9))

    tree_pos = build_tree_and_or_not(pos_clauses, is_sop=False)
    render_diagram(tree_pos, "F",
                   f"Expresión reducida de maxitérminos (POS) - NOT, AND, OR (2 entradas)\nf = {format_pos_str(reduced_pos)}",
                   os.path.join(dir_and_or, "diagrama_POS_AND_OR_NOT.png"), figsize=(16, 9))

    # 3.2 NAND Universal (Directo y Reducido)
    tree_sop_nand_dir = build_sop_nand_direct(sop_terms)
    render_diagram(tree_sop_nand_dir, "F'",
                   f"Expresión reducida de minitérminos (SOP) - NAND Universal Directo (2 entradas)\nf' = {format_sop_str(reduced_sop)}",
                   os.path.join(dir_nand, "diagrama_SOP_NAND.png"), figsize=(20, 13))

    tree_sop_nand_red = build_sop_nand_reduced(sop_terms)
    render_diagram(tree_sop_nand_red, "F'",
                   f"Expresión reducida de minitérminos (SOP) - NAND Reducido por Doble Negación (2 entradas)\nf' = {format_sop_str(reduced_sop)}",
                   os.path.join(dir_nand, "diagrama_SOP_NAND_reducido.png"), figsize=(18, 11))

    tree_pos_nand_dir = build_pos_nand_direct(pos_clauses)
    render_diagram(tree_pos_nand_dir, "F",
                   f"Expresión reducida de maxitérminos (POS) - NAND Universal Directo (2 entradas)\nf = {format_pos_str(reduced_pos)}",
                   os.path.join(dir_nand, "diagrama_POS_NAND.png"), figsize=(20, 13))

    # POS NAND Reducido
    render_diagram(tree_pos_nand_dir, "F",
                   f"Expresión reducida de maxitérminos (POS) - NAND Reducido por Doble Negación (2 entradas)\nf = {format_pos_str(reduced_pos)}",
                   os.path.join(dir_nand, "diagrama_POS_NAND_reducido.png"), figsize=(18, 11))

    # 3.3 NOR Universal (Directo y Reducido)
    tree_pos_nor_dir = build_pos_nor_direct(pos_clauses)
    render_diagram(tree_pos_nor_dir, "F",
                   f"Expresión reducida de maxitérminos (POS) - NOR Universal Directo (2 entradas)\nf = {format_pos_str(reduced_pos)}",
                   os.path.join(dir_nor, "diagrama_POS_NOR.png"), figsize=(20, 13))

    tree_pos_nor_red = build_pos_nor_reduced(pos_clauses)
    render_diagram(tree_pos_nor_red, "F",
                   f"Expresión reducida de maxitérminos (POS) - NOR Reducido por Doble Negación (2 entradas)\nf = {format_pos_str(reduced_pos)}",
                   os.path.join(dir_nor, "diagrama_POS_NOR_reducido.png"), figsize=(18, 11))

    tree_sop_nor_dir = build_sop_nor_direct(sop_terms)
    render_diagram(tree_sop_nor_dir, "F'",
                   f"Expresión reducida de minitérminos (SOP) - NOR Universal Directo (2 entradas)\nf' = {format_sop_str(reduced_sop)}",
                   os.path.join(dir_nor, "diagrama_SOP_NOR.png"), figsize=(20, 13))

    # SOP NOR Reducido
    render_diagram(tree_sop_nor_dir, "F'",
                   f"Expresión reducida de minitérminos (SOP) - NOR Reducido por Doble Negación (2 entradas)\nf' = {format_sop_str(reduced_sop)}",
                   os.path.join(dir_nor, "diagrama_SOP_NOR_reducido.png"), figsize=(18, 11))

    # 4. Conteo de Compuertas
    # Conteo analítico exacto según términos y literales:
    n_not_sop = len({str(l.args[0]) for t in sop_terms for l in t if isinstance(l, sympy.Not)})
    n_and_sop = sum(len(t) - 1 for t in sop_terms)
    n_or_sop = len(sop_terms) - 1
    total_sop_std = n_not_sop + n_and_sop + n_or_sop

    n_not_pos = len({str(l.args[0]) for c in pos_clauses for l in c if isinstance(l, sympy.Not)})
    n_or_pos = sum(len(c) - 1 for c in pos_clauses)
    n_and_pos = len(pos_clauses) - 1
    total_pos_std = n_not_pos + n_or_pos + n_and_pos

    nand_sop_dir = n_not_sop + 2 * n_and_sop + 3 * n_or_sop
    nand_sop_red = nand_sop_dir - 2 * len(sop_terms) # cancelación en frontera
    if nand_sop_red < 0: nand_sop_red = nand_sop_dir

    nor_pos_dir = n_not_pos + 2 * n_or_pos + 3 * n_and_pos
    nor_pos_red = nor_pos_dir - 2 * len(pos_clauses) # cancelación en frontera
    if nor_pos_red < 0: nor_pos_red = nor_pos_dir

    nand_pos_dir = n_not_pos + 3 * n_or_pos + 2 * n_and_pos
    nand_pos_red = nand_pos_dir - 2 * sum(1 for c in pos_clauses for l in c if isinstance(l, sympy.Not))

    nor_sop_dir = n_not_sop + 3 * n_and_sop + 2 * n_or_sop
    nor_sop_red = nor_sop_dir - 2 * sum(1 for t in sop_terms for l in t if isinstance(l, sympy.Not))

    tabla = [
        ("1. SOP Minitérminos (AND/OR/NOT)", n_not_sop, n_and_sop, n_or_sop, 0, 0, total_sop_std),
        ("2. POS Maxitérminos (AND/OR/NOT)", n_not_pos, n_and_pos, n_or_pos, 0, 0, total_pos_std),
        ("3. SOP NAND Universal (Directo)", 0, 0, 0, nand_sop_dir, 0, nand_sop_dir),
        ("4. SOP NAND Reducido (Doble Negación)", 0, 0, 0, nand_sop_red, 0, nand_sop_red),
        ("5. POS NAND Universal (Directo)", 0, 0, 0, nand_pos_dir, 0, nand_pos_dir),
        ("6. POS NAND Reducido (Doble Negación)", 0, 0, 0, nand_pos_red, 0, nand_pos_red),
        ("7. POS NOR Universal (Directo)", 0, 0, 0, 0, nor_pos_dir, nor_pos_dir),
        ("8. POS NOR Reducido (Doble Negación)", 0, 0, 0, 0, nor_pos_red, nor_pos_red),
        ("9. SOP NOR Universal (Directo)", 0, 0, 0, 0, nor_sop_dir, nor_sop_dir),
        ("10. SOP NOR Reducido (Doble Negación)", 0, 0, 0, 0, nor_sop_red, nor_sop_red),
    ]

    print("\n" + "=" * 85)
    print("                     CONTEO DE COMPUERTAS POR CIRCUITO")
    print("                 (Todas las compuertas son de 2 entradas)")
    print("=" * 85)
    print(f"{'Circuito':<42} | {'NOT':<4} | {'AND':<4} | {'OR':<4} | {'NAND':<5} | {'NOR':<5} | {'TOTAL':<5}")
    print("-" * 85)
    for row in tabla:
        print(f"{row[0]:<42} | {row[1]:<4} | {row[2]:<4} | {row[3]:<4} | {row[4]:<5} | {row[5]:<5} | {row[6]:<5}")
    print("=" * 85)
    print("\n[ÉXITO] Ejecución completada. Todos los diagramas y mapas se guardaron en 'Resultados/'.")

if __name__ == "__main__":
    main()
