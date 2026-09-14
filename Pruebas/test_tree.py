import sympy
from sympy.logic.boolalg import simplify_logic
import schemdraw
from schemdraw.parsing import logicparse

A, B, C, D = sympy.symbols('A B C D')
vars_list = [A, B, C, D]
f_zeros = [0, 1, 2, 5, 6, 7, 11, 15]

# SOP
minterms = []
for i in f_zeros:
    lits = [v if (i & (1 << (3-j))) else sympy.Not(v) for j, v in enumerate(vars_list)]
    minterms.append(sympy.And(*lits))
sop = simplify_logic(sympy.Or(*minterms), form='dnf')
print('SOP:', sop)

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
    if len(items) == 1:
        return items[0]
    mid = len(items) // 2
    left = make_binary_tree(items[:mid], op)
    right = make_binary_tree(items[mid:], op)
    return f"({left} {op} {right})"

terms = extract_terms(sop, is_sop=True)
term_trees = []
for t in terms:
    l_strs = [f"(not {l.args[0]})" if isinstance(l, sympy.Not) else str(l) for l in t]
    term_trees.append(make_binary_tree(l_strs, 'and'))
full_tree = make_binary_tree(term_trees, 'or')
print('Full tree:', full_tree)

d = logicparse(full_tree, outlabel="F'")
print('Parsed successfully!')
