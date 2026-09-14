# -*- coding: utf-8 -*-
"""
Módulo de Mapas de Karnaugh (K-Maps)
Genera mapas de Karnaugh resueltos visualmente con lazos y colores para 2, 3, 4 y 5 variables.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import schemdraw
import schemdraw.logic as logic
import sympy

from .boolean_logic import format_sop_str, format_pos_str
from .resource_manager import get_system_profile, cleanup_memory

def term_to_pattern(term, vars_list, is_sop=True):
    """
    Convierte un término/cláusula de SymPy a un patrón binario con '.' para schemdraw Kmap.
    Ej: A & ~B & D -> '10.1'
    """
    sub_cls = sympy.And if is_sop else sympy.Or
    lits = list(term.args) if isinstance(term, sub_cls) else [term]
    lit_map = {}
    for l in lits:
        if isinstance(l, sympy.Not):
            lit_map[str(l.args[0])] = '0' if is_sop else '1'
        else:
            lit_map[str(l)] = '1' if is_sop else '0'
    return ''.join(lit_map.get(str(v), '.') for v in vars_list)


def generate_kmaps(vars_symbols, zeros, ones, reduced_sop, reduced_pos, out_dir, dpi=None):
    """
    Genera los mapas de Karnaugh para minitérminos (f) y maxitérminos (f) en out_dir.
    Retorna un diccionario con los nombres de archivos generados.
    """
    profile = get_system_profile()
    if dpi is None:
        dpi = profile["dpi"]
    os.makedirs(out_dir, exist_ok=True)
    n_vars = len(vars_symbols)
    kmaps = {}

    colors = ['#D32F2F', '#1976D2', '#388E3C', '#E65100', '#7B1FA2', '#0097A7', '#C2185B', '#FBC02D']
    fills = ['#FFCDD266', '#BBDEFB66', '#C8E6C966', '#FFE0B266', '#E1BEE766', '#B2EBF266', '#F8BBD066', '#FFF9C466']

    sop_terms = reduced_sop.args if isinstance(reduced_sop, sympy.Or) else [reduced_sop]
    pos_clauses = reduced_pos.args if isinstance(reduced_pos, sympy.And) else [reduced_pos]

    if n_vars in [2, 3, 4]:
        var_str = ''.join(str(v) for v in vars_symbols)

        # 1. K-map f (Minitérminos - SOP)
        tt_sop = [(f"{i:0{n_vars}b}", '1' if i in ones else '0') for i in range(2**n_vars)]
        groups_sop = {}
        patches_sop = []
        for idx, term in enumerate(sop_terms):
            pat = term_to_pattern(term, vars_symbols, is_sop=True)
            c = colors[idx % len(colors)]
            f = fills[idx % len(fills)]
            groups_sop[pat] = {'color': c, 'fill': f, 'lw': 2.5}
            patches_sop.append(mpatches.Patch(facecolor=f[:7], edgecolor=c, label=f"{format_sop_str(term)}"))

        fig1, ax1 = plt.subplots(figsize=(7.5, 8.5), dpi=dpi)
        d1 = schemdraw.Drawing()
        k1 = logic.Kmap(names=var_str, truthtable=tt_sop, groups=groups_sop)
        d1.add(k1)
        d1.draw(show=False, canvas=ax1)
        ax1.axis('off')
        ax1.set_aspect('equal')
        ax1.legend(handles=patches_sop, loc='upper center', bbox_to_anchor=(0.5, -0.05),
                   fontsize=9.5, frameon=True, fancybox=True, title="Lazos de Minitérminos (Unos)")
        ax1.set_title(f"Mapa de Karnaugh Resuelto - Minitérminos (SOP)\nf = {format_sop_str(reduced_sop)}",
                      fontsize=12, fontweight='bold', color='#0D47A1', pad=20)
        plt.savefig(os.path.join(out_dir, 'kmap_miniterminos.png'), bbox_inches='tight', dpi=dpi)
        plt.close(fig1)
        cleanup_memory()
        kmaps['miniterminos'] = 'kmap_miniterminos.png'

        # 2. K-map f (Maxitérminos)
        tt_f = [(f"{i:0{n_vars}b}", '0' if i in zeros else '1') for i in range(2**n_vars)]
        groups_f = {}
        patches_f = []
        for idx, clause in enumerate(pos_clauses):
            pat = term_to_pattern(clause, vars_symbols, is_sop=False)
            c = colors[idx % len(colors)]
            f = fills[idx % len(fills)]
            groups_f[pat] = {'color': c, 'fill': f, 'lw': 2.5}
            patches_f.append(mpatches.Patch(facecolor=f[:7], edgecolor=c, label=f"{format_pos_str(clause)}"))

        fig2, ax2 = plt.subplots(figsize=(7.5, 8.5), dpi=dpi)
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
        plt.savefig(os.path.join(out_dir, 'kmap_maxiterminos.png'), bbox_inches='tight', dpi=dpi)
        plt.close(fig2)
        cleanup_memory()
        kmaps['maxiterminos'] = 'kmap_maxiterminos.png'

    elif n_vars == 5:
        var_names = [str(v) for v in vars_symbols]
        sub_names = ''.join(var_names[1:])
        
        # Sub-mapas Minitérminos f (SOP)
        fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7.5), dpi=dpi)
        tt1 = [(f"{i:04b}", '1' if i in ones else '0') for i in range(16)]
        d1 = schemdraw.Drawing()
        d1.add(logic.Kmap(names=sub_names, truthtable=tt1))
        d1.draw(show=False, canvas=ax1)
        ax1.axis('off')
        ax1.set_title(f'Sub-mapa {var_names[0]} = 0', fontsize=12, fontweight='bold')

        tt2 = [(f"{i:04b}", '1' if (i + 16) in ones else '0') for i in range(16)]
        d2 = schemdraw.Drawing()
        d2.add(logic.Kmap(names=sub_names, truthtable=tt2))
        d2.draw(show=False, canvas=ax2)
        ax2.axis('off')
        ax2.set_title(f'Sub-mapa {var_names[0]} = 1', fontsize=12, fontweight='bold')

        plt.suptitle(f"Mapa de Karnaugh de 5 Variables - Minitérminos (SOP)\nf = {format_sop_str(reduced_sop)}",
                     fontsize=13, fontweight='bold', color='#0D47A1')
        plt.savefig(os.path.join(out_dir, 'kmap_miniterminos.png'), bbox_inches='tight', dpi=dpi)
        plt.close(fig1)
        cleanup_memory()
        kmaps['miniterminos'] = 'kmap_miniterminos.png'

        # Sub-mapas Maxitérminos f
        fig2, (ax3, ax4) = plt.subplots(1, 2, figsize=(14, 7.5), dpi=dpi)
        tt3 = [(f"{i:04b}", '0' if i in zeros else '1') for i in range(16)]
        d3 = schemdraw.Drawing()
        d3.add(logic.Kmap(names=sub_names, truthtable=tt3))
        d3.draw(show=False, canvas=ax3)
        ax3.axis('off')
        ax3.set_title(f'Sub-mapa {var_names[0]} = 0', fontsize=12, fontweight='bold')

        tt4 = [(f"{i:04b}", '0' if (i + 16) in zeros else '1') for i in range(16)]
        d4 = schemdraw.Drawing()
        d4.add(logic.Kmap(names=sub_names, truthtable=tt4))
        d4.draw(show=False, canvas=ax4)
        ax4.axis('off')
        ax4.set_title(f'Sub-mapa {var_names[0]} = 1', fontsize=12, fontweight='bold')

        plt.suptitle(f"Mapa de Karnaugh de 5 Variables - Maxitérminos (f)\nf = {format_pos_str(reduced_pos)}",
                     fontsize=13, fontweight='bold', color='#B71C1C')
        plt.savefig(os.path.join(out_dir, 'kmap_maxiterminos.png'), bbox_inches='tight', dpi=dpi)
        plt.close(fig2)
        cleanup_memory()
        kmaps['maxiterminos'] = 'kmap_maxiterminos.png'

    return kmaps
