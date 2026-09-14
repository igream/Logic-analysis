import sys
if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

import sympy
from sympy.logic.boolalg import SOPform, POSform, simplify_logic
import schemdraw
import schemdraw.logic as logic
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import re

import re

def format_sop(expr):
    s = str(expr)
    s = s.replace(' & ', '')
    s = s.replace(' | ', ' + ')
    s = re.sub(r'~([A-Z])', r"\1'", s)
    s = s.replace('(', '').replace(')', '')
    return s

def format_pos(expr):
    s = str(expr)
    s = s.replace(' | ', '+')
    s = s.replace(' & ', '')
    s = re.sub(r'~([A-Z])', r"\1'", s)
    return s

def format_expr(expr, is_pos=False):
    if is_pos:
        s = str(expr)
        s = s.replace(' | ', '+')
        s = s.replace(' & ', '')
        s = re.sub(r'~([A-Z])', r"\1'", s)
        return s
    else:
        s = str(expr)
        s = s.replace(' & ', '')
        s = s.replace(' | ', ' + ')
        s = re.sub(r'~([A-Z])', r"\1'", s)
        s = s.replace('(', '').replace(')', '')
        return s

def main():
    A, B, C, D = sympy.symbols('A B C D')
    vars = [A, B, C, D]
    minterms_indices = [0, 1, 2, 5, 6, 7, 11, 15]
    
    # 1. Unreduced minterm expression for f'
    minterms = []
    for i in minterms_indices:
        term = []
        for j, v in enumerate(vars):
            if (i & (1 << (3-j))) == 0:
                term.append(sympy.Not(v))
            else:
                term.append(v)
        minterms.append(sympy.And(*term))
    
    unreduced_sop = sympy.Or(*minterms)
    
    # 2. Unreduced maxterm expression for f
    maxterms = []
    for i in minterms_indices:
        term = []
        for j, v in enumerate(vars):
            # For maxterm i, if bit is 1 it's ~v, if 0 it's v
            if (i & (1 << (3-j))) == 0:
                term.append(v)
            else:
                term.append(sympy.Not(v))
        maxterms.append(sympy.Or(*term))
        
    unreduced_pos = sympy.And(*maxterms)
    
    # 3. Reduced minterm expression for f'
    reduced_sop = simplify_logic(unreduced_sop, form='dnf')
    
    # 4. Reduced maxterm expression for f
    reduced_pos = simplify_logic(unreduced_pos, form='cnf')
    
    print("1. Unreduced minterm expression for f':")
    print("f' =", format_expr(unreduced_sop))
    print("\n2. Unreduced maxterm expression for f:")
    print("f =", format_expr(unreduced_pos, is_pos=True))
    print("\n3. Reduced minterm expression for f':")
    print("f' =", format_expr(reduced_sop))
    print("\n4. Reduced maxterm expression for f:")
    print("f =", format_expr(reduced_pos, is_pos=True))
    
    # Generating K-map images
    
    # f' Truth table
    tt_fprime = [('0000', 1), ('0001', 1), ('0010', 1), ('0011', 0),
                 ('0100', 0), ('0101', 1), ('0110', 1), ('0111', 1),
                 ('1000', 0), ('1001', 0), ('1010', 0), ('1011', 1),
                 ('1100', 0), ('1101', 0), ('1110', 0), ('1111', 1)]
    
    groups_fprime = {
        '000.': {'color': 'red', 'fill': '#ff000033'},
        '0.10': {'color': 'blue', 'fill': '#0000ff33'},
        '01.1': {'color': 'green', 'fill': '#00ff0033'},
        '1.11': {'color': 'orange', 'fill': '#ffa50033'}
    }
    
    fig1 = plt.figure(figsize=(8, 9), dpi=300)
    d1 = schemdraw.Drawing(canvas=fig1.gca())
    k1 = logic.Kmap(names='ABCD', truthtable=tt_fprime, groups=groups_fprime)
    d1.add(k1)
    
    patches1 = [
        mpatches.Patch(color='red', label="A'B'C'", alpha=0.2),
        mpatches.Patch(color='blue', label="A'CD'", alpha=0.2),
        mpatches.Patch(color='green', label="A'BD", alpha=0.2),
        mpatches.Patch(color='orange', label="ACD", alpha=0.2)
    ]
    plt.legend(handles=patches1, loc='upper right')
    plt.title(f"K-map f' Minterms (SOP)\nf' = {format_expr(reduced_sop)}")
    plt.axis('off')
    d1.save('kmap_miniterminos_fprime.png')
    plt.close(fig1)

    # f Truth table
    tt_f = [('0000', 0), ('0001', 0), ('0010', 0), ('0011', 1),
            ('0100', 1), ('0101', 0), ('0110', 0), ('0111', 0),
            ('1000', 1), ('1001', 1), ('1010', 1), ('1011', 0),
            ('1100', 1), ('1101', 1), ('1110', 1), ('1111', 0)]
            
    groups_f = {
        '000.': {'color': 'red', 'fill': '#ff000033'},
        '0.10': {'color': 'blue', 'fill': '#0000ff33'},
        '01.1': {'color': 'green', 'fill': '#00ff0033'},
        '1.11': {'color': 'orange', 'fill': '#ffa50033'}
    }
    
    fig2 = plt.figure(figsize=(8, 9), dpi=300)
    d2 = schemdraw.Drawing(canvas=fig2.gca())
    k2 = logic.Kmap(names='ABCD', truthtable=tt_f, groups=groups_f)
    d2.add(k2)
    
    patches2 = [
        mpatches.Patch(color='red', label="(A+B+C)", alpha=0.2),
        mpatches.Patch(color='blue', label="(A+C'+D)", alpha=0.2),
        mpatches.Patch(color='green', label="(A+B'+D')", alpha=0.2),
        mpatches.Patch(color='orange', label="(A'+C'+D')", alpha=0.2)
    ]
    plt.legend(handles=patches2, loc='upper right')
    plt.title(f"K-map f Maxterms (POS)\nf = {format_expr(reduced_pos, is_pos=True)}")
    plt.axis('off')
    d2.save('kmap_maxiterminos_f.png')
    plt.close(fig2)

if __name__ == '__main__':
    main()
