# -*- coding: utf-8 -*-
"""
Motor Principal de Deducción y Síntesis Lógica (Logic Engine)
Orquesta el análisis booleano, conteo de compuertas, mapas de Karnaugh y diagramas de circuitos.
"""

import os
import sympy

from .boolean_logic import deduce_and_simplify, format_sop_str, format_pos_str
from .gate_counter import count_gates
from .kmaps import generate_kmaps
from .circuit_drawer import generate_or_restore_all_diagrams

def process_logic(variables, zeros, ones, out_dir=None, base_dir=None, dpi=180):
    """
    Ejecuta el procesamiento lógico completo:
    1. Deducción booleana analítica y simplificación (SOP y POS).
    2. Conteo de compuertas de 2 entradas para 10 familias de circuitos.
    3. Generación de mapas de Karnaugh con lazos visuales.
    4. Generación o restauración de los 10 diagramas de circuitos.
    """
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if out_dir is None:
        out_dir = os.path.join(base_dir, "static", "generated")

    os.makedirs(out_dir, exist_ok=True)

    # 1. Deducción Analítica Booleana
    deduction = deduce_and_simplify(variables, zeros, ones)
    vars_symbols = deduction["vars_symbols"]
    n_vars = len(vars_symbols)
    unreduced_sop = deduction["unreduced_sop"]
    unreduced_pos = deduction["unreduced_pos"]
    reduced_sop = deduction["reduced_sop"]
    reduced_pos = deduction["reduced_pos"]
    sop_terms = deduction["sop_terms"]
    pos_clauses = deduction["pos_clauses"]

    # 2. Conteo Analítico de Compuertas
    tabla_conteo = count_gates(variables, zeros, sop_terms, pos_clauses)

    # 3. Mapas de Karnaugh
    kmaps = generate_kmaps(
        vars_symbols=vars_symbols,
        zeros=zeros,
        ones=ones,
        reduced_sop=reduced_sop,
        reduced_pos=reduced_pos,
        out_dir=out_dir,
        dpi=dpi
    )

    # 4. Diagramas de Circuitos (10 familias)
    diagramas = generate_or_restore_all_diagrams(
        variables=variables,
        zeros=zeros,
        ones=ones,
        reduced_sop=reduced_sop,
        reduced_pos=reduced_pos,
        sop_terms=sop_terms,
        pos_clauses=pos_clauses,
        out_dir=out_dir,
        base_dir=base_dir,
        dpi=dpi
    )

    return {
        "num_bits": n_vars,
        "variables": variables,
        "zeros": zeros,
        "ones": ones,
        "unreduced_sop": format_sop_str(unreduced_sop),
        "unreduced_pos": format_pos_str(unreduced_pos),
        "reduced_sop": format_sop_str(reduced_sop),
        "reduced_pos": format_pos_str(reduced_pos),
        "is_equivalent": deduction.get("is_equivalent", True),
        "tabla_conteo": tabla_conteo,
        "kmaps": kmaps,
        "diagramas": diagramas,
    }
