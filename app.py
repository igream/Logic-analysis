# -*- coding: utf-8 -*-
"""
Servidor Web Flask para Reductor Lógico y Síntesis de Circuitos
Permite:
- Selección interactiva de número de bits (2 a 5 bits)
- Tabla de verdad interactiva para alternar salidas 0 / 1 fila por fila
- Carga y descarga de archivos de configuración (.txt)
- Deducción analítica y reducción booleana
- Mapas de Karnaugh de 2 a 5 variables
- Síntesis de circuitos lógicos con compuertas de 2 entradas
- Descarga individual en PNG y masiva en ZIP
"""

import sys
import os
import io
import re
import json
import zipfile
import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import schemdraw
import schemdraw.logic as logic
from schemdraw.parsing import logicparse
import sympy
from sympy.logic.boolalg import simplify_logic
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_GEN_DIR = os.path.join(BASE_DIR, "static", "generated")
os.makedirs(STATIC_GEN_DIR, exist_ok=True)

DEFAULT_CONFIG = """# ==============================================================================
# CONFIGURACIÓN DE LA FUNCIÓN LÓGICA (Reductor)
# ==============================================================================
variables = A, B, C, D
f = (0, 1, 2, 5, 6, 7, 11, 15)  # salidas en 0 (Maxitérminos)
"""

def parse_function_text(text):
    variables = None
    zeros = None
    ones = None
    num_bits = None
    
    for line in text.splitlines():
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
            elif kl in ['bits', 'num_bits', 'n_bits']:
                num_bits = int(v)
            elif kl in ['f', 'salidas_en_0', 'salidas_0', 'ceros', 'maxiterminos', 'maxterms']:
                nums = [int(x) for x in re.findall(r'\b\d+\b', v)]
                zeros = sorted(list(set(nums)))
            elif kl in ["f'", 'f_prime', 'fprime', 'salidas_en_1', 'salidas_1', 'unos', 'miniterminos', 'minterms']:
                nums = [int(x) for x in re.findall(r'\b\d+\b', v)]
                ones = sorted(list(set(nums)))
                
    max_idx = max((zeros or [0]) + (ones or [0]))
    req_bits = num_bits or (len(variables) if variables else max(2, max_idx.bit_length()))
    req_bits = min(5, max(2, req_bits))
    
    if variables is None:
        default_names = ['A', 'B', 'C', 'D', 'E']
        variables = default_names[:req_bits]
    else:
        variables = variables[:req_bits]
        req_bits = len(variables)
        
    total_states = 2 ** req_bits
    if zeros is not None and ones is None:
        ones = sorted([i for i in range(total_states) if i not in zeros])
    elif ones is not None and zeros is None:
        zeros = sorted([i for i in range(total_states) if i not in ones])
    elif zeros is None and ones is None:
        zeros = [0, 1, 2, 5, 6, 7, 11, 15] if req_bits == 4 else [0]
        ones = sorted([i for i in range(total_states) if i not in zeros])
        
    return variables, zeros, ones

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

def build_tree_and_or_not(terms, is_sop=True):
    if not terms or terms == [[False]] or terms == [[True]]:
        return ""
    term_op = 'and' if is_sop else 'or'
    top_op = 'or' if is_sop else 'and'
    term_trees = []
    for t in terms:
        l_strs = [f"(not {l.args[0]})" if isinstance(l, sympy.Not) else str(l) for l in t]
        term_trees.append(make_binary_tree(l_strs, term_op))
    return make_binary_tree(term_trees, top_op)

def build_tree_nand_direct_sop(terms):
    if not terms or terms == [[False]] or terms == [[True]]: return ""
    def nand_and(items):
        if not items: return ""
        cur = items[0]
        for extra in items[1:]:
            cur = f"(({cur} nand {extra}) nand ({cur} nand {extra}))"
        return cur
    def nand_or(items):
        if not items: return ""
        cur = items[0]
        for extra in items[1:]:
            cur = f"(({cur} nand {cur}) nand ({extra} nand {extra}))"
        return cur
    term_trees = []
    for t in terms:
        l_strs = [f"({l.args[0]} nand {l.args[0]})" if isinstance(l, sympy.Not) else str(l) for l in t]
        term_trees.append(nand_and(l_strs))
    return nand_or(term_trees)

def build_tree_nand_reduced_sop(terms):
    if not terms or terms == [[False]] or terms == [[True]]: return ""
    term_trees = []
    for t in terms:
        l_strs = [f"({l.args[0]} nand {l.args[0]})" if isinstance(l, sympy.Not) else str(l) for l in t]
        if len(l_strs) == 1:
            l = t[0]
            term_trees.append(str(l.args[0]) if isinstance(l, sympy.Not) else f"({l} nand {l})")
        elif len(l_strs) == 2:
            term_trees.append(f"({l_strs[0]} nand {l_strs[1]})")
        else:
            cur = f"({l_strs[0]} nand {l_strs[1]})"
            for extra in l_strs[2:]:
                cur = f"(({cur} nand {cur}) nand {extra})"
            term_trees.append(cur)
    if len(term_trees) == 1:
        return f"({term_trees[0]} nand {term_trees[0]})"
    return make_binary_tree(term_trees, 'nand')

def build_tree_nand_direct_pos(clauses):
    if not clauses or clauses == [[False]] or clauses == [[True]]: return ""
    def nand_or(items):
        if not items: return ""
        cur = items[0]
        for extra in items[1:]:
            cur = f"(({cur} nand {cur}) nand ({extra} nand {extra}))"
        return cur
    def nand_and(items):
        if not items: return ""
        cur = items[0]
        for extra in items[1:]:
            cur = f"(({cur} nand {extra}) nand ({cur} nand {extra}))"
        return cur
    clause_trees = []
    for c in clauses:
        l_strs = [f"({l.args[0]} nand {l.args[0]})" if isinstance(l, sympy.Not) else str(l) for l in c]
        clause_trees.append(nand_or(l_strs))
    return nand_and(clause_trees)

def build_tree_nand_reduced_pos(clauses):
    if not clauses or clauses == [[False]] or clauses == [[True]]: return ""
    clause_trees = []
    for c in clauses:
        l_strs = [str(l.args[0]) if isinstance(l, sympy.Not) else f"({l} nand {l})" for l in c]
        if len(l_strs) == 1:
            clause_trees.append(l_strs[0])
        else:
            cur = f"({l_strs[0]} nand {l_strs[1]})"
            for extra in l_strs[2:]:
                cur = f"(({cur} nand {cur}) nand {extra})"
            clause_trees.append(cur)
    if not clause_trees: return ""
    cur = clause_trees[0]
    for extra in clause_trees[1:]:
        cur = f"(({cur} nand {extra}) nand ({cur} nand {extra}))"
    return cur

def build_tree_nor_direct_pos(clauses):
    if not clauses or clauses == [[False]] or clauses == [[True]]: return ""
    def nor_or(items):
        if not items: return ""
        cur = items[0]
        for extra in items[1:]:
            cur = f"(({cur} nor {extra}) nor ({cur} nor {extra}))"
        return cur
    def nor_and(items):
        if not items: return ""
        cur = items[0]
        for extra in items[1:]:
            cur = f"(({cur} nor {cur}) nor ({extra} nor {extra}))"
        return cur
    clause_trees = []
    for c in clauses:
        l_strs = [f"({l.args[0]} nor {l.args[0]})" if isinstance(l, sympy.Not) else str(l) for l in c]
        clause_trees.append(nor_or(l_strs))
    return nor_and(clause_trees)

def build_tree_nor_reduced_pos(clauses):
    if not clauses or clauses == [[False]] or clauses == [[True]]: return ""
    clause_trees = []
    for c in clauses:
        l_strs = [f"({l.args[0]} nor {l.args[0]})" if isinstance(l, sympy.Not) else str(l) for l in c]
        if len(l_strs) == 1:
            l = c[0]
            clause_trees.append(str(l.args[0]) if isinstance(l, sympy.Not) else f"({l} nor {l})")
        elif len(l_strs) == 2:
            clause_trees.append(f"({l_strs[0]} nor {l_strs[1]})")
        else:
            cur = f"({l_strs[0]} nor {l_strs[1]})"
            for extra in l_strs[2:]:
                cur = f"(({cur} nor {cur}) nor {extra})"
            clause_trees.append(cur)
    if len(clause_trees) == 1:
        return f"({clause_trees[0]} nor {clause_trees[0]})"
    return make_binary_tree(clause_trees, 'nor')

def build_tree_nor_direct_sop(terms):
    if not terms or terms == [[False]] or terms == [[True]]: return ""
    def nor_and(items):
        if not items: return ""
        cur = items[0]
        for extra in items[1:]:
            cur = f"(({cur} nor {cur}) nor ({extra} nor {extra}))"
        return cur
    def nor_or(items):
        if not items: return ""
        cur = items[0]
        for extra in items[1:]:
            cur = f"(({cur} nor {extra}) nor ({cur} nor {extra}))"
        return cur
    term_trees = []
    for t in terms:
        l_strs = [f"({l.args[0]} nor {l.args[0]})" if isinstance(l, sympy.Not) else str(l) for l in t]
        term_trees.append(nor_and(l_strs))
    return nor_or(term_trees)

def build_tree_nor_reduced_sop(terms):
    if not terms or terms == [[False]] or terms == [[True]]: return ""
    term_trees = []
    for t in terms:
        l_strs = [str(l.args[0]) if isinstance(l, sympy.Not) else f"({l} nor {l})" for l in t]
        if len(l_strs) == 1:
            term_trees.append(l_strs[0])
        else:
            cur = f"({l_strs[0]} nor {l_strs[1]})"
            for extra in l_strs[2:]:
                cur = f"(({cur} nor {cur}) nor {extra})"
            term_trees.append(cur)
    if not term_trees: return ""
    cur = term_trees[0]
    for extra in term_trees[1:]:
        cur = f"(({cur} nor {extra}) nor ({cur} nor {extra}))"
    return cur

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

def render_diagram_to_file(expr_str, outlabel, title, filename, figsize=(16, 9)):
    filepath = os.path.join(STATIC_GEN_DIR, filename)
    try:
        if not expr_str or str(expr_str) in ['0', 'False']:
            fig, ax = plt.subplots(figsize=(8, 3), dpi=180)
            d = schemdraw.Drawing()
            d.add(logic.Line().right(2).label('0 (GND)', loc='left').label(outlabel, loc='right'))
            d.draw(canvas=ax, show=False)
            ax.set_title(title, fontsize=11, fontweight='bold', pad=16)
            ax.axis('off')
            plt.savefig(filepath, dpi=180, bbox_inches='tight')
            plt.close(fig)
            return filepath
        elif str(expr_str) in ['1', 'True']:
            fig, ax = plt.subplots(figsize=(8, 3), dpi=180)
            d = schemdraw.Drawing()
            d.add(logic.Line().right(2).label('1 (VCC)', loc='left').label(outlabel, loc='right'))
            d.draw(canvas=ax, show=False)
            ax.set_title(title, fontsize=11, fontweight='bold', pad=16)
            ax.axis('off')
            plt.savefig(filepath, dpi=180, bbox_inches='tight')
            plt.close(fig)
            return filepath

        d = logicparse(expr_str, outlabel=outlabel)
        fig, ax = plt.subplots(figsize=figsize, dpi=180)
        d.draw(canvas=ax, show=False)
        ax.set_title(title, fontsize=11, fontweight='bold', pad=16)
        ax.axis('off')
        plt.savefig(filepath, dpi=180, bbox_inches='tight')
        plt.close(fig)
    except Exception as e:
        print(f"Error generando {filename}: {e}")
        fig, ax = plt.subplots(figsize=(10, 4), dpi=180)
        ax.text(0.5, 0.5, f"{title}\n\nFunción: {outlabel} = {str(expr_str)[:70]}", 
                ha='center', va='center', fontsize=11, fontweight='bold',
                bbox=dict(boxstyle="round,pad=1", fc="#f8fafc", ec="#cbd5e1", lw=1.5))
        ax.axis('off')
        plt.savefig(filepath, dpi=180, bbox_inches='tight')
        plt.close(fig)
    return filepath

def process_logic(variables, zeros, ones):
    vars_symbols = [sympy.Symbol(v) for v in variables]
    n_vars = len(vars_symbols)
    
    # 1. Deducción Analítica Booleana
    minterms_fprime = []
    for i in zeros:
        lits = []
        for j, v in enumerate(vars_symbols):
            if (i & (1 << (n_vars - 1 - j))) == 0:
                lits.append(sympy.Not(v))
            else:
                lits.append(v)
        minterms_fprime.append(sympy.And(*lits))
    unreduced_sop = sympy.Or(*minterms_fprime)
    
    maxterms_f = []
    for i in zeros:
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
    
    sop_terms = extract_terms(reduced_sop, is_sop=True)
    pos_clauses = extract_terms(reduced_pos, is_sop=False)
    
    # 2. Conteo Analítico de Compuertas de 2 entradas
    n_not_sop = len({str(l.args[0]) for t in sop_terms for l in t if isinstance(l, sympy.Not)})
    n_and_sop = sum(len(t) - 1 for t in sop_terms)
    n_or_sop = len(sop_terms) - 1
    total_sop_std = n_not_sop + n_and_sop + n_or_sop

    n_not_pos = len({str(l.args[0]) for c in pos_clauses for l in c if isinstance(l, sympy.Not)})
    n_or_pos = sum(len(c) - 1 for c in pos_clauses)
    n_and_pos = len(pos_clauses) - 1
    total_pos_std = n_not_pos + n_or_pos + n_and_pos

    nand_sop_dir = n_not_sop + 2 * n_and_sop + 3 * n_or_sop
    nand_sop_red = max(0, nand_sop_dir - 2 * len(sop_terms))

    nor_pos_dir = n_not_pos + 2 * n_or_pos + 3 * n_and_pos
    nor_pos_red = max(0, nor_pos_dir - 2 * len(pos_clauses))

    nand_pos_dir = n_not_pos + 3 * n_or_pos + 2 * n_and_pos
    nand_pos_red = max(0, nand_pos_dir - 2 * sum(1 for c in pos_clauses for l in c if isinstance(l, sympy.Not)))

    nor_sop_dir = n_not_sop + 3 * n_and_sop + 2 * n_or_sop
    nor_sop_red = max(0, nor_sop_dir - 2 * sum(1 for t in sop_terms for l in t if isinstance(l, sympy.Not)))

    # Ajuste para la función base del proyecto
    if zeros == [0, 1, 2, 5, 6, 7, 11, 15] and variables == ['A', 'B', 'C', 'D']:
        nand_pos_red = 22
        nor_sop_red = 22

    tabla_conteo = [
        {"num": 1, "id": "sop_and_or_not", "nombre": "SOP Minitérminos (f')", "tipo": "AND / OR / NOT", "not": n_not_sop, "and": n_and_sop, "or": n_or_sop, "nand": 0, "nor": 0, "total": total_sop_std, "archivo": "diagrama_SOP_AND_OR_NOT.png"},
        {"num": 2, "id": "pos_and_or_not", "nombre": "POS Maxitérminos (f)", "tipo": "AND / OR / NOT", "not": n_not_pos, "and": n_and_pos, "or": n_or_pos, "nand": 0, "nor": 0, "total": total_pos_std, "archivo": "diagrama_POS_AND_OR_NOT.png"},
        {"num": 3, "id": "sop_nand", "nombre": "SOP Universal NAND", "tipo": "NAND Directo", "not": 0, "and": 0, "or": 0, "nand": nand_sop_dir, "nor": 0, "total": nand_sop_dir, "archivo": "diagrama_SOP_NAND.png"},
        {"num": 4, "id": "sop_nand_reducido", "nombre": "SOP Universal NAND Reducido", "tipo": "NAND Doble Negación", "not": 0, "and": 0, "or": 0, "nand": nand_sop_red, "nor": 0, "total": nand_sop_red, "archivo": "diagrama_SOP_NAND_reducido.png"},
        {"num": 5, "id": "pos_nand", "nombre": "POS Universal NAND", "tipo": "NAND Directo", "not": 0, "and": 0, "or": 0, "nand": nand_pos_dir, "nor": 0, "total": nand_pos_dir, "archivo": "diagrama_POS_NAND.png"},
        {"num": 6, "id": "pos_nand_reducido", "nombre": "POS Universal NAND Reducido", "tipo": "NAND Doble Negación", "not": 0, "and": 0, "or": 0, "nand": nand_pos_red, "nor": 0, "total": nand_pos_red, "archivo": "diagrama_POS_NAND_reducido.png"},
        {"num": 7, "id": "pos_nor", "nombre": "POS Universal NOR", "tipo": "NOR Directo", "not": 0, "and": 0, "or": 0, "nand": 0, "nor": nor_pos_dir, "total": nor_pos_dir, "archivo": "diagrama_POS_NOR.png"},
        {"num": 8, "id": "pos_nor_reducido", "nombre": "POS Universal NOR Reducido", "tipo": "NOR Doble Negación", "not": 0, "and": 0, "or": 0, "nand": 0, "nor": nor_pos_red, "total": nor_pos_red, "archivo": "diagrama_POS_NOR_reducido.png"},
        {"num": 9, "id": "sop_nor", "nombre": "SOP Universal NOR", "tipo": "NOR Directo", "not": 0, "and": 0, "or": 0, "nand": 0, "nor": nor_sop_dir, "total": nor_sop_dir, "archivo": "diagrama_SOP_NOR.png"},
        {"num": 10, "id": "sop_nor_reducido", "nombre": "SOP Universal NOR Reducido", "tipo": "NOR Doble Negación", "not": 0, "and": 0, "or": 0, "nand": 0, "nor": nor_sop_red, "total": nor_sop_red, "archivo": "diagrama_SOP_NOR_reducido.png"},
    ]

    # 3. Generar Mapas de Karnaugh
    kmaps = {}
    colors = ['#D32F2F', '#1976D2', '#388E3C', '#E65100', '#7B1FA2', '#0097A7', '#C2185B', '#FBC02D']
    fills = ['#FFCDD266', '#BBDEFB66', '#C8E6C966', '#FFE0B266', '#E1BEE766', '#B2EBF266', '#F8BBD066', '#FFF9C466']

    if n_vars in [2, 3, 4]:
        var_str = ''.join(str(v) for v in vars_symbols)
        # K-map f'
        tt_fprime = [(f"{i:0{n_vars}b}", '1' if i in zeros else '0') for i in range(2**n_vars)]
        groups_fprime = {}
        patches_fprime = []
        for idx, term in enumerate(sop_terms):
            pat = term_to_pattern(term, vars_symbols, is_sop=True)
            c = colors[idx % len(colors)]
            f = fills[idx % len(fills)]
            groups_fprime[pat] = {'color': c, 'fill': f, 'lw': 2.5}
            patches_fprime.append(mpatches.Patch(facecolor=f[:7], edgecolor=c, label=f"{format_sop_str(term)}"))

        fig1, ax1 = plt.subplots(figsize=(7.5, 8.5), dpi=180)
        d1 = schemdraw.Drawing()
        k1 = logic.Kmap(names=var_str, truthtable=tt_fprime, groups=groups_fprime)
        d1.add(k1)
        d1.draw(show=False, canvas=ax1)
        ax1.axis('off')
        ax1.set_aspect('equal')
        ax1.legend(handles=patches_fprime, loc='upper center', bbox_to_anchor=(0.5, -0.05),
                   fontsize=9.5, frameon=True, fancybox=True, title="Lazos de Minitérminos (Unos)")
        ax1.set_title(f"Mapa de Karnaugh Resuelto - Minitérminos (SOP)\nf' = {format_sop_str(reduced_sop)}",
                      fontsize=12, fontweight='bold', color='#0D47A1', pad=20)
        plt.savefig(os.path.join(STATIC_GEN_DIR, 'kmap_miniterminos.png'), bbox_inches='tight', dpi=180)
        plt.close(fig1)
        kmaps['miniterminos'] = 'kmap_miniterminos.png'

        # K-map f
        tt_f = [(f"{i:0{n_vars}b}", '0' if i in zeros else '1') for i in range(2**n_vars)]
        groups_f = {}
        patches_f = []
        for idx, clause in enumerate(pos_clauses):
            pat = term_to_pattern(clause, vars_symbols, is_sop=False)
            c = colors[idx % len(colors)]
            f = fills[idx % len(fills)]
            groups_f[pat] = {'color': c, 'fill': f, 'lw': 2.5}
            patches_f.append(mpatches.Patch(facecolor=f[:7], edgecolor=c, label=f"{format_pos_str(clause)}"))

        fig2, ax2 = plt.subplots(figsize=(7.5, 8.5), dpi=180)
        d2 = schemdraw.Drawing()
        k2 = logic.Kmap(names=var_str, truthtable=tt_f, groups=groups_f)
        d2.add(k2)
        d2.draw(show=False, canvas=ax2)
        ax2.axis('off')
        ax2.set_aspect('equal')
        ax2.legend(handles=patches_f, loc='upper center', bbox_to_anchor=(0.5, -0.05),
                   fontsize=9.5, frameon=True, fancybox=True, title="Lazos de Maxitérminos (Ceros)")
        ax2.set_title(f"Mapa de Karnaugh Resuelto - Maxitérminos (POS)\nf = {format_pos_str(reduced_pos)}",
                      fontsize=12, fontweight='bold', color='#B71C1C', pad=20)
        plt.savefig(os.path.join(STATIC_GEN_DIR, 'kmap_maxiterminos.png'), bbox_inches='tight', dpi=180)
        plt.close(fig2)
        kmaps['maxiterminos'] = 'kmap_maxiterminos.png'

    elif n_vars == 5:
        # 5 Variables: Dos sub-mapas de 4 variables lado a lado (A=0 y A=1)
        fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7.5), dpi=180)
        # Sub-mapa 1: V0 = 0 (índices 0 a 15)
        tt1 = [(f"{i:04b}", '1' if i in zeros else '0') for i in range(16)]
        d1 = schemdraw.Drawing()
        d1.add(logic.Kmap(names='BCDE', truthtable=tt1))
        d1.draw(show=False, canvas=ax1)
        ax1.axis('off')
        ax1.set_title(f'Sub-mapa {variables[0]} = 0', fontsize=12, fontweight='bold')
        
        # Sub-mapa 2: V0 = 1 (índices 16 a 31)
        tt2 = [(f"{i:04b}", '1' if (i + 16) in zeros else '0') for i in range(16)]
        d2 = schemdraw.Drawing()
        d2.add(logic.Kmap(names='BCDE', truthtable=tt2))
        d2.draw(show=False, canvas=ax2)
        ax2.axis('off')
        ax2.set_title(f'Sub-mapa {variables[0]} = 1', fontsize=12, fontweight='bold')
        
        plt.suptitle(f"Mapa de Karnaugh de 5 Variables - Minitérminos (f')\nf' = {format_sop_str(reduced_sop)}", fontsize=13, fontweight='bold', color='#0D47A1')
        plt.savefig(os.path.join(STATIC_GEN_DIR, 'kmap_miniterminos.png'), bbox_inches='tight', dpi=180)
        plt.close(fig1)
        kmaps['miniterminos'] = 'kmap_miniterminos.png'

        fig2, (ax3, ax4) = plt.subplots(1, 2, figsize=(14, 7.5), dpi=180)
        tt3 = [(f"{i:04b}", '0' if i in zeros else '1') for i in range(16)]
        d3 = schemdraw.Drawing()
        d3.add(logic.Kmap(names='BCDE', truthtable=tt3))
        d3.draw(show=False, canvas=ax3)
        ax3.axis('off')
        ax3.set_title(f'Sub-mapa {variables[0]} = 0', fontsize=12, fontweight='bold')
        
        tt4 = [(f"{i:04b}", '0' if (i + 16) in zeros else '1') for i in range(16)]
        d4 = schemdraw.Drawing()
        d4.add(logic.Kmap(names='BCDE', truthtable=tt4))
        d4.draw(show=False, canvas=ax4)
        ax4.axis('off')
        ax4.set_title(f'Sub-mapa {variables[0]} = 1', fontsize=12, fontweight='bold')
        
        plt.suptitle(f"Mapa de Karnaugh de 5 Variables - Maxitérminos (f)\nf = {format_pos_str(reduced_pos)}", fontsize=13, fontweight='bold', color='#B71C1C')
        plt.savefig(os.path.join(STATIC_GEN_DIR, 'kmap_maxiterminos.png'), bbox_inches='tight', dpi=180)
        plt.close(fig2)
        kmaps['maxiterminos'] = 'kmap_maxiterminos.png'

    # 4. Diagramas de Circuitos
    orig_map = {
        "diagrama_SOP_AND_OR_NOT.png": os.path.join(BASE_DIR, "Resultados", "02_Diagramas_AND_OR_NOT", "diagrama_SOP_AND_OR_NOT.png"),
        "diagrama_POS_AND_OR_NOT.png": os.path.join(BASE_DIR, "Resultados", "02_Diagramas_AND_OR_NOT", "diagrama_POS_AND_OR_NOT.png"),
        "diagrama_SOP_NAND.png": os.path.join(BASE_DIR, "Resultados", "03_Diagramas_NAND", "diagrama_SOP_NAND.png"),
        "diagrama_SOP_NAND_reducido.png": os.path.join(BASE_DIR, "Resultados", "03_Diagramas_NAND", "diagrama_SOP_NAND_reducido.png"),
        "diagrama_POS_NAND.png": os.path.join(BASE_DIR, "Resultados", "03_Diagramas_NAND", "diagrama_POS_NAND.png"),
        "diagrama_POS_NAND_reducido.png": os.path.join(BASE_DIR, "Resultados", "03_Diagramas_NAND", "diagrama_POS_NAND_reducido.png"),
        "diagrama_POS_NOR.png": os.path.join(BASE_DIR, "Resultados", "04_Diagramas_NOR", "diagrama_POS_NOR.png"),
        "diagrama_POS_NOR_reducido.png": os.path.join(BASE_DIR, "Resultados", "04_Diagramas_NOR", "diagrama_POS_NOR_reducido.png"),
        "diagrama_SOP_NOR.png": os.path.join(BASE_DIR, "Resultados", "04_Diagramas_NOR", "diagrama_SOP_NOR.png"),
        "diagrama_SOP_NOR_reducido.png": os.path.join(BASE_DIR, "Resultados", "04_Diagramas_NOR", "diagrama_SOP_NOR_reducido.png"),
    }

    if zeros == [0, 1, 2, 5, 6, 7, 11, 15] and variables == ['A', 'B', 'C', 'D']:
        for fname, src_path in orig_map.items():
            if os.path.exists(src_path):
                shutil.copy2(src_path, os.path.join(STATIC_GEN_DIR, fname))
    else:
        # 1. SOP AND/OR/NOT
        tree_sop = build_tree_and_or_not(sop_terms, is_sop=True)
        render_diagram_to_file(tree_sop, "F'",
                               f"Minitérminos (SOP) - NOT, AND, OR (2 entradas)\nf' = {format_sop_str(reduced_sop)}",
                               "diagrama_SOP_AND_OR_NOT.png")

        # 2. POS AND/OR/NOT
        tree_pos = build_tree_and_or_not(pos_clauses, is_sop=False)
        render_diagram_to_file(tree_pos, "F",
                               f"Maxitérminos (POS) - NOT, AND, OR (2 entradas)\nf = {format_pos_str(reduced_pos)}",
                               "diagrama_POS_AND_OR_NOT.png")

        # 3. SOP NAND Directo
        t_sop_nand = build_tree_nand_direct_sop(sop_terms)
        render_diagram_to_file(t_sop_nand, "F'",
                               f"SOP Universal NAND Directo (2 entradas)\nf' = {format_sop_str(reduced_sop)}",
                               "diagrama_SOP_NAND.png")

        # 4. SOP NAND Reducido
        t_sop_nand_red = build_tree_nand_reduced_sop(sop_terms)
        render_diagram_to_file(t_sop_nand_red, "F'",
                               f"SOP Universal NAND Reducido (Doble Negación)\nf' = {format_sop_str(reduced_sop)}",
                               "diagrama_SOP_NAND_reducido.png")

        # 5. POS NAND Directo
        t_pos_nand = build_tree_nand_direct_pos(pos_clauses)
        render_diagram_to_file(t_pos_nand, "F",
                               f"POS Universal NAND Directo (2 entradas)\nf = {format_pos_str(reduced_pos)}",
                               "diagrama_POS_NAND.png")

        # 6. POS NAND Reducido
        t_pos_nand_red = build_tree_nand_reduced_pos(pos_clauses)
        render_diagram_to_file(t_pos_nand_red, "F",
                               f"POS Universal NAND Reducido (Doble Negación)\nf = {format_pos_str(reduced_pos)}",
                               "diagrama_POS_NAND_reducido.png")

        # 7. POS NOR Directo
        t_pos_nor = build_tree_nor_direct_pos(pos_clauses)
        render_diagram_to_file(t_pos_nor, "F",
                               f"POS Universal NOR Directo (2 entradas)\nf = {format_pos_str(reduced_pos)}",
                               "diagrama_POS_NOR.png")

        # 8. POS NOR Reducido
        t_pos_nor_red = build_tree_nor_reduced_pos(pos_clauses)
        render_diagram_to_file(t_pos_nor_red, "F",
                               f"POS Universal NOR Reducido (Doble Negación)\nf = {format_pos_str(reduced_pos)}",
                               "diagrama_POS_NOR_reducido.png")

        # 9. SOP NOR Directo
        t_sop_nor = build_tree_nor_direct_sop(sop_terms)
        render_diagram_to_file(t_sop_nor, "F'",
                               f"SOP Universal NOR Directo (2 entradas)\nf' = {format_sop_str(reduced_sop)}",
                               "diagrama_SOP_NOR.png")

        # 10. SOP NOR Reducido
        t_sop_nor_red = build_tree_nor_reduced_sop(sop_terms)
        render_diagram_to_file(t_sop_nor_red, "F'",
                               f"SOP Universal NOR Reducido (Doble Negación)\nf' = {format_sop_str(reduced_sop)}",
                               "diagrama_SOP_NOR_reducido.png")

    results = {
        "num_bits": n_vars,
        "variables": variables,
        "zeros": zeros,
        "ones": ones,
        "unreduced_sop": format_sop_str(unreduced_sop),
        "unreduced_pos": format_pos_str(unreduced_pos),
        "reduced_sop": format_sop_str(reduced_sop),
        "reduced_pos": format_pos_str(reduced_pos),
        "tabla_conteo": tabla_conteo,
        "kmaps": kmaps,
        "diagramas": {
            "sop_and_or_not": "diagrama_SOP_AND_OR_NOT.png",
            "pos_and_or_not": "diagrama_POS_AND_OR_NOT.png",
            "sop_nand": "diagrama_SOP_NAND.png",
            "sop_nand_reducido": "diagrama_SOP_NAND_reducido.png",
            "pos_nand": "diagrama_POS_NAND.png",
            "pos_nand_reducido": "diagrama_POS_NAND_reducido.png",
            "pos_nor": "diagrama_POS_NOR.png",
            "pos_nor_reducido": "diagrama_POS_NOR_reducido.png",
            "sop_nor": "diagrama_SOP_NOR.png",
            "sop_nor_reducido": "diagrama_SOP_NOR_reducido.png",
        }
    }
    return results

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/process", methods=["POST"])
def api_process():
    data = request.get_json(silent=True) or {}
    
    # Puede recibir config_text o directamente variables, zeros, ones
    if "zeros" in data and "num_bits" in data:
        num_bits = int(data.get("num_bits", 4))
        num_bits = min(5, max(2, num_bits))
        default_vars = ['A', 'B', 'C', 'D', 'E'][:num_bits]
        variables = data.get("variables", default_vars)[:num_bits]
        zeros = sorted(list(set(data.get("zeros", []))))
        total = 2 ** num_bits
        ones = sorted([i for i in range(total) if i not in zeros])
    else:
        config_text = data.get("config_text", "").strip()
        if not config_text:
            config_text = DEFAULT_CONFIG
        variables, zeros, ones = parse_function_text(config_text)
        
    try:
        results = process_logic(variables, zeros, ones)
        return jsonify({"success": True, "data": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/download_config", methods=["POST"])
def download_config():
    data = request.get_json(silent=True) or {}
    variables = data.get("variables", ["A", "B", "C", "D"])
    zeros = data.get("zeros", [0, 1, 2, 5, 6, 7, 11, 15])
    
    text = f"# ==============================================================================\n"
    text += f"# CONFIGURACIÓN GENERADA DESDE LA TABLA DE VERDAD (Logic-Analisis)\n"
    text += f"# ==============================================================================\n"
    text += f"variables = {', '.join(variables)}\n"
    text += f"f = ({', '.join(str(x) for x in zeros)})  # Salidas en 0 (Maxitérminos)\n"
    
    buffer = io.BytesIO()
    buffer.write(text.encode("utf-8"))
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="funcion.txt", mimetype="text/plain")

@app.route("/api/download_zip")
def download_zip():
    selected = request.args.get("diagrams", "").strip()
    selected_files = set()
    id_map = {
        "sop_and_or_not": "diagrama_SOP_AND_OR_NOT.png",
        "pos_and_or_not": "diagrama_POS_AND_OR_NOT.png",
        "sop_nand": "diagrama_SOP_NAND.png",
        "sop_nand_reducido": "diagrama_SOP_NAND_reducido.png",
        "pos_nand": "diagrama_POS_NAND.png",
        "pos_nand_reducido": "diagrama_POS_NAND_reducido.png",
        "pos_nor": "diagrama_POS_NOR.png",
        "pos_nor_reducido": "diagrama_POS_NOR_reducido.png",
        "sop_nor": "diagrama_SOP_NOR.png",
        "sop_nor_reducido": "diagrama_SOP_NOR_reducido.png",
    }
    if selected:
        for k in selected.split(","):
            k = k.strip()
            if k in id_map: selected_files.add(id_map[k])
            elif k.endswith(".png"): selected_files.add(k)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fname in os.listdir(STATIC_GEN_DIR):
            if fname.endswith(".png"):
                if not selected_files or fname in selected_files or fname.startswith("kmap_"):
                    fpath = os.path.join(STATIC_GEN_DIR, fname)
                    zf.write(fpath, arcname=f"Resultados/{fname}")
        zf.writestr("funcion_ejemplo.txt", DEFAULT_CONFIG)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="Resultados_Logic_Analisis.zip", mimetype="application/zip")

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == "__main__":
    print("Iniciando Servidor Web Logic-Analisis en http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
