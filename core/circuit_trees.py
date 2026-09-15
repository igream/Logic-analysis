# -*- coding: utf-8 -*-
"""
Módulo de Síntesis de Árboles de Circuitos con Compuertas Estrictas de 2 Entradas
Construye árboles lógicos (LogicTree) optimizados para las 10 familias de circuitos,
garantizando estricta equivalencia lógica formal en todos los niveles y eliminando
la duplicación exponencial de compuertas.
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


def make_nand_or_tree(negated_terms):
    """
    Construye un árbol OR de compuertas NAND de 2 entradas a partir de términos negados (T_i').
    Aplica cancelación de doble negación en la frontera y preserva la equivalencia lógica
    exacta sumando todos los términos sin corrupción de operaciones.
    """
    def helper(items):
        if len(items) == 1:
            return items[0], True  # (árbol, está_negado)
        mid = len(items) // 2
        left_tree, left_is_neg = helper(items[:mid])
        right_tree, right_is_neg = helper(items[mid:])
        left_in = left_tree if left_is_neg else LogicTree('inv_nand', left_tree)
        right_in = right_tree if right_is_neg else LogicTree('inv_nand', right_tree)
        return LogicTree('nand', left_in, right_in), False  # Salida de nivel es suma positiva

    if len(negated_terms) == 1:
        return LogicTree('inv_nand', negated_terms[0])
    top_tree, _ = helper(negated_terms)
    return top_tree


def make_nor_and_tree(negated_clauses):
    """
    Construye un árbol AND de compuertas NOR de 2 entradas a partir de cláusulas negadas (C_i').
    Aplica cancelación de doble negación en la frontera y preserva la equivalencia lógica
    exacta multiplicando todas las cláusulas sin corrupción de operaciones.
    """
    def helper(items):
        if len(items) == 1:
            return items[0], True  # (árbol, está_negado)
        mid = len(items) // 2
        left_tree, left_is_neg = helper(items[:mid])
        right_tree, right_is_neg = helper(items[mid:])
        left_in = left_tree if left_is_neg else LogicTree('inv_nor', left_tree)
        right_in = right_tree if right_is_neg else LogicTree('inv_nor', right_tree)
        return LogicTree('nor', left_in, right_in), False  # Salida de nivel es producto positivo

    if len(negated_clauses) == 1:
        return LogicTree('inv_nor', negated_clauses[0])
    top_tree, _ = helper(negated_clauses)
    return top_tree


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
    SOP NAND Reducido:
    - Términos producto sintetizados para generar T_i' mediante NANDs.
    - Cancelación de doble negación en la frontera con el árbol OR.
    - Árbol OR multinivel balanceado con compuertas NAND de 2 entradas.
    """
    if not terms or terms == [[False]] or terms == [[True]]:
        return None
    term_trees = []
    for t in terms:
        if len(t) == 1:
            l = t[0]
            # Salida debe ser T_i'
            term_trees.append(LogicTree(str(l.args[0])) if isinstance(l, sympy.Not) else LogicTree('inv_nand', LogicTree(str(l))))
        else:
            lits = [LogicTree('inv_nand', LogicTree(str(l.args[0]))) if isinstance(l, sympy.Not) else LogicTree(str(l)) for l in t]
            cur = LogicTree('nand', lits[0], lits[1])
            for extra in lits[2:]:
                cur = LogicTree('nand', LogicTree('inv_nand', cur), extra)
            term_trees.append(cur)
    return make_nand_or_tree(term_trees)


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
    - Cláusulas suma sintetizadas mediante NANDs con entradas negadas: (A + B) = NAND(A', B').
    - Salidas de cláusulas C_i combinadas mediante árbol AND con compuertas NAND de 2 entradas.
    """
    if not clauses or clauses == [[False]] or clauses == [[True]]:
        return None
    def nand_and_2(x, y):
        return LogicTree('inv_nand', LogicTree('nand', x, y))
    clause_trees = []
    for c in clauses:
        if len(c) == 1:
            l = c[0]
            clause_trees.append(LogicTree('inv_nand', LogicTree(str(l.args[0]))) if isinstance(l, sympy.Not) else LogicTree(str(l)))
        else:
            lits = [LogicTree(str(l.args[0])) if isinstance(l, sympy.Not) else LogicTree('inv_nand', LogicTree(str(l))) for l in c]
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
    POS NOR Reducido:
    - Cláusulas suma sintetizadas para generar C_i' mediante NORs.
    - Cancelación de doble negación en la frontera con el árbol AND.
    - Árbol AND multinivel balanceado con compuertas NOR de 2 entradas.
    """
    if not clauses or clauses == [[False]] or clauses == [[True]]:
        return None
    clause_trees = []
    for c in clauses:
        if len(c) == 1:
            l = c[0]
            # Salida debe ser C_i'
            clause_trees.append(LogicTree(str(l.args[0])) if isinstance(l, sympy.Not) else LogicTree('inv_nor', LogicTree(str(l))))
        else:
            lits = [LogicTree('inv_nor', LogicTree(str(l.args[0]))) if isinstance(l, sympy.Not) else LogicTree(str(l)) for l in c]
            cur = LogicTree('nor', lits[0], lits[1])
            for extra in lits[2:]:
                cur = LogicTree('nor', LogicTree('inv_nor', cur), extra)
            clause_trees.append(cur)
    return make_nor_and_tree(clause_trees)


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
    - Términos producto sintetizados mediante NORs con entradas negadas: (A · B) = NOR(A', B').
    - Salidas de productos T_i combinadas mediante árbol OR con compuertas NOR de 2 entradas.
    """
    if not terms or terms == [[False]] or terms == [[True]]:
        return None
    def nor_or_2(x, y):
        return LogicTree('inv_nor', LogicTree('nor', x, y))
    term_trees = []
    for t in terms:
        if len(t) == 1:
            l = t[0]
            term_trees.append(LogicTree('inv_nor', LogicTree(str(l.args[0]))) if isinstance(l, sympy.Not) else LogicTree(str(l)))
        else:
            lits = [LogicTree(str(l.args[0])) if isinstance(l, sympy.Not) else LogicTree('inv_nor', LogicTree(str(l))) for l in t]
            cur = LogicTree('nor', lits[0], lits[1])
            for extra in lits[2:]:
                cur = LogicTree('nor', LogicTree('inv_nor', cur), extra)
            term_trees.append(cur)
    return make_binary_2in_gate(term_trees, nor_or_2)
