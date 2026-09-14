# -*- coding: utf-8 -*-
"""
Módulo de Síntesis de Árboles Binarios de Circuitos
Genera expresiones de interconexión con compuertas estrictas de 2 entradas
para las 10 familias lógicas analizadas.
"""
import sympy

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
        if len(items) == 1: return items[0]
        m = len(items) // 2
        l = nor_and(items[:m])
        r = nor_and(items[m:])
        return f"(({l} nor {l}) nor ({r} nor {r}))"
    term_strings = []
    for t in terms:
        lits = [f"({l.args[0]} nor {l.args[0]})" if isinstance(l, sympy.Not) else str(l) for l in t]
        term_strings.append(nor_and(lits))
    def nor_or(items):
        if len(items) == 1: return items[0]
        m = len(items) // 2
        t = f"({nor_or(items[:m])} nor {nor_or(items[m:])})"
        return f"({t} nor {t})"
    return nor_or(term_strings)

def build_tree_nor_reduced_sop(terms):
    # Por dualidad y simetría con POS NAND reducido
    return build_tree_nor_direct_sop(terms)

