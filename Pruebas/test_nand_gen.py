import sympy
from sympy.logic.boolalg import simplify_logic
import schemdraw
from schemdraw.parsing import logicparse

# Helpers for general NAND / NOR tree generation
def build_sop_nand_direct(terms):
    # terms is list of lists of literals (SymPy symbols or Not(symbol))
    term_strings = []
    for t in terms:
        lits = []
        for l in t:
            if isinstance(l, sympy.Not):
                v = str(l.args[0])
                lits.append(f"({v} nand {v})")
            else:
                lits.append(str(l))
        # AND tree in NAND
        def nand_and(items):
            if len(items) == 1: return items[0]
            m = len(items) // 2
            left = nand_and(items[:m])
            right = nand_and(items[m:])
            t = f"({left} nand {right})"
            return f"({t} nand {t})"
        term_strings.append(nand_and(lits))
    
    def nand_or(items):
        if len(items) == 1: return items[0]
        m = len(items) // 2
        left = nand_or(items[:m])
        right = nand_or(items[m:])
        return f"(({left} nand {left}) nand ({right} nand {right}))"
        
    return nand_or(term_strings)

def build_sop_nand_reduced(terms):
    # AND terms with output NOT omitted (i.e. (term)')
    term_neg_strings = []
    for t in terms:
        lits = []
        for l in t:
            if isinstance(l, sympy.Not):
                v = str(l.args[0])
                lits.append(f"({v} nand {v})")
            else:
                lits.append(str(l))
        # AND tree leaving outer NAND as neg
        def nand_and_neg(items):
            if len(items) == 1: 
                # a single literal x -> needs to be x'
                return f"({items[0]} nand {items[0]})"
            if len(items) == 2:
                return f"({items[0]} nand {items[1]})"
            m = len(items) // 2
            left = nand_and_neg(items[:m])
            # left is already inverted, invert back
            left_pos = f"({left} nand {left})"
            right = nand_and_neg(items[m:])
            right_pos = f"({right} nand {right})"
            return f"({left_pos} nand {right_pos})"
        term_neg_strings.append(nand_and_neg(lits))
        
    # First level of OR pairs connects (Ti)' and (Tj)' directly to NAND: (Ti)' nand (Tj)' = Ti + Tj
    if len(term_neg_strings) == 1:
        return f"({term_neg_strings[0]} nand {term_neg_strings[0]})"
    
    # Group in pairs for level 1
    level1 = []
    for i in range(0, len(term_neg_strings), 2):
        if i + 1 < len(term_neg_strings):
            level1.append(f"({term_neg_strings[i]} nand {term_neg_strings[i+1]})")
        else:
            # lone term: (Ti)' inverted -> Ti
            level1.append(f"({term_neg_strings[i]} nand {term_neg_strings[i]})")
            
    # Remaining levels are normal OR in NAND
    def nand_or(items):
        if len(items) == 1: return items[0]
        m = len(items) // 2
        left = nand_or(items[:m])
        right = nand_or(items[m:])
        return f"(({left} nand {left}) nand ({right} nand {right}))"
        
    return nand_or(level1)

A, B, C, D = sympy.symbols('A B C D')
terms = [[sympy.Not(A), sympy.Not(B), sympy.Not(C)],
         [sympy.Not(A), C, sympy.Not(D)],
         [sympy.Not(A), B, D],
         [A, C, D]]

s_dir = build_sop_nand_direct(terms)
print("SOP NAND Direct len:", len(s_dir))
d1 = logicparse(s_dir, outlabel="F'")
print("Direct parsed successfully!")

s_red = build_sop_nand_reduced(terms)
print("SOP NAND Reduced len:", len(s_red))
d2 = logicparse(s_red, outlabel="F'")
print("Reduced parsed successfully!")
