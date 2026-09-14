# -*- coding: utf-8 -*-
"""
Módulo de Dibujo y Renderizado de Diagramas Lógicos
Genera o restaura los 10 diagramas de compuertas lógicas de 2 entradas usando schemdraw.
"""

import os
import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.logic as logic
from schemdraw.parsing import logicparse

from schemdraw.elements import RightLines
from schemdraw.parsing.buchheim import buchheim
from schemdraw.parsing.logic_parser import LogicTree

from .boolean_logic import format_sop_str, format_pos_str
from .circuit_trees import (
    build_tree_and_or_not,
    build_tree_nand_direct_sop,
    build_tree_nand_reduced_sop,
    build_tree_nand_direct_pos,
    build_tree_nand_reduced_pos,
    build_tree_nor_direct_pos,
    build_tree_nor_reduced_pos,
    build_tree_nor_direct_sop,
    build_tree_nor_reduced_sop,
)

DIAGRAM_FILENAMES = {
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

def draw_logic_tree(tree, gateH=1.15, gateW=2.3, outlabel=None):
    """
    Renderiza un LogicTree con compuertas ANSI/IEEE de 2 entradas.
    Soporta inversores universales puenteados ('inv_nand', 'inv_nor')
    sin duplicación de subárboles ni compresión de elementos.
    """
    drawing = schemdraw.Drawing()
    drawing.unit = gateW
    dtree = buchheim(tree)
    all_gates = ['and', 'or', 'nand', 'nor', 'not', 'inv_nand', 'inv_nor']

    def drawit(root, depth=0, outlabel=None):
        node_type = root.node
        x = root.y * -gateW
        y = -root.x * gateH
        
        if node_type in ['inv_nand', 'inv_nor']:
            elm_cls = logic.Nand if node_type == 'inv_nand' else logic.Nor
            g = elm_cls(inputs=2, d='r', at=(x, y), anchor='end', l=gateW)
            drawing.add(g)
            drawing.add(logic.Line().at(g.in1).to(g.in2))
            mid_y = (g.in1[1] + g.in2[1]) / 2.0
            mid_pt = (g.in1[0], mid_y)
            if outlabel:
                g.label(outlabel, loc='end')
            
            if root.children:
                child = root.children[0]
                if child.node in all_gates:
                    childelm = drawit(child, depth + 1)
                    drawing.add(RightLines(at=mid_pt, to=childelm.end))
                else:
                    drawing.add(logic.Line().left(0.6).at(mid_pt).label(child.node, loc='left'))
            return g
        else:
            elmdefs = {
                'and': logic.And,
                'or': logic.Or,
                'nand': logic.Nand,
                'nor': logic.Nor,
                'not': logic.Not
            }
            elm = elmdefs.get(node_type, logic.And)
            n_in = max(1, len(root.children))
            g = elm(d='r', at=(x, y), anchor='end', l=gateW, inputs=n_in)
            if outlabel:
                g.label(outlabel, loc='end')
            drawing.add(g)
            for i, child in enumerate(root.children):
                anchorname = 'start' if elm == logic.Not else f'in{i+1}'
                pt = getattr(g, anchorname)
                if child.node not in all_gates:
                    drawing.add(logic.Line().left(0.6).at(pt).label(child.node, loc='left'))
                else:
                    childelm = drawit(child, depth + 1)
                    drawing.add(RightLines(at=(g, anchorname), to=childelm.end))
            return g

    drawit(dtree, outlabel=outlabel)
    return drawing


def render_diagram_to_file(tree_or_expr, outlabel, title, filepath, figsize=(16, 9), dpi=180):
    """
    Renderiza un árbol de compuertas (LogicTree) o expresión lógica a imagen PNG con schemdraw.
    Maneja constantes ('0', '1', False, True) y cálculo dinámico de dimensiones.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    try:
        if tree_or_expr is None or str(tree_or_expr) in ['0', 'False']:
            fig, ax = plt.subplots(figsize=(8, 3), dpi=dpi)
            d = schemdraw.Drawing()
            d.add(logic.Line().right(2).label('0 (GND)', loc='left').label(outlabel, loc='right'))
            d.draw(canvas=ax, show=False)
            ax.set_title(title, fontsize=11, fontweight='bold', pad=16)
            ax.axis('off')
            plt.savefig(filepath, dpi=dpi, bbox_inches='tight')
            plt.close(fig)
            return filepath
        elif str(tree_or_expr) in ['1', 'True']:
            fig, ax = plt.subplots(figsize=(8, 3), dpi=dpi)
            d = schemdraw.Drawing()
            d.add(logic.Line().right(2).label('1 (VCC)', loc='left').label(outlabel, loc='right'))
            d.draw(canvas=ax, show=False)
            ax.set_title(title, fontsize=11, fontweight='bold', pad=16)
            ax.axis('off')
            plt.savefig(filepath, dpi=dpi, bbox_inches='tight')
            plt.close(fig)
            return filepath

        if isinstance(tree_or_expr, LogicTree):
            d = draw_logic_tree(tree_or_expr, gateH=1.15, gateW=2.3, outlabel=outlabel)
        else:
            d = logicparse(str(tree_or_expr), outlabel=outlabel)

        bb = d.get_bbox()
        w = max(1.0, bb.xmax - bb.xmin)
        h = max(1.0, bb.ymax - bb.ymin)

        # Dimensiones dinámicas proporcionales para evitar compresión y asegurar legibilidad
        fig_w = max(float(figsize[0]), w * 1.35 + 2.5)
        fig_h = max(float(figsize[1]), h * 1.15 + 2.5)

        fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=max(200, dpi))
        d.draw(canvas=ax, show=False)
        ax.set_title(title, fontsize=12.5, fontweight='bold', pad=18)
        ax.axis('off')
        plt.savefig(filepath, dpi=max(200, dpi), bbox_inches='tight')
        plt.close(fig)
    except Exception as e:
        print(f"Aviso en renderizado de {filepath}: {e}")
        fig, ax = plt.subplots(figsize=(12, 5), dpi=dpi)
        ax.text(0.5, 0.5, f"{title}\n\nFunción: {outlabel}", 
                ha='center', va='center', fontsize=11, fontweight='bold',
                bbox=dict(boxstyle="round,pad=1", fc="#f8fafc", ec="#cbd5e1", lw=1.5))
        ax.axis('off')
        plt.savefig(filepath, dpi=dpi, bbox_inches='tight')
        plt.close(fig)
    return filepath


def generate_or_restore_all_diagrams(variables, zeros, ones, reduced_sop, reduced_pos,
                                     sop_terms, pos_clauses, out_dir, base_dir=None, dpi=180):
    """
    Genera dinámicamente los 10 diagramas limpios con compuertas estrictas de 2 entradas en out_dir.
    """
    os.makedirs(out_dir, exist_ok=True)
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 1. SOP AND/OR/NOT
    t1 = build_tree_and_or_not(sop_terms, is_sop=True)
    render_diagram_to_file(t1, "F'",
                           f"Minitérminos (SOP) - NOT, AND, OR (2 entradas)\nf' = {format_sop_str(reduced_sop)}",
                           os.path.join(out_dir, "diagrama_SOP_AND_OR_NOT.png"), dpi=dpi)

    # 2. POS AND/OR/NOT
    t2 = build_tree_and_or_not(pos_clauses, is_sop=False)
    render_diagram_to_file(t2, "F",
                           f"Maxitérminos (POS) - NOT, AND, OR (2 entradas)\nf = {format_pos_str(reduced_pos)}",
                           os.path.join(out_dir, "diagrama_POS_AND_OR_NOT.png"), dpi=dpi)

    # 3. SOP NAND Directo
    t3 = build_tree_nand_direct_sop(sop_terms)
    render_diagram_to_file(t3, "F'",
                           f"SOP Universal NAND Directo (2 entradas)\nf' = {format_sop_str(reduced_sop)}",
                           os.path.join(out_dir, "diagrama_SOP_NAND.png"), figsize=(18, 10), dpi=dpi)

    # 4. SOP NAND Reducido
    t4 = build_tree_nand_reduced_sop(sop_terms)
    render_diagram_to_file(t4, "F'",
                           f"SOP Universal NAND Reducido (Doble Negación)\nf' = {format_sop_str(reduced_sop)}",
                           os.path.join(out_dir, "diagrama_SOP_NAND_reducido.png"), figsize=(16, 9), dpi=dpi)

    # 5. POS NAND Directo
    t5 = build_tree_nand_direct_pos(pos_clauses)
    render_diagram_to_file(t5, "F",
                           f"POS Universal NAND Directo (2 entradas)\nf = {format_pos_str(reduced_pos)}",
                           os.path.join(out_dir, "diagrama_POS_NAND.png"), figsize=(18, 10), dpi=dpi)

    # 6. POS NAND Reducido
    t6 = build_tree_nand_reduced_pos(pos_clauses)
    render_diagram_to_file(t6, "F",
                           f"POS Universal NAND Reducido (Doble Negación)\nf = {format_pos_str(reduced_pos)}",
                           os.path.join(out_dir, "diagrama_POS_NAND_reducido.png"), figsize=(16, 9), dpi=dpi)

    # 7. POS NOR Directo
    t7 = build_tree_nor_direct_pos(pos_clauses)
    render_diagram_to_file(t7, "F",
                           f"POS Universal NOR Directo (2 entradas)\nf = {format_pos_str(reduced_pos)}",
                           os.path.join(out_dir, "diagrama_POS_NOR.png"), figsize=(18, 10), dpi=dpi)

    # 8. POS NOR Reducido
    t8 = build_tree_nor_reduced_pos(pos_clauses)
    render_diagram_to_file(t8, "F",
                           f"POS Universal NOR Reducido (Doble Negación)\nf = {format_pos_str(reduced_pos)}",
                           os.path.join(out_dir, "diagrama_POS_NOR_reducido.png"), figsize=(16, 9), dpi=dpi)

    # 9. SOP NOR Directo
    t9 = build_tree_nor_direct_sop(sop_terms)
    render_diagram_to_file(t9, "F'",
                           f"SOP Universal NOR Directo (2 entradas)\nf' = {format_sop_str(reduced_sop)}",
                           os.path.join(out_dir, "diagrama_SOP_NOR.png"), figsize=(18, 10), dpi=dpi)

    # 10. SOP NOR Reducido
    t10 = build_tree_nor_reduced_sop(sop_terms)
    render_diagram_to_file(t10, "F'",
                           f"SOP Universal NOR Reducido (Doble Negación)\nf' = {format_sop_str(reduced_sop)}",
                           os.path.join(out_dir, "diagrama_SOP_NOR_reducido.png"), figsize=(16, 9), dpi=dpi)

    return DIAGRAM_FILENAMES
