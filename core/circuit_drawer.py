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

def render_diagram_to_file(expr_str, outlabel, title, filepath, figsize=(16, 9), dpi=180):
    """
    Renderiza una expresión lógica a imagen PNG con schemdraw.logicparse.
    Maneja constantes ('0', '1', False, True) y excepciones de sintaxis.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    try:
        if not expr_str or str(expr_str) in ['0', 'False']:
            fig, ax = plt.subplots(figsize=(8, 3), dpi=dpi)
            d = schemdraw.Drawing()
            d.add(logic.Line().right(2).label('0 (GND)', loc='left').label(outlabel, loc='right'))
            d.draw(canvas=ax, show=False)
            ax.set_title(title, fontsize=11, fontweight='bold', pad=16)
            ax.axis('off')
            plt.savefig(filepath, dpi=dpi, bbox_inches='tight')
            plt.close(fig)
            return filepath
        elif str(expr_str) in ['1', 'True']:
            fig, ax = plt.subplots(figsize=(8, 3), dpi=dpi)
            d = schemdraw.Drawing()
            d.add(logic.Line().right(2).label('1 (VCC)', loc='left').label(outlabel, loc='right'))
            d.draw(canvas=ax, show=False)
            ax.set_title(title, fontsize=11, fontweight='bold', pad=16)
            ax.axis('off')
            plt.savefig(filepath, dpi=dpi, bbox_inches='tight')
            plt.close(fig)
            return filepath

        d = logicparse(expr_str, outlabel=outlabel)
        bb = d.get_bbox()
        w = max(1.0, bb.xmax - bb.xmin)
        h = max(1.0, bb.ymax - bb.ymin)

        # Dimensiones dinámicas proporcionales para evitar compresión y asegurar legibilidad
        fig_w = max(float(figsize[0]), w * 1.35 + 3.0)
        fig_h = max(float(figsize[1]), h * 1.2 + 2.0)

        fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=max(200, dpi))
        d.draw(canvas=ax, show=False)
        ax.set_title(title, fontsize=12.5, fontweight='bold', pad=18)
        ax.axis('off')
        plt.savefig(filepath, dpi=max(200, dpi), bbox_inches='tight')
        plt.close(fig)
    except Exception as e:
        print(f"Aviso en renderizado de {filepath}: {e}")
        fig, ax = plt.subplots(figsize=(12, 5), dpi=dpi)
        ax.text(0.5, 0.5, f"{title}\n\nFunción: {outlabel} = {str(expr_str)[:100]}", 
                ha='center', va='center', fontsize=11, fontweight='bold',
                bbox=dict(boxstyle="round,pad=1", fc="#f8fafc", ec="#cbd5e1", lw=1.5))
        ax.axis('off')
        plt.savefig(filepath, dpi=dpi, bbox_inches='tight')
        plt.close(fig)
    return filepath


def generate_or_restore_all_diagrams(variables, zeros, ones, reduced_sop, reduced_pos,
                                    sop_terms, pos_clauses, out_dir, base_dir=None, dpi=180):
    """
    Genera o restaura los 10 diagramas en out_dir.
    Si coincide con la función base de 4 bits, restaura las imágenes de alta calidad de Resultados/.
    De lo contrario, genera cada uno dinámicamente.
    """
    os.makedirs(out_dir, exist_ok=True)
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    orig_map = {
        "diagrama_SOP_AND_OR_NOT.png": os.path.join(base_dir, "Resultados", "02_Diagramas_AND_OR_NOT", "diagrama_SOP_AND_OR_NOT.png"),
        "diagrama_POS_AND_OR_NOT.png": os.path.join(base_dir, "Resultados", "02_Diagramas_AND_OR_NOT", "diagrama_POS_AND_OR_NOT.png"),
        "diagrama_SOP_NAND.png": os.path.join(base_dir, "Resultados", "03_Diagramas_NAND", "diagrama_SOP_NAND.png"),
        "diagrama_SOP_NAND_reducido.png": os.path.join(base_dir, "Resultados", "03_Diagramas_NAND", "diagrama_SOP_NAND_reducido.png"),
        "diagrama_POS_NAND.png": os.path.join(base_dir, "Resultados", "03_Diagramas_NAND", "diagrama_POS_NAND.png"),
        "diagrama_POS_NAND_reducido.png": os.path.join(base_dir, "Resultados", "03_Diagramas_NAND", "diagrama_POS_NAND_reducido.png"),
        "diagrama_POS_NOR.png": os.path.join(base_dir, "Resultados", "04_Diagramas_NOR", "diagrama_POS_NOR.png"),
        "diagrama_POS_NOR_reducido.png": os.path.join(base_dir, "Resultados", "04_Diagramas_NOR", "diagrama_POS_NOR_reducido.png"),
        "diagrama_SOP_NOR.png": os.path.join(base_dir, "Resultados", "04_Diagramas_NOR", "diagrama_SOP_NOR.png"),
        "diagrama_SOP_NOR_reducido.png": os.path.join(base_dir, "Resultados", "04_Diagramas_NOR", "diagrama_SOP_NOR_reducido.png"),
    }

    if zeros == [0, 1, 2, 5, 6, 7, 11, 15] and variables == ['A', 'B', 'C', 'D']:
        for fname, src_path in orig_map.items():
            if os.path.exists(src_path):
                shutil.copy2(src_path, os.path.join(out_dir, fname))
    else:
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
                               os.path.join(out_dir, "diagrama_SOP_NAND.png"), figsize=(20, 13), dpi=dpi)

        # 4. SOP NAND Reducido
        t4 = build_tree_nand_reduced_sop(sop_terms)
        render_diagram_to_file(t4, "F'",
                               f"SOP Universal NAND Reducido (Doble Negación)\nf' = {format_sop_str(reduced_sop)}",
                               os.path.join(out_dir, "diagrama_SOP_NAND_reducido.png"), figsize=(18, 11), dpi=dpi)

        # 5. POS NAND Directo
        t5 = build_tree_nand_direct_pos(pos_clauses)
        render_diagram_to_file(t5, "F",
                               f"POS Universal NAND Directo (2 entradas)\nf = {format_pos_str(reduced_pos)}",
                               os.path.join(out_dir, "diagrama_POS_NAND.png"), figsize=(20, 13), dpi=dpi)

        # 6. POS NAND Reducido
        t6 = build_tree_nand_reduced_pos(pos_clauses)
        render_diagram_to_file(t6, "F",
                               f"POS Universal NAND Reducido (Doble Negación)\nf = {format_pos_str(reduced_pos)}",
                               os.path.join(out_dir, "diagrama_POS_NAND_reducido.png"), figsize=(18, 11), dpi=dpi)

        # 7. POS NOR Directo
        t7 = build_tree_nor_direct_pos(pos_clauses)
        render_diagram_to_file(t7, "F",
                               f"POS Universal NOR Directo (2 entradas)\nf = {format_pos_str(reduced_pos)}",
                               os.path.join(out_dir, "diagrama_POS_NOR.png"), figsize=(20, 13), dpi=dpi)

        # 8. POS NOR Reducido
        t8 = build_tree_nor_reduced_pos(pos_clauses)
        render_diagram_to_file(t8, "F",
                               f"POS Universal NOR Reducido (Doble Negación)\nf = {format_pos_str(reduced_pos)}",
                               os.path.join(out_dir, "diagrama_POS_NOR_reducido.png"), figsize=(18, 11), dpi=dpi)

        # 9. SOP NOR Directo
        t9 = build_tree_nor_direct_sop(sop_terms)
        render_diagram_to_file(t9, "F'",
                               f"SOP Universal NOR Directo (2 entradas)\nf' = {format_sop_str(reduced_sop)}",
                               os.path.join(out_dir, "diagrama_SOP_NOR.png"), figsize=(20, 13), dpi=dpi)

        # 10. SOP NOR Reducido
        t10 = build_tree_nor_reduced_sop(sop_terms)
        render_diagram_to_file(t10, "F'",
                               f"SOP Universal NOR Reducido (Doble Negación)\nf' = {format_sop_str(reduced_sop)}",
                               os.path.join(out_dir, "diagrama_SOP_NOR_reducido.png"), figsize=(18, 11), dpi=dpi)

    return DIAGRAM_FILENAMES
