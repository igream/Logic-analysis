# -*- coding: utf-8 -*-
"""
Módulo de Lógica y Deducción Booleana
Maneja minitérminos, maxitérminos y simplificaciones con SymPy.
"""
import sympy
from sympy.logic.boolalg import simplify_logic

def format_sop_str(expr):
    if expr in [sympy.false, False, 0]: return "0"
    if expr in [sympy.true, True, 1]: return "1"
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
    if expr in [sympy.false, False, 0]: return "(0)"
    if expr in [sympy.true, True, 1]: return "(1)"
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
    if expr in [sympy.false, False, 0]:
        return []
    if expr in [sympy.true, True, 1]:
        return []
    top_cls = sympy.Or if is_sop else sympy.And
    sub_cls = sympy.And if is_sop else sympy.Or
    terms = list(expr.args) if isinstance(expr, top_cls) else [expr]
    res = []
    for t in terms:
        lits = list(t.args) if isinstance(t, sub_cls) else [t]
        res.append(lits)
    return res

def deduce_and_simplify(variables, zeros, ones):
    vars_symbols = [sympy.Symbol(v) for v in variables]
    n_vars = len(vars_symbols)

    # Minitérminos de f (salidas en 1 de f)
    minterms_f = []
    for i in ones:
        lits = []
        for j, v in enumerate(vars_symbols):
            if (i & (1 << (n_vars - 1 - j))) == 0:
                lits.append(sympy.Not(v))
            else:
                lits.append(v)
        minterms_f.append(sympy.And(*lits))
    unreduced_sop = sympy.Or(*minterms_f) if minterms_f else sympy.false

    # Maxitérminos de f (salidas en 0 de f)
    maxterms_f = []
    for i in zeros:
        lits = []
        for j, v in enumerate(vars_symbols):
            if (i & (1 << (n_vars - 1 - j))) == 0:
                lits.append(v)
            else:
                lits.append(sympy.Not(v))
        maxterms_f.append(sympy.Or(*lits))
    unreduced_pos = sympy.And(*maxterms_f) if maxterms_f else sympy.true

    reduced_sop = simplify_logic(unreduced_sop, form='dnf')
    reduced_pos = simplify_logic(unreduced_pos, form='cnf')

    # Verificación estricta de legitimidad y equivalencia lógica: SOP(f) == POS(f) == f
    if reduced_sop == reduced_pos:
        is_equivalent = True
    elif reduced_sop in [sympy.true, True, 1] and reduced_pos in [sympy.true, True, 1]:
        is_equivalent = True
    elif reduced_sop in [sympy.false, False, 0] and reduced_pos in [sympy.false, False, 0]:
        is_equivalent = True
    else:
        try:
            equiv_expr = simplify_logic(sympy.Equivalent(reduced_sop, reduced_pos))
            is_equivalent = (equiv_expr == sympy.true)
        except Exception:
            is_equivalent = False

    sop_terms = extract_terms(reduced_sop, is_sop=True)
    pos_clauses = extract_terms(reduced_pos, is_sop=False)

    return {
        "vars_symbols": vars_symbols,
        "n_vars": n_vars,
        "unreduced_sop": unreduced_sop,
        "unreduced_pos": unreduced_pos,
        "reduced_sop": reduced_sop,
        "reduced_pos": reduced_pos,
        "is_equivalent": is_equivalent,
        "sop_terms": sop_terms,
        "pos_clauses": pos_clauses
    }

