# -*- coding: utf-8 -*-
"""
Módulo de Dibujo y Renderizado de Diagramas Lógicos
Genera o restaura los 10 diagramas de compuertas lógicas de 2 entradas usando schemdraw.
Optimizado dinámicamente para entornos de memoria reducida (Render 512MB) y alto rendimiento local.
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
from .resource_manager import get_system_profile, cleanup_memory
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
from .circuit_dag import (
    synthesize_nand_dag_sop,
    synthesize_nand_dag_pos,
)
from .dag_drawer import render_dag_to_file

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
    "sop_nand_dag": "diagrama_SOP_NAND_dag.png",
    "pos_nand_dag": "diagrama_POS_NAND_dag.png",
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


def render_diagram_to_file(tree_or_expr, outlabel, title, filepath, figsize=(16, 9), dpi=None):
    """
    Renderiza un árbol de compuertas (LogicTree) o expresión lógica a imagen PNG con schemdraw.
    Ajusta dinámicamente el lienzo y el DPI según el perfil de recursos disponible.
    """
    profile = get_system_profile()
    if dpi is None:
        dpi = profile["dpi"]

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
            cleanup_memory()
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
            cleanup_memory()
            return filepath

        if isinstance(tree_or_expr, LogicTree):
            d = draw_logic_tree(tree_or_expr, gateH=1.15, gateW=2.3, outlabel=outlabel)
        else:
            d = logicparse(str(tree_or_expr), outlabel=outlabel)

        bb = d.get_bbox()
        w = max(1.0, bb.xmax - bb.xmin)
        h = max(1.0, bb.ymax - bb.ymin)

        # Dimensiones proporcionales con límite superior según el perfil de memoria
        raw_w = max(float(figsize[0]), w * 1.35 + 2.5)
        raw_h = max(float(figsize[1]), h * 1.15 + 2.5)
        fig_w = min(profile["max_canvas_w"], raw_w)
        fig_h = min(profile["max_canvas_h"], raw_h)

        fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)
        d.draw(canvas=ax, show=False)
        ax.set_title(title, fontsize=12.5, fontweight='bold', pad=18)
        ax.axis('off')
        plt.savefig(filepath, dpi=dpi, bbox_inches='tight')
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
    finally:
        cleanup_memory()

    return filepath


def get_diagram_spec(diagram_id, reduced_sop, reduced_pos, sop_terms, pos_clauses):
    """
    Retorna la tupla de especificación (builder_fn, outlabel, title, filename, figsize)
    para un identificador de diagrama dado.
    """
    specs = {
        "sop_and_or_not": (
            lambda: build_tree_and_or_not(sop_terms, is_sop=True),
            "F",
            f"Minitérminos (SOP) - NOT, AND, OR (2 entradas)\nf = {format_sop_str(reduced_sop)}",
            "diagrama_SOP_AND_OR_NOT.png",
            (16, 9)
        ),
        "pos_and_or_not": (
            lambda: build_tree_and_or_not(pos_clauses, is_sop=False),
            "F",
            f"Maxitérminos (POS) - NOT, AND, OR (2 entradas)\nf = {format_pos_str(reduced_pos)}",
            "diagrama_POS_AND_OR_NOT.png",
            (16, 9)
        ),
        "sop_nand": (
            lambda: build_tree_nand_direct_sop(sop_terms),
            "F",
            f"SOP Universal NAND Directo (2 entradas)\nf = {format_sop_str(reduced_sop)}",
            "diagrama_SOP_NAND.png",
            (18, 10)
        ),
        "sop_nand_reducido": (
            lambda: build_tree_nand_reduced_sop(sop_terms),
            "F",
            f"SOP Universal NAND Reducido (Doble Negación)\nf = {format_sop_str(reduced_sop)}",
            "diagrama_SOP_NAND_reducido.png",
            (16, 9)
        ),
        "pos_nand": (
            lambda: build_tree_nand_direct_pos(pos_clauses),
            "F",
            f"POS Universal NAND Directo (2 entradas)\nf = {format_pos_str(reduced_pos)}",
            "diagrama_POS_NAND.png",
            (18, 10)
        ),
        "pos_nand_reducido": (
            lambda: build_tree_nand_reduced_pos(pos_clauses),
            "F",
            f"POS Universal NAND Reducido (Doble Negación)\nf = {format_pos_str(reduced_pos)}",
            "diagrama_POS_NAND_reducido.png",
            (16, 9)
        ),
        "pos_nor": (
            lambda: build_tree_nor_direct_pos(pos_clauses),
            "F",
            f"POS Universal NOR Directo (2 entradas)\nf = {format_pos_str(reduced_pos)}",
            "diagrama_POS_NOR.png",
            (18, 10)
        ),
        "pos_nor_reducido": (
            lambda: build_tree_nor_reduced_pos(pos_clauses),
            "F",
            f"POS Universal NOR Reducido (Doble Negación)\nf = {format_pos_str(reduced_pos)}",
            "diagrama_POS_NOR_reducido.png",
            (16, 9)
        ),
        "sop_nor": (
            lambda: build_tree_nor_direct_sop(sop_terms),
            "F",
            f"SOP Universal NOR Directo (2 entradas)\nf = {format_sop_str(reduced_sop)}",
            "diagrama_SOP_NOR.png",
            (18, 10)
        ),
        "sop_nor_reducido": (
            lambda: build_tree_nor_reduced_sop(sop_terms),
            "F",
            f"SOP Universal NOR Reducido (Doble Negación)\nf = {format_sop_str(reduced_sop)}",
            "diagrama_SOP_NOR_reducido.png",
            (16, 9)
        ),
        "sop_nand_dag": (
            lambda: synthesize_nand_dag_sop(sop_terms),
            "F",
            f"SOP Universal NAND Optimizado (DAG / Reutilización)\nf = {format_sop_str(reduced_sop)}",
            "diagrama_SOP_NAND_dag.png",
            (18, 9)
        ),
        "pos_nand_dag": (
            lambda: synthesize_nand_dag_pos(pos_clauses),
            "F",
            f"POS Universal NAND Optimizado (DAG / Reutilización)\nf = {format_pos_str(reduced_pos)}",
            "diagrama_POS_NAND_dag.png",
            (18, 9)
        ),
    }
    return specs.get(diagram_id)


def render_single_diagram(diagram_id, reduced_sop, reduced_pos, sop_terms, pos_clauses, out_dir, dpi=None):
    """
    Renderiza un único diagrama bajo demanda por su identificador.
    """
    spec = get_diagram_spec(diagram_id, reduced_sop, reduced_pos, sop_terms, pos_clauses)
    if not spec:
        return None

    builder_fn, outlabel, title, filename, figsize = spec
    filepath = os.path.join(out_dir, filename)

    if diagram_id in ["sop_nand_dag", "pos_nand_dag"]:
        dag = builder_fn()
        title_with_count = f"{title} | Total: {dag.count_nand_gates()} NANDs"
        render_dag_to_file(dag, title_with_count, outlabel, filepath, figsize=figsize, dpi=dpi)
    else:
        tree = builder_fn()
        render_diagram_to_file(tree, outlabel, title, filepath, figsize=figsize, dpi=dpi)

    return filename


def generate_or_restore_all_diagrams(variables, zeros, ones, reduced_sop, reduced_pos,
                                     sop_terms, pos_clauses, out_dir, base_dir=None,
                                     dpi=None, selected_diagrams=None):
    """
    Genera dinámicamente diagramas limpios con compuertas de 2 entradas en out_dir.
    Si selected_diagrams se especifica, solo se renderizan los diagramas seleccionados,
    optimizando drásticamente el uso de memoria en servidores como Render.
    """
    os.makedirs(out_dir, exist_ok=True)
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    target_ids = list(DIAGRAM_FILENAMES.keys()) if not selected_diagrams else [d for d in selected_diagrams if d in DIAGRAM_FILENAMES]

    for diag_id in target_ids:
        render_single_diagram(
            diagram_id=diag_id,
            reduced_sop=reduced_sop,
            reduced_pos=reduced_pos,
            sop_terms=sop_terms,
            pos_clauses=pos_clauses,
            out_dir=out_dir,
            dpi=dpi
        )

    return DIAGRAM_FILENAMES
