# -*- coding: utf-8 -*-
"""
Módulo de Síntesis de Árboles de Circuitos con Compuertas Estrictas de 2 Entradas
Construye árboles lógicos (LogicTree) optimizados para las 10 familias de circuitos,
eliminando completamente la duplicación exponencial de compuertas.
"""

from schemdraw.parsing.logic_parser import LogicTree
import sympy

def make_binary_tree(items, op):
    """Construye un árbol binario equilibrado de 2 entradas para una lista de nodos/literales."""
    if not items:
        return None
    if len(items) == 1:
        return items[0] if isinstance(items[0], LogicTree) else LogicTree(str(items[0]))
    mid = len(items) // 2
    left = make_binary_tree(items[:mid], op)
    right = make_binary_tree(items[mid:], op)
    return LogicTree(op, left, right)

def make_binary_2in_gate(items, make_gate_fn):
    """Aplica una función de síntesis de 2 entradas en árbol binario equilibrado."""
    if not items:
        return None
    if len(items) == 1:
        return items[0] if isinstance(items[0], LogicTree) else LogicTree(str(items[0]))
    mid = len(items) // 2
    left = make_binary_2in_gate(items[:mid], make_gate_fn)
    right = make_binary_2in_gate(items[mid:], make_gate_fn)
    return make_gate_fn(left, right)


# 1 & 2. AND / OR / NOT (2 entradas)
def build_tree_and_or_not(terms, is_sop=True):
    """
    Sintetiza árbol estándar con compuertas AND, OR y NOT de 2 entradas.
    is_sop=True  -> Minitérminos: ANDs agrupados por OR.
    is_sop=False -> Maxitérminos: ORs agrupados por AND.
    """
    if not terms or terms == [[False]] or terms == [[True]]:
        return None
    term_op = 'and' if is_sop else 'or'
    top_op = 'or' if is_sop else 'and'
    term_trees = []
    for t in terms:
        lits = [LogicTree('not', LogicTree(str(l.args[0]))) if isinstance(l, sympy.Not) else LogicTree(str(l)) for l in t]
        term_trees.append(make_binary_tree(lits, term_op))
    return make_binary_tree(term_trees, top_op)


# 3. SOP Universal NAND Directo
def build_tree_nand_direct_sop(terms):
    """
    SOP NAND Directo:
    - Inversores: inv_nand (NAND de 2 entradas puenteadas).
    - AND de 2 entradas: NAND seguido de inv_nand.
    - OR de 2 entradas: inv_nand en cada entrada seguido de NAND.
    """
    if not terms or terms == [[False]] or terms == [[True]]:
        return None
    def nand_and_2(x, y):
        return LogicTree('inv_nand', LogicTree('nand', x, y))
    def nand_or_2(x, y):
        return LogicTree('nand', LogicTree('inv_nand', x), LogicTree('inv_nand', y))
    term_trees = []
    for t in terms:
        lits = [LogicTree('inv_nand', LogicTree(str(l.args[0]))) if isinstance(l, sympy.Not) else LogicTree(str(l)) for l in t]
        term_trees.append(make_binary_2in_gate(lits, nand_and_2))
    return make_binary_2in_gate(term_trees, nand_or_2)


# 4. SOP Universal NAND Reducido (Doble Negación)
def build_tree_nand_reduced_sop(terms):
    """
    SOP NAND Reducido (2 niveles NAND-NAND):
    - Literales negados: inv_nand.
    - Términos producto: sintetizados con NANDs de 2 entradas.
    - Suma (OR): cancelación de doble negación en la frontera AND-OR;
      los términos entran directamente al árbol de NANDs.
    """
    if not terms or terms == [[False]] or terms == [[True]]:
        return None
    term_trees = []
    for t in terms:
        lits = [LogicTree('inv_nand', LogicTree(str(l.args[0]))) if isinstance(l, sympy.Not) else LogicTree(str(l)) for l in t]
        if len(lits) == 1:
            l = t[0]
            term_trees.append(LogicTree(str(l.args[0])) if isinstance(l, sympy.Not) else LogicTree('inv_nand', LogicTree(str(l))))
        elif len(lits) == 2:
            term_trees.append(LogicTree('nand', lits[0], lits[1]))
        else:
            cur = LogicTree('nand', lits[0], lits[1])
            for extra in lits[2:]:
                cur = LogicTree('nand', LogicTree('inv_nand', cur), extra)
            term_trees.append(cur)
    if len(term_trees) == 1:
        return LogicTree('inv_nand', term_trees[0])
    return make_binary_tree(term_trees, 'nand')


# 5. POS Universal NAND Directo
def build_tree_nand_direct_pos(clauses):
    """
    POS NAND Directo:
    - Inversores: inv_nand.
    - OR de 2 entradas: inv_nand en cada entrada seguido de NAND.
    - AND de 2 entradas: NAND seguido de inv_nand.
    """
    if not clauses or clauses == [[False]] or clauses == [[True]]:
        return None
    def nand_or_2(x, y):
        return LogicTree('nand', LogicTree('inv_nand', x), LogicTree('inv_nand', y))
    def nand_and_2(x, y):
        return LogicTree('inv_nand', LogicTree('nand', x, y))
    clause_trees = []
    for c in clauses:
        lits = [LogicTree('inv_nand', LogicTree(str(l.args[0]))) if isinstance(l, sympy.Not) else LogicTree(str(l)) for l in c]
        clause_trees.append(make_binary_2in_gate(lits, nand_or_2))
    return make_binary_2in_gate(clause_trees, nand_and_2)


# 6. POS Universal NAND Reducido
def build_tree_nand_reduced_pos(clauses):
    """
    POS NAND Reducido:
    - Cancelación de dobles negaciones en literales negados de las sumas:
      (A + B') = NAND(inv_nand(A), B).
    - Salidas de sumas agrupadas por árbol AND de 2 entradas con NAND.
    """
    if not clauses or clauses == [[False]] or clauses == [[True]]:
        return None
    def nand_and_2(x, y):
        return LogicTree('inv_nand', LogicTree('nand', x, y))
    clause_trees = []
    for c in clauses:
        lits = [LogicTree(str(l.args[0])) if isinstance(l, sympy.Not) else LogicTree('inv_nand', LogicTree(str(l))) for l in c]
        if len(lits) == 1:
            clause_trees.append(lits[0])
        elif len(lits) == 2:
            clause_trees.append(LogicTree('nand', lits[0], lits[1]))
        else:
            cur = LogicTree('nand', lits[0], lits[1])
            for extra in lits[2:]:
                cur = LogicTree('nand', LogicTree('inv_nand', cur), extra)
            clause_trees.append(cur)
    return make_binary_2in_gate(clause_trees, nand_and_2)


# 7. POS Universal NOR Directo
def build_tree_nor_direct_pos(clauses):
    """
    POS NOR Directo:
    - Inversores: inv_nor (NOR de 2 entradas puenteadas).
    - OR de 2 entradas: NOR seguido de inv_nor.
    - AND de 2 entradas: inv_nor en cada entrada seguido de NOR.
    """
    if not clauses or clauses == [[False]] or clauses == [[True]]:
        return None
    def nor_or_2(x, y):
        return LogicTree('inv_nor', LogicTree('nor', x, y))
    def nor_and_2(x, y):
        return LogicTree('nor', LogicTree('inv_nor', x), LogicTree('inv_nor', y))
    clause_trees = []
    for c in clauses:
        lits = [LogicTree('inv_nor', LogicTree(str(l.args[0]))) if isinstance(l, sympy.Not) else LogicTree(str(l)) for l in c]
        clause_trees.append(make_binary_2in_gate(lits, nor_or_2))
    return make_binary_2in_gate(clause_trees, nor_and_2)


# 8. POS Universal NOR Reducido (Doble Negación)
def build_tree_nor_reduced_pos(clauses):
    """
    POS NOR Reducido (2 niveles NOR-NOR):
    - Literales negados: inv_nor.
    - Cláusulas suma: sintetizadas con NORs de 2 entradas.
    - Producto (AND): cancelación de doble negación en la frontera OR-AND;
      las cláusulas entran directamente al árbol de NORs.
    """
    if not clauses or clauses == [[False]] or clauses == [[True]]:
        return None
    clause_trees = []
    for c in clauses:
        lits = [LogicTree('inv_nor', LogicTree(str(l.args[0]))) if isinstance(l, sympy.Not) else LogicTree(str(l)) for l in c]
        if len(lits) == 1:
            l = c[0]
            clause_trees.append(LogicTree(str(l.args[0])) if isinstance(l, sympy.Not) else LogicTree('inv_nor', LogicTree(str(l))))
        elif len(lits) == 2:
            clause_trees.append(LogicTree('nor', lits[0], lits[1]))
        else:
            cur = LogicTree('nor', lits[0], lits[1])
            for extra in lits[2:]:
                cur = LogicTree('nor', LogicTree('inv_nor', cur), extra)
            clause_trees.append(cur)
    if len(clause_trees) == 1:
        return LogicTree('inv_nor', clause_trees[0])
    return make_binary_tree(clause_trees, 'nor')


# 9. SOP Universal NOR Directo
def build_tree_nor_direct_sop(terms):
    """
    SOP NOR Directo:
    - Inversores: inv_nor.
    - AND de 2 entradas: inv_nor en cada entrada seguido de NOR.
    - OR de 2 entradas: NOR seguido de inv_nor.
    """
    if not terms or terms == [[False]] or terms == [[True]]:
        return None
    def nor_and_2(x, y):
        return LogicTree('nor', LogicTree('inv_nor', x), LogicTree('inv_nor', y))
    def nor_or_2(x, y):
        return LogicTree('inv_nor', LogicTree('nor', x, y))
    term_trees = []
    for t in terms:
        lits = [LogicTree('inv_nor', LogicTree(str(l.args[0]))) if isinstance(l, sympy.Not) else LogicTree(str(l)) for l in t]
        term_trees.append(make_binary_2in_gate(lits, nor_and_2))
    return make_binary_2in_gate(term_trees, nor_or_2)


# 10. SOP Universal NOR Reducido
def build_tree_nor_reduced_sop(terms):
    """
    SOP NOR Reducido:
    - Cancelación de dobles negaciones en literales negados de los productos:
      (A · B') = NOR(inv_nor(A), B).
    - Salidas de productos agrupadas por árbol OR de 2 entradas con NOR.
    """
    if not terms or terms == [[False]] or terms == [[True]]:
        return None
    def nor_or_2(x, y):
        return LogicTree('inv_nor', LogicTree('nor', x, y))
    term_trees = []
    for t in terms:
        lits = [LogicTree(str(l.args[0])) if isinstance(l, sympy.Not) else LogicTree('inv_nor', LogicTree(str(l))) for l in t]
        if len(lits) == 1:
            term_trees.append(lits[0])
        elif len(lits) == 2:
            term_trees.append(LogicTree('nor', lits[0], lits[1]))
        else:
            cur = LogicTree('nor', lits[0], lits[1])
            for extra in lits[2:]:
                cur = LogicTree('nor', LogicTree('inv_nor', cur), extra)
            term_trees.append(cur)
    return make_binary_2in_gate(term_trees, nor_or_2)


