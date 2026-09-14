# -*- coding: utf-8 -*-
"""
Paquete Core del Reductor Lógico y Síntesis de Circuitos.
"""

from .engine import process_logic
from .parser import parse_function_text, parse_config_file, DEFAULT_CONFIG
from .boolean_logic import deduce_and_simplify, format_sop_str, format_pos_str
from .gate_counter import count_gates
from .kmaps import generate_kmaps
from .circuit_drawer import generate_or_restore_all_diagrams, render_single_diagram, DIAGRAM_FILENAMES
from .resource_manager import get_system_profile, cleanup_memory

__all__ = [
    "process_logic",
    "parse_function_text",
    "parse_config_file",
    "DEFAULT_CONFIG",
    "deduce_and_simplify",
    "format_sop_str",
    "format_pos_str",
    "count_gates",
    "generate_kmaps",
    "generate_or_restore_all_diagrams",
    "render_single_diagram",
    "DIAGRAM_FILENAMES",
    "get_system_profile",
    "cleanup_memory",
]
