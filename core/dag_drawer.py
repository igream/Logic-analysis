# -*- coding: utf-8 -*-
"""
Módulo de Renderizado de Circuitos DAG con Compuertas NAND y Reutilización
Genera esquemáticos profesionales con:
- Distribución topológica por capas (X) y ordenamiento libre de colisiones (Y).
- Enrutamiento ortogonal tipo Bus Vertical para señales compartidas (fan-out >= 2).
- Puntos de derivación y bifurcación explícitos (elm.Dot).
- Conexiones ortogonales limpias para señales individuales (fan-out = 1).
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.logic as logic
import schemdraw.elements as elm

from .resource_manager import get_system_profile, cleanup_memory


def render_dag_to_file(dag, title, outlabel, filepath, figsize=(18, 9), dpi=None):
    """
    Renderiza un CircuitDAG a imagen PNG usando schemdraw y matplotlib.
    Garantiza un cableado ortogonal limpio sin superposición de líneas ni cruce sobre compuertas.
    """
    profile = get_system_profile()
    if dpi is None:
        dpi = profile["dpi"]

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # Casos constantes triviales (0 o 1)
    if not dag.nodes or (dag.output_node and dag.output_node.label in ['0', '1', 'False', 'True']):
        fig, ax = plt.subplots(figsize=(8, 3), dpi=dpi)
        d = schemdraw.Drawing()
        lbl_const = dag.output_node.label if dag.output_node else '0'
        vcc_gnd = '1 (VCC)' if lbl_const in ['1', 'True'] else '0 (GND)'
        d.add(logic.Line().right(2).label(vcc_gnd, loc='left').label(outlabel, loc='right'))
        d.draw(canvas=ax, show=False)
        ax.set_title(title, fontsize=11, fontweight='bold', pad=16)
        ax.axis('off')
        plt.savefig(filepath, dpi=dpi, bbox_inches='tight')
        plt.close(fig)
        cleanup_memory()
        return filepath

    # 1. Agrupar nodos por capa topológica
    layers = {}
    for n in dag.nodes.values():
        layers.setdefault(n.layer, []).append(n)

    # 2. Asignación de coordenadas espaciales
    x_gap = 5.0
    for l_idx in sorted(layers.keys()):
        nodes = layers[l_idx]
        if l_idx > 0:
            def sort_key(node):
                if not node.inputs:
                    return 0.0
                return sum(inp.y for inp in node.inputs) / len(node.inputs)
            nodes.sort(key=sort_key, reverse=True)

        y_pitch = 2.8
        total_h = (len(nodes) - 1) * y_pitch
        for i, n in enumerate(nodes):
            n.x = l_idx * x_gap
            n.y = (total_h / 2.0) - (i * y_pitch)

    d = schemdraw.Drawing()
    gate_elements = {}
    pin_inputs = {}

    # 3. Dibujar compuertas y terminales de entrada
    for n in dag.nodes.values():
        if n.node_type == 'input':
            d.add(logic.Line().right(0.6).at((n.x - 0.6, n.y)).label(n.label, loc='left'))
            gate_elements[n.id] = (n.x, n.y)
        elif n.node_type == 'inv_nand':
            g = logic.Nand(inputs=2, d='r', at=(n.x, n.y), anchor='end', l=1.6)
            d.add(g)
            d.add(logic.Line().at(g.in1).to(g.in2))
            mid_y = (g.in1[1] + g.in2[1]) / 2.0
            pin_inputs[n.id] = [(g.in1[0], mid_y)]
            gate_elements[n.id] = g.end
        elif n.node_type == 'nand':
            g = logic.Nand(inputs=2, d='r', at=(n.x, n.y), anchor='end', l=1.6)
            d.add(g)
            pin_inputs[n.id] = [g.in1, g.in2]
            gate_elements[n.id] = g.end

    # 4. Línea de salida hacia el label F
    if dag.output_node and dag.output_node.id in gate_elements:
        out_pt = gate_elements[dag.output_node.id]
        d.add(logic.Line().right(1.0).at(out_pt).label(outlabel, loc='right'))

    # 4. Agrupar consumidores por nodo fuente
    consumers_by_src = {}
    for n in dag.nodes.values():
        if not n.inputs:
            continue
        pins = pin_inputs[n.id]
        for idx, inp_node in enumerate(n.inputs):
            target_pin = pins[idx] if idx < len(pins) else pins[-1]
            consumers_by_src.setdefault(inp_node.id, []).append((n, target_pin))

    # 5. Enrutamiento ortogonal con buses para señales compartidas
    layer_buses = {}
    for src_id, targets in consumers_by_src.items():
        src_node = dag.nodes[src_id]
        src_pt = gate_elements[src_id]

        if len(targets) == 1:
            tgt_node, tgt_pin = targets[0]
            mid_x = (src_pt[0] + tgt_pin[0]) / 2.0
            d.add(logic.Line().at(src_pt).to((mid_x, src_pt[1])))
            d.add(logic.Line().at((mid_x, src_pt[1])).to((mid_x, tgt_pin[1])))
            d.add(logic.Line().at((mid_x, tgt_pin[1])).to(tgt_pin))
        else:
            bus_slot = layer_buses.get(src_node.layer, 0) + 1
            layer_buses[src_node.layer] = bus_slot
            bus_x = src_pt[0] + 0.45 + (bus_slot * 0.40)

            all_ys = [src_pt[1]] + [tgt_pin[1] for _, tgt_pin in targets]
            y_min = min(all_ys)
            y_max = max(all_ys)

            d.add(logic.Line().at(src_pt).to((bus_x, src_pt[1])))
            d.add(elm.Dot().at((bus_x, src_pt[1])))
            d.add(logic.Line().at((bus_x, y_min)).to((bus_x, y_max)))

            for tgt_node, tgt_pin in targets:
                d.add(elm.Dot().at((bus_x, tgt_pin[1])))
                d.add(logic.Line().at((bus_x, tgt_pin[1])).to(tgt_pin))

    # 6. Dimensionamiento dinámico del canvas y guardado
    try:
        bb = d.get_bbox()
        w = max(1.0, bb.xmax - bb.xmin)
        h = max(1.0, bb.ymax - bb.ymin)
        raw_w = max(float(figsize[0]), w * 1.25 + 2.5)
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
        print(f"Aviso en renderizado de DAG {filepath}: {e}")
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
