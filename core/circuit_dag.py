# -*- coding: utf-8 -*-
"""
Módulo de Síntesis Lógica Basada en DAG (Directed Acyclic Graph)
Implementa la optimización de compuertas NAND de 2 entradas mediante:
1. Reutilización de inversores puenteados (fan-out de literales negados).
2. Factorización de subexpresiones comunes (Common Subexpression Elimination - CSE).
3. Árboles de reducción de De Morgan optimizados.
"""

from collections import Counter
from itertools import combinations
import sympy


class DAGNode:
    """Nodo en el Grafo Acíclico Dirigido del circuito lógico."""
    def __init__(self, node_id, node_type, inputs=None, label=None):
        self.id = node_id
        self.node_type = node_type  # 'input', 'inv_nand', 'nand'
        self.inputs = inputs or []
        self.label = label or node_id
        self.layer = 0
        self.x = 0.0
        self.y = 0.0
        self.users = []

    def __repr__(self):
        return f"DAGNode({self.id}, {self.node_type}, label={self.label})"


class CircuitDAG:
    """Estructura de circuito lógico representado como DAG."""
    def __init__(self):
        self.nodes = {}
        self.output_node = None

    def add_node(self, node):
        self.nodes[node.id] = node
        for inp in node.inputs:
            if node not in inp.users:
                inp.users.append(node)
        return node

    def count_nand_gates(self):
        """Cuenta el número total de compuertas NAND de 2 entradas (incluyendo inversores puenteados)."""
        return sum(1 for n in self.nodes.values() if n.node_type in ['nand', 'inv_nand'])

    def assign_layers(self):
        """Asigna niveles topológicos a cada nodo para layout visual por capas."""
        for n in self.nodes.values():
            if n.node_type == 'input':
                n.layer = 0

        changed = True
        while changed:
            changed = False
            for n in self.nodes.values():
                if n.node_type != 'input' and n.inputs:
                    max_in_layer = max(inp.layer for inp in n.inputs)
                    new_layer = max_in_layer + 1
                    if new_layer != n.layer:
                        n.layer = new_layer
                        changed = True

        if self.output_node and self.nodes:
            max_layer = max((n.layer for n in self.nodes.values() if n != self.output_node), default=0)
            if self.output_node.layer <= max_layer:
                self.output_node.layer = max_layer + 1


def eval_dag_node(node, memo=None):
    """Evalúa simbólicamente la función booleana del DAG."""
    if memo is None:
        memo = {}
    if node.id in memo:
        return memo[node.id]

    if node.node_type == 'input':
        if node.label in ['0', 'False']:
            res = sympy.false
        elif node.label in ['1', 'True']:
            res = sympy.true
        else:
            res = sympy.Symbol(node.label)
    elif node.node_type == 'inv_nand':
        res = sympy.Not(eval_dag_node(node.inputs[0], memo))
    elif node.node_type == 'nand':
        left = eval_dag_node(node.inputs[0], memo)
        right = eval_dag_node(node.inputs[1], memo)
        res = sympy.Not(sympy.And(left, right))
    else:
        res = sympy.Symbol(node.label)

    memo[node.id] = res
    return res


def synthesize_nand_dag_sop(terms):
    """
    Sintetiza un circuito óptimo con compuertas NAND de 2 entradas para SOP (Suma de Productos)
    reutilizando inversores y pares de subproductos comunes (CSE).
    """
    if not terms or terms == [[False]]:
        dag = CircuitDAG()
        zero = DAGNode('const_0', 'input', label='0')
        dag.add_node(zero)
        dag.output_node = zero
        dag.assign_layers()
        return dag
    if terms == [[True]]:
        dag = CircuitDAG()
        one = DAGNode('const_1', 'input', label='1')
        dag.add_node(one)
        dag.output_node = one
        dag.assign_layers()
        return dag

    dag = CircuitDAG()
    node_counter = 0

    def gen_id(prefix):
        nonlocal node_counter
        node_counter += 1
        return f"{prefix}_{node_counter}"

    # 1. Variables primarias e inversores compartidos
    lit_nodes = {}
    all_lits = [lit for t in terms for lit in t]
    vars_needed = set()
    neg_vars_needed = set()
    for l in all_lits:
        if isinstance(l, sympy.Not):
            vname = str(l.args[0])
            vars_needed.add(vname)
            neg_vars_needed.add(vname)
        else:
            vars_needed.add(str(l))

    in_nodes = {}
    for v in sorted(list(vars_needed)):
        n = dag.add_node(DAGNode(f"in_{v}", "input", label=v))
        in_nodes[v] = n
        lit_nodes[v] = n

    for v in sorted(list(neg_vars_needed)):
        inv_n = dag.add_node(DAGNode(f"inv_{v}", "inv_nand", inputs=[in_nodes[v]], label=f"{v}'"))
        lit_nodes[f"~{v}"] = inv_n

    term_nodes_list = []
    for t in terms:
        t_list = [lit_nodes[str(l)] for l in t]
        term_nodes_list.append(t_list)

    # 2. Factorización de subproductos comunes (CSE)
    subexpr_cache = {}
    while True:
        pair_counts = Counter()
        for t_list in term_nodes_list:
            if len(t_list) >= 2:
                ids = sorted([n.id for n in t_list])
                for p in combinations(ids, 2):
                    pair_counts[p] += 1

        most_common = pair_counts.most_common(1)
        if not most_common or most_common[0][1] < 2:
            break

        best_pair_ids, cnt = most_common[0]
        u_node = dag.nodes[best_pair_ids[0]]
        v_node = dag.nodes[best_pair_ids[1]]
        pair_key = (best_pair_ids[0], best_pair_ids[1])

        if pair_key not in subexpr_cache:
            nand_p = dag.add_node(DAGNode(gen_id("sub_nand"), "nand", inputs=[u_node, v_node], label=f"({u_node.label}·{v_node.label})'"))
            and_p = dag.add_node(DAGNode(gen_id("sub_and"), "inv_nand", inputs=[nand_p], label=f"{u_node.label}·{v_node.label}"))
            subexpr_cache[pair_key] = and_p

        shared_node = subexpr_cache[pair_key]

        new_term_nodes_list = []
        for t_list in term_nodes_list:
            t_ids = [n.id for n in t_list]
            if best_pair_ids[0] in t_ids and best_pair_ids[1] in t_ids:
                remaining = [n for n in t_list if n.id not in best_pair_ids]
                remaining.append(shared_node)
                new_term_nodes_list.append(remaining)
            else:
                new_term_nodes_list.append(t_list)
        term_nodes_list = new_term_nodes_list

    # 3. Ensamblado de términos (cada término genera T_i negado, listo para De Morgan)
    term_outputs = []
    for t_list in term_nodes_list:
        if len(t_list) == 1:
            u = t_list[0]
            if u.node_type == 'inv_nand':
                term_outputs.append(u.inputs[0])
            else:
                inv_u = dag.add_node(DAGNode(gen_id("term_inv"), "inv_nand", inputs=[u], label=f"{u.label}'"))
                term_outputs.append(inv_u)
        elif len(t_list) == 2:
            n = dag.add_node(DAGNode(gen_id("term_nand"), "nand", inputs=[t_list[0], t_list[1]], label=f"({t_list[0].label}·{t_list[1].label})'"))
            term_outputs.append(n)
        else:
            cur = dag.add_node(DAGNode(gen_id("term_nand"), "nand", inputs=[t_list[0], t_list[1]]))
            for extra in t_list[2:]:
                cur_and = dag.add_node(DAGNode(gen_id("and_step"), "inv_nand", inputs=[cur]))
                cur = dag.add_node(DAGNode(gen_id("term_nand"), "nand", inputs=[cur_and, extra]))
            term_outputs.append(cur)

    # 4. Árbol de Suma OR con compuertas NAND (De Morgan)
    def build_or_tree(items):
        if len(items) == 1:
            return items[0], True
        mid = len(items) // 2
        left_node, left_is_neg = build_or_tree(items[:mid])
        right_node, right_is_neg = build_or_tree(items[mid:])

        left_in = left_node if left_is_neg else dag.add_node(DAGNode(gen_id("or_inv"), "inv_nand", inputs=[left_node]))
        right_in = right_node if right_is_neg else dag.add_node(DAGNode(gen_id("or_inv"), "inv_nand", inputs=[right_node]))
        out_nand = dag.add_node(DAGNode(gen_id("or_nand"), "nand", inputs=[left_in, right_in]))
        return out_nand, False

    if len(term_outputs) == 1:
        out_root = dag.add_node(DAGNode(gen_id("out_inv"), "inv_nand", inputs=[term_outputs[0]], label="F"))
    else:
        root_node, is_neg = build_or_tree(term_outputs)
        out_root = root_node
        out_root.label = "F"

    dag.output_node = out_root
    dag.assign_layers()
    return dag


def synthesize_nand_dag_pos(clauses):
    """
    Sintetiza un circuito óptimo con compuertas NAND de 2 entradas para POS (Producto de Sumas)
    reutilizando inversores y pares de sub-sumas comunes (CSE).
    """
    if not clauses or clauses == [[False]]:
        dag = CircuitDAG()
        zero = DAGNode('const_0', 'input', label='0')
        dag.add_node(zero)
        dag.output_node = zero
        dag.assign_layers()
        return dag
    if clauses == [[True]]:
        dag = CircuitDAG()
        one = DAGNode('const_1', 'input', label='1')
        dag.add_node(one)
        dag.output_node = one
        dag.assign_layers()
        return dag

    dag = CircuitDAG()
    node_counter = 0

    def gen_id(prefix):
        nonlocal node_counter
        node_counter += 1
        return f"{prefix}_{node_counter}"

    # 1. Variables primarias e inversores compartidos
    all_lits = [lit for c in clauses for lit in c]
    vars_needed = set()
    neg_vars_needed = set()
    for l in all_lits:
        if isinstance(l, sympy.Not):
            vname = str(l.args[0])
            vars_needed.add(vname)
            neg_vars_needed.add(vname)
        else:
            vars_needed.add(str(l))

    in_nodes = {}
    for v in sorted(list(vars_needed)):
        in_nodes[v] = dag.add_node(DAGNode(f"in_{v}", "input", label=v))

    inv_nodes = {}
    for v in sorted(list(neg_vars_needed)):
        inv_nodes[v] = dag.add_node(DAGNode(f"inv_{v}", "inv_nand", inputs=[in_nodes[v]], label=f"{v}'"))

    def get_neg_lit_node(lit):
        """Para compuertas NAND, una suma (A + B) es NAND(A', B'). Devuelve el nodo negado."""
        if isinstance(lit, sympy.Not):
            vname = str(lit.args[0])
            return in_nodes[vname]  # (A')' = A
        else:
            vname = str(lit)
            if vname in inv_nodes:
                return inv_nodes[vname]
            inv_n = dag.add_node(DAGNode(f"inv_{vname}", "inv_nand", inputs=[in_nodes[vname]], label=f"{vname}'"))
            inv_nodes[vname] = inv_n
            return inv_n

    clause_nodes_list = []
    for c in clauses:
        c_list = [get_neg_lit_node(l) for l in c]
        clause_nodes_list.append(c_list)

    # 2. Factorización de sub-sumas comunes: NAND(u, v) = u' + v'
    subsum_cache = {}
    while True:
        pair_counts = Counter()
        for c_list in clause_nodes_list:
            if len(c_list) >= 2:
                ids = sorted([n.id for n in c_list])
                for p in combinations(ids, 2):
                    pair_counts[p] += 1
        most_common = pair_counts.most_common(1)
        if not most_common or most_common[0][1] < 2:
            break

        best_pair_ids, cnt = most_common[0]
        u_node = dag.nodes[best_pair_ids[0]]
        v_node = dag.nodes[best_pair_ids[1]]
        pair_key = (best_pair_ids[0], best_pair_ids[1])

        if pair_key not in subsum_cache:
            sum_node = dag.add_node(DAGNode(gen_id("sub_or"), "nand", inputs=[u_node, v_node], label=f"({u_node.label}'+{v_node.label}')"))
            inv_sum = dag.add_node(DAGNode(gen_id("inv_sub_or"), "inv_nand", inputs=[sum_node]))
            subsum_cache[pair_key] = (sum_node, inv_sum)

        sum_node, inv_sum = subsum_cache[pair_key]

        new_clause_nodes_list = []
        for c_list in clause_nodes_list:
            c_ids = [n.id for n in c_list]
            if best_pair_ids[0] in c_ids and best_pair_ids[1] in c_ids:
                remaining = [n for n in c_list if n.id not in best_pair_ids]
                remaining.append(inv_sum)
                new_clause_nodes_list.append(remaining)
            else:
                new_clause_nodes_list.append(c_list)
        clause_nodes_list = new_clause_nodes_list

    # 3. Ensamblado de cláusulas (cada cláusula genera C_i positivo)
    clause_outputs = []
    for c_idx, c_list in enumerate(clause_nodes_list):
        orig_c = clauses[c_idx]
        if len(c_list) == 1:
            l = orig_c[0]
            if isinstance(l, sympy.Not):
                vname = str(l.args[0])
                clause_outputs.append(inv_nodes[vname])
            else:
                vname = str(l)
                clause_outputs.append(in_nodes[vname])
        elif len(c_list) == 2:
            n = dag.add_node(DAGNode(gen_id("cl_nand"), "nand", inputs=[c_list[0], c_list[1]], label=f"C{c_idx+1}"))
            clause_outputs.append(n)
        else:
            cur = dag.add_node(DAGNode(gen_id("cl_nand"), "nand", inputs=[c_list[0], c_list[1]]))
            for extra in c_list[2:]:
                cur_inv = dag.add_node(DAGNode(gen_id("cl_step_inv"), "inv_nand", inputs=[cur]))
                cur = dag.add_node(DAGNode(gen_id("cl_nand"), "nand", inputs=[cur_inv, extra]))
            clause_outputs.append(cur)

    # 4. Árbol de Producto AND con compuertas NAND
    def build_and_tree(items):
        if len(items) == 1:
            return items[0]
        mid = len(items) // 2
        left_node = build_and_tree(items[:mid])
        right_node = build_and_tree(items[mid:])
        nand_gate = dag.add_node(DAGNode(gen_id("and_nand"), "nand", inputs=[left_node, right_node]))
        and_gate = dag.add_node(DAGNode(gen_id("and_inv"), "inv_nand", inputs=[nand_gate]))
        return and_gate

    out_root = build_and_tree(clause_outputs)
    out_root.label = "F"
    dag.output_node = out_root
    dag.assign_layers()
    return dag
