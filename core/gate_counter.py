# -*- coding: utf-8 -*-
"""
Módulo de Conteo de Compuertas Lógicas (2 entradas)
Calcula el número exacto de compuertas requeridas para cada una de las 10 familias
inspeccionando directamente la topología sintética de los árboles de compuertas.
"""

from .circuit_trees import (
    build_tree_and_or_not,
    build_tree_nand_direct_sop,
    build_tree_nand_reduced_sop,
    build_tree_nand_direct_pos,
    build_tree_nand_reduced_pos,
    build_tree_nor_direct_pos,
    build_tree_nor_reduced_pos,
    build_tree_nor_direct_sop,
    build_tree_nor_reduced_sop
)
from .circuit_dag import (
    synthesize_nand_dag_sop,
    synthesize_nand_dag_pos
)

def _count_tree_gates(node):
    counts = {"not": 0, "and": 0, "or": 0, "nand": 0, "nor": 0}
    if node is None:
        return counts
    def walk(n):
        if not hasattr(n, "node") or not n.node:
            return
        op = str(n.node).lower()
        if op == "not":
            counts["not"] += 1
        elif op == "and":
            counts["and"] += 1
        elif op == "or":
            counts["or"] += 1
        elif op in ["nand", "inv_nand"]:
            counts["nand"] += 1
        elif op in ["nor", "inv_nor"]:
            counts["nor"] += 1
        for child in getattr(n, "children", []):
            walk(child)
    walk(node)
    counts["total"] = sum(counts.values())
    return counts

def count_gates(variables, zeros, sop_terms, pos_clauses):
    """
    Calcula la tabla de conteo de compuertas de 2 entradas para las 10 familias de circuitos,
    garantizando concordancia del 100% con los esquemáticos generados.
    """
    c1 = _count_tree_gates(build_tree_and_or_not(sop_terms, is_sop=True))
    c2 = _count_tree_gates(build_tree_and_or_not(pos_clauses, is_sop=False))
    c3 = _count_tree_gates(build_tree_nand_direct_sop(sop_terms))
    c4 = _count_tree_gates(build_tree_nand_reduced_sop(sop_terms))
    c5 = _count_tree_gates(build_tree_nand_direct_pos(pos_clauses))
    c6 = _count_tree_gates(build_tree_nand_reduced_pos(pos_clauses))
    c7 = _count_tree_gates(build_tree_nor_direct_pos(pos_clauses))
    c8 = _count_tree_gates(build_tree_nor_reduced_pos(pos_clauses))
    c9 = _count_tree_gates(build_tree_nor_direct_sop(sop_terms))
    c10 = _count_tree_gates(build_tree_nor_reduced_sop(sop_terms))
    c11_nand = synthesize_nand_dag_sop(sop_terms).count_nand_gates()
    c12_nand = synthesize_nand_dag_pos(pos_clauses).count_nand_gates()

    tabla_conteo = [
        {"num": 1, "id": "sop_and_or_not", "nombre": "SOP Minitérminos (f)", "tipo": "AND / OR / NOT", "not": c1["not"], "and": c1["and"], "or": c1["or"], "nand": 0, "nor": 0, "total": c1["total"], "archivo": "diagrama_SOP_AND_OR_NOT.png"},
        {"num": 2, "id": "pos_and_or_not", "nombre": "POS Maxitérminos (f)", "tipo": "AND / OR / NOT", "not": c2["not"], "and": c2["and"], "or": c2["or"], "nand": 0, "nor": 0, "total": c2["total"], "archivo": "diagrama_POS_AND_OR_NOT.png"},
        {"num": 3, "id": "sop_nand", "nombre": "SOP Universal NAND (f)", "tipo": "NAND Directo", "not": 0, "and": 0, "or": 0, "nand": c3["nand"], "nor": 0, "total": c3["total"], "archivo": "diagrama_SOP_NAND.png"},
        {"num": 4, "id": "sop_nand_reducido", "nombre": "SOP Universal NAND Reducido (f)", "tipo": "NAND Doble Negación", "not": 0, "and": 0, "or": 0, "nand": c4["nand"], "nor": 0, "total": c4["total"], "archivo": "diagrama_SOP_NAND_reducido.png"},
        {"num": 5, "id": "pos_nand", "nombre": "POS Universal NAND (f)", "tipo": "NAND Directo", "not": 0, "and": 0, "or": 0, "nand": c5["nand"], "nor": 0, "total": c5["total"], "archivo": "diagrama_POS_NAND.png"},
        {"num": 6, "id": "pos_nand_reducido", "nombre": "POS Universal NAND Reducido (f)", "tipo": "NAND Doble Negación", "not": 0, "and": 0, "or": 0, "nand": c6["nand"], "nor": 0, "total": c6["total"], "archivo": "diagrama_POS_NAND_reducido.png"},
        {"num": 7, "id": "pos_nor", "nombre": "POS Universal NOR (f)", "tipo": "NOR Directo", "not": 0, "and": 0, "or": 0, "nand": 0, "nor": c7["nor"], "total": c7["total"], "archivo": "diagrama_POS_NOR.png"},
        {"num": 8, "id": "pos_nor_reducido", "nombre": "POS Universal NOR Reducido (f)", "tipo": "NOR Doble Negación", "not": 0, "and": 0, "or": 0, "nand": 0, "nor": c8["nor"], "total": c8["total"], "archivo": "diagrama_POS_NOR_reducido.png"},
        {"num": 9, "id": "sop_nor", "nombre": "SOP Universal NOR (f)", "tipo": "NOR Directo", "not": 0, "and": 0, "or": 0, "nand": 0, "nor": c9["nor"], "total": c9["total"], "archivo": "diagrama_SOP_NOR.png"},
        {"num": 10, "id": "sop_nor_reducido", "nombre": "SOP Universal NOR Reducido (f)", "tipo": "NOR Doble Negación", "not": 0, "and": 0, "or": 0, "nand": 0, "nor": c10["nor"], "total": c10["total"], "archivo": "diagrama_SOP_NOR_reducido.png"},
        {"num": 11, "id": "sop_nand_dag", "nombre": "SOP Universal NAND Optimizado (f)", "tipo": "NAND Reutilización (DAG/CSE)", "not": 0, "and": 0, "or": 0, "nand": c11_nand, "nor": 0, "total": c11_nand, "archivo": "diagrama_SOP_NAND_dag.png"},
        {"num": 12, "id": "pos_nand_dag", "nombre": "POS Universal NAND Optimizado (f)", "tipo": "NAND Reutilización (DAG/CSE)", "not": 0, "and": 0, "or": 0, "nand": c12_nand, "nor": 0, "total": c12_nand, "archivo": "diagrama_POS_NAND_dag.png"},
    ]
    return tabla_conteo
