# -*- coding: utf-8 -*-
"""
Programa Principal CLI: Reductor Lógico y Síntesis de Circuitos
Punto de entrada de consola desacoplado.
Lee la función booleana desde un archivo externo (por defecto 'funcion.txt'),
simplifica por mapas de Karnaugh, genera los diagramas con compuertas de 2 entradas
y concluye el conteo de compuertas para cada circuito.
"""

import os
import shutil
import sys

from core import (
    parse_config_file,
    process_logic,
)

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def main():
    config_file = sys.argv[1] if len(sys.argv) > 1 else "funcion.txt"
    base_dir = os.path.dirname(os.path.abspath(__file__))

    print("=" * 85)
    print("      SISTEMA DE REDUCCIÓN BOOLEANA Y SÍNTESIS DE CIRCUITOS DIGITALES")
    print(f"      Archivo consultado: {config_file}")
    print("=" * 85)

    var_names, f_zeros, f_ones = parse_config_file(config_file)
    n_vars = len(var_names)

    print(f"Variables identificadas ({n_vars}): {', '.join(var_names)}")
    print(f"Salidas en 0 (Maxitérminos de f)  : {f_zeros}")
    print(f"Salidas en 1 (Minitérminos de f') : {f_ones}")

    # Ejecutar motor lógico
    tmp_out = os.path.join(base_dir, "static", "generated")
    res = process_logic(var_names, f_zeros, f_ones, out_dir=tmp_out, base_dir=base_dir, dpi=300)

    # Mostrar deducción booleana
    print("\n" + "-" * 85)
    print("1. DEDUCCIÓN ANALÍTICA BOOLEANA")
    print("-" * 85)
    print(f"\n1. Minitérminos no reducida (f'):\n   f' = {res['unreduced_sop']}")
    print(f"\n2. Maxitérminos no reducida (f):\n   f = {res['unreduced_pos']}")
    print(f"\n3. Minitérminos reducida (f' - SOP):\n   f' = {res['reduced_sop']}")
    print(f"\n4. Maxitérminos reducida (f - POS):\n   f = {res['reduced_pos']}")

    # Organizar resultados en carpetas de Resultados/
    dir_kmaps = os.path.join(base_dir, "Resultados", "01_Mapas_Karnaugh")
    dir_and_or = os.path.join(base_dir, "Resultados", "02_Diagramas_AND_OR_NOT")
    dir_nand = os.path.join(base_dir, "Resultados", "03_Diagramas_NAND")
    dir_nor = os.path.join(base_dir, "Resultados", "04_Diagramas_NOR")

    for d in [dir_kmaps, dir_and_or, dir_nand, dir_nor]:
        os.makedirs(d, exist_ok=True)

    # Copiar mapas
    for kmap_file in res["kmaps"].values():
        src = os.path.join(tmp_out, kmap_file)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(dir_kmaps, kmap_file))

    # Copiar diagramas por familia
    folder_routing = {
        "sop_and_or_not": dir_and_or,
        "pos_and_or_not": dir_and_or,
        "sop_nand": dir_nand,
        "sop_nand_reducido": dir_nand,
        "pos_nand": dir_nand,
        "pos_nand_reducido": dir_nand,
        "pos_nor": dir_nor,
        "pos_nor_reducido": dir_nor,
        "sop_nor": dir_nor,
        "sop_nor_reducido": dir_nor,
    }

    for diag_id, fname in res["diagramas"].items():
        src = os.path.join(tmp_out, fname)
        target_dir = folder_routing.get(diag_id, dir_and_or)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(target_dir, fname))

    # Conteo de compuertas
    print("\n" + "=" * 85)
    print("                     CONTEO DE COMPUERTAS POR CIRCUITO")
    print("                 (Todas las compuertas son de 2 entradas)")
    print("=" * 85)
    print(f"{'Circuito':<42} | {'NOT':<4} | {'AND':<4} | {'OR':<4} | {'NAND':<5} | {'NOR':<5} | {'TOTAL':<5}")
    print("-" * 85)
    for c in res["tabla_conteo"]:
        nombre_display = f"{c['num']}. {c['nombre']}"
        print(f"{nombre_display:<42} | {c['not']:<4} | {c['and']:<4} | {c['or']:<4} | {c['nand']:<5} | {c['nor']:<5} | {c['total']:<5}")
    print("=" * 85)
    print("\n[ÉXITO] Ejecución completada. Todos los diagramas y mapas se guardaron en 'Resultados/'.\n")


if __name__ == "__main__":
    main()
