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
from schemdraw.elements import RightLines
import sympy

from .resource_manager import get_system_profile, cleanup_memory


def _render_structured_circuit(terms, is_sop, title, outlabel, filepath, figsize=(18, 9), dpi=150, profile=None):
    """
    Renderizador universal de esquemáticos estructurados por niveles y renglones:
    - Entradas primarias e inversores limpios en la columna izquierda.
    - Bus vertical de distribución para literales (V y V').
    - Términos/cláusulas en renglones horizontales independientes con espaciado constante.
    - Árbol de reducción binario simétrico convergente a la salida F.
    - Cableado 100% ortogonal sin cruces sobre compuertas lógicas.
    """
    d = schemdraw.Drawing()

    # 1. Variables e inversores necesarios
    all_lits = [lit for t in terms for lit in t]
    vars_needed = sorted(list(set(str(l.args[0]) if isinstance(l, sympy.Not) else str(l) for l in all_lits)))
    neg_vars_needed = sorted(list(set(str(l.args[0]) for l in all_lits if isinstance(l, sympy.Not))))

    if not is_sop:
        vars_needed = []
        neg_vars_needed = []
        for t in terms:
            if len(t) == 1:
                l = t[0]
                if isinstance(l, sympy.Not):
                    vname = str(l.args[0])
                    vars_needed.append(vname)
                    neg_vars_needed.append(vname)
                else:
                    vars_needed.append(str(l))
            else:
                for l in t:
                    if isinstance(l, sympy.Not):
                        vars_needed.append(str(l.args[0]))
                    else:
                        vname = str(l)
                        vars_needed.append(vname)
                        neg_vars_needed.append(vname)
        vars_needed = sorted(list(set(vars_needed)))
        neg_vars_needed = sorted(list(set(neg_vars_needed)))

    num_terms = len(terms)
    term_pitch = 3.6
    total_term_h = max(0, (num_terms - 1) * term_pitch)
    term_ys = [(total_term_h / 2.0) - (i * term_pitch) for i in range(num_terms)]

    num_vars = len(vars_needed)
    in_pitch = 2.8
    total_in_h = max(0, (num_vars - 1) * in_pitch)
    var_ys = {v: (total_in_h / 2.0) - (i * in_pitch) for i, v in enumerate(vars_needed)}

    # Coordenadas X de etapas
    x_input_labels = 0.0
    x_inverters = 2.2
    x_bus_start = 4.8
    rail_gap = 0.5

    rails = {}
    curr_x = x_bus_start
    for v in vars_needed:
        rails[v] = curr_x
        curr_x += rail_gap
        if v in neg_vars_needed:
            rails[f"{v}'"] = curr_x
            curr_x += rail_gap
    x_bus_end = curr_x

    max_lits = max((len(t) for t in terms), default=1)
    cascade_extra = max(0, max_lits - 2) * 3.6
    x_terms_start = x_bus_end + 1.2
    x_term_out = x_terms_start + 1.6 + cascade_extra

    # Límites verticales del bus
    all_known_ys = term_ys + list(var_ys.values())
    rail_top = max(all_known_ys) + 1.2
    rail_bot = min(all_known_ys) - 1.2

    # 2. Dibujar Entradas e Inversores en columna izquierda
    for v in vars_needed:
        vy = var_ys[v]
        d.add(logic.Line().right(0.6).at((x_input_labels, vy)).label(v, loc='left'))
        pt_in = (x_input_labels + 0.6, vy)

        rx_v = rails[v]
        d.add(logic.Line().at(pt_in).to((rx_v, vy)))
        d.add(elm.Dot().at((rx_v, vy)))

        if v in neg_vars_needed:
            rx_neg = rails[f"{v}'"]
            inv_y = vy - 0.8
            d.add(elm.Dot().at(pt_in))

            inv_g = logic.Nand(inputs=2, d='r', at=(x_inverters + 1.2, inv_y), anchor='end', l=1.2)
            d.add(inv_g)
            d.add(logic.Line().at(inv_g.in1).to(inv_g.in2))
            mid_in_y = (inv_g.in1[1] + inv_g.in2[1]) / 2.0

            # Entrada al inversor con ángulo recto
            d.add(logic.Line().at(pt_in).to((x_inverters, vy)))
            d.add(logic.Line().at((x_inverters, vy)).to((x_inverters, mid_in_y)))
            d.add(logic.Line().at((x_inverters, mid_in_y)).to((inv_g.in1[0], mid_in_y)))

            # Salida del inversor al riel V'
            d.add(logic.Line().at(inv_g.end).to((rx_neg, inv_y)))
            d.add(elm.Dot().at((rx_neg, inv_y)))

    # Líneas verticales del bus de literales
    for r_lbl, rx in rails.items():
        d.add(logic.Line().at((rx, rail_bot)).to((rx, rail_top)))
        d.add(elm.Label().at((rx, rail_top + 0.35)).label(r_lbl, loc='center', fontsize=9))

    # 3. Dibujar Términos / Cláusulas en renglones horizontales
    term_out_pins = []

    for i, t in enumerate(terms):
        ty = term_ys[i]
        if is_sop:
            lits = [f"{l.args[0]}'" if isinstance(l, sympy.Not) else str(l) for l in t]
        else:
            if len(t) == 1:
                # En cláusula POS unitaria (L), la señal no pasa por NAND; se conecta directamente L
                l = t[0]
                lits = [f"{l.args[0]}'" if isinstance(l, sympy.Not) else str(l)]
            else:
                # Cláusula de >=2 literales: cada literal entra invertido a NAND: (A + B) = NAND(A', B')
                lits = []
                for l in t:
                    if isinstance(l, sympy.Not):
                        lits.append(str(l.args[0]))
                    else:
                        lits.append(f"{str(l)}'")

        if len(lits) == 1:
            lit_name = lits[0]
            rx = rails[lit_name]
            if is_sop and num_terms > 1:
                # En SOP para conectar al árbol OR de De Morgan, cada término debe entrar negado (T_i')
                # Si el término es un literal simple L, L' = NAND(L, L)
                inv = logic.Nand(inputs=2, d='r', at=(x_term_out, ty), anchor='end', l=1.2)
                d.add(inv)
                d.add(logic.Line().at(inv.in1).to(inv.in2))
                my = (inv.in1[1] + inv.in2[1]) / 2.0
                d.add(logic.Line().at((rx, my)).to((inv.in1[0], my)))
                d.add(elm.Dot().at((rx, my)))
                term_out_pins.append((inv.end, ty))
            else:
                d.add(logic.Line().at((rx, ty)).to((x_term_out, ty)))
                d.add(elm.Dot().at((rx, ty)))
                term_out_pins.append(((x_term_out, ty), ty))
        elif len(lits) == 2:
            g = logic.Nand(inputs=2, d='r', at=(x_term_out, ty), anchor='end', l=1.4)
            d.add(g)

            rx0 = rails[lits[0]]
            d.add(logic.Line().at((rx0, g.in1[1])).to(g.in1))
            d.add(elm.Dot().at((rx0, g.in1[1])))

            rx1 = rails[lits[1]]
            d.add(logic.Line().at((rx1, g.in2[1])).to(g.in2))
            d.add(elm.Dot().at((rx1, g.in2[1])))

            term_out_pins.append((g.end, ty))
        else:
            # Cascada para 3 o más literales a lo largo del renglón
            curr_x = x_terms_start
            g1 = logic.Nand(inputs=2, d='r', at=(curr_x + 1.4, ty), anchor='end', l=1.4)
            d.add(g1)
            rx0 = rails[lits[0]]
            d.add(logic.Line().at((rx0, g1.in1[1])).to(g1.in1))
            d.add(elm.Dot().at((rx0, g1.in1[1])))
            rx1 = rails[lits[1]]
            d.add(logic.Line().at((rx1, g1.in2[1])).to(g1.in2))
            d.add(elm.Dot().at((rx1, g1.in2[1])))

            curr_out = g1.end
            curr_x += 1.4

            for lit_idx in range(2, len(lits)):
                extra_lit = lits[lit_idx]
                is_last = (lit_idx == len(lits) - 1)

                inv_x = curr_x + 1.6
                inv = logic.Nand(inputs=2, d='r', at=(inv_x, ty), anchor='end', l=1.1)
                d.add(inv)
                d.add(logic.Line().at(inv.in1).to(inv.in2))
                my = (inv.in1[1] + inv.in2[1]) / 2.0
                d.add(logic.Line().at(curr_out).to((inv.in1[0], my)))

                next_nand_x = x_term_out if is_last else (inv_x + 2.0)
                gn = logic.Nand(inputs=2, d='r', at=(next_nand_x, ty), anchor='end', l=1.4)
                d.add(gn)

                mid_wire_x = (inv.end[0] + gn.in1[0]) / 2.0
                d.add(logic.Line().at(inv.end).to((mid_wire_x, ty)))
                d.add(logic.Line().at((mid_wire_x, ty)).to((mid_wire_x, gn.in1[1])))
                d.add(logic.Line().at((mid_wire_x, gn.in1[1])).to(gn.in1))

                rx_extra = rails[extra_lit]
                d.add(logic.Line().at((rx_extra, gn.in2[1])).to(gn.in2))
                d.add(elm.Dot().at((rx_extra, gn.in2[1])))

                curr_out = gn.end
                curr_x = next_nand_x

            term_out_pins.append((curr_out, ty))

    # 4. Árbol de Reducción Simétrico Balanceado
    curr_level_pins = term_out_pins
    tree_stage_x = x_term_out + 2.6

    if num_terms == 1 and is_sop and len(terms[0]) > 1:
        # Término único SOP de >=2 literales produce T_1'. Necesita un inversor para obtener F = T_1
        p, y = curr_level_pins[0]
        inv_f = logic.Nand(inputs=2, d='r', at=(tree_stage_x, y), anchor='end', l=1.2)
        d.add(inv_f)
        d.add(logic.Line().at(inv_f.in1).to(inv_f.in2))
        my = (inv_f.in1[1] + inv_f.in2[1]) / 2.0
        d.add(logic.Line().at(p).to((inv_f.in1[0], my)))
        curr_level_pins = [(inv_f.end, y)]

    while len(curr_level_pins) > 1:
        next_level_pins = []
        for i in range(0, len(curr_level_pins), 2):
            if i + 1 < len(curr_level_pins):
                p1, y1 = curr_level_pins[i]
                p2, y2 = curr_level_pins[i + 1]
                mid_y = (y1 + y2) / 2.0

                g_tree = logic.Nand(inputs=2, d='r', at=(tree_stage_x, mid_y), anchor='end', l=1.4)
                d.add(g_tree)

                d.add(RightLines(at=p1, to=g_tree.in1))
                d.add(RightLines(at=p2, to=g_tree.in2))

                if is_sop:
                    if len(curr_level_pins) > 2:
                        inv_tree = logic.Nand(inputs=2, d='r', at=(tree_stage_x + 1.8, mid_y), anchor='end', l=1.1)
                        d.add(inv_tree)
                        d.add(logic.Line().at(inv_tree.in1).to(inv_tree.in2))
                        my = (inv_tree.in1[1] + inv_tree.in2[1]) / 2.0
                        d.add(logic.Line().at(g_tree.end).to((inv_tree.in1[0], my)))
                        next_level_pins.append((inv_tree.end, mid_y))
                    else:
                        next_level_pins.append((g_tree.end, mid_y))
                else:
                    inv_tree = logic.Nand(inputs=2, d='r', at=(tree_stage_x + 1.8, mid_y), anchor='end', l=1.1)
                    d.add(inv_tree)
                    d.add(logic.Line().at(inv_tree.in1).to(inv_tree.in2))
                    my = (inv_tree.in1[1] + inv_tree.in2[1]) / 2.0
                    d.add(logic.Line().at(g_tree.end).to((inv_tree.in1[0], my)))
                    next_level_pins.append((inv_tree.end, mid_y))
            else:
                p, y = curr_level_pins[i]
                next_level_pins.append((p, y))

        curr_level_pins = next_level_pins
        tree_stage_x += 3.6

    final_pin, final_y = curr_level_pins[0]
    d.add(logic.Line().right(1.2).at(final_pin).label(outlabel, loc='right'))

    # Dimensionamiento dinámico del canvas y guardado
    bb = d.get_bbox()
    w = max(1.0, bb.xmax - bb.xmin)
    h = max(1.0, bb.ymax - bb.ymin)
    raw_w = max(float(figsize[0]), w * 1.15 + 2.0)
    raw_h = max(float(figsize[1]), h * 1.10 + 2.0)
    max_w = profile["max_canvas_w"] if profile else 32
    max_h = profile["max_canvas_h"] if profile else 20
    fig_w = min(max_w, raw_w)
    fig_h = min(max_h, raw_h)

    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)
    d.draw(canvas=ax, show=False)
    ax.set_title(title, fontsize=12.5, fontweight='bold', pad=18)
    ax.axis('off')
    plt.savefig(filepath, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    return filepath


def render_dag_to_file(dag, title, outlabel, filepath, figsize=(18, 9), dpi=None):
    """
    Renderiza un CircuitDAG a imagen PNG usando schemdraw y matplotlib.
    Utiliza el motor estructurado por niveles y renglones cuando se dispone de la información
    de términos o cláusulas, garantizando cero cruces sobre compuertas y orden visual riguroso.
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

    # Caso estructurado prioritario
    terms = getattr(dag, 'terms', None)
    if terms is not None:
        try:
            is_sop = getattr(dag, 'is_sop', True)
            _render_structured_circuit(terms, is_sop, title, outlabel, filepath,
                                      figsize=figsize, dpi=dpi, profile=profile)
            return filepath
        except Exception as e:
            print(f"Aviso: Renderizado estructurado falló ({e}), usando fallback topológico.")
        finally:
            cleanup_memory()

    # Fallback: Distribución topológica general por capas
    try:
        layers = {}
        for n in dag.nodes.values():
            layers.setdefault(n.layer, []).append(n)

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

        if dag.output_node and dag.output_node.id in gate_elements:
            out_pt = gate_elements[dag.output_node.id]
            d.add(logic.Line().right(1.0).at(out_pt).label(outlabel, loc='right'))

        consumers_by_src = {}
        for n in dag.nodes.values():
            if not n.inputs:
                continue
            pins = pin_inputs[n.id]
            for idx, inp_node in enumerate(n.inputs):
                target_pin = pins[idx] if idx < len(pins) else pins[-1]
                consumers_by_src.setdefault(inp_node.id, []).append((n, target_pin))

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
