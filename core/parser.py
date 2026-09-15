# -*- coding: utf-8 -*-
"""
Módulo de Parseo de Funciones Lógicas
"""
import re
import os

DEFAULT_CONFIG = """# ==============================================================================
# CONFIGURACIÓN DE LA FUNCIÓN LÓGICA (Reductor)
# ==============================================================================
variables = A, B, C, D
f = (0, 1, 2, 5, 6, 7, 11, 15)  # salidas en 0 (Maxitérminos)
"""

def parse_function_text(text):
    variables = None
    zeros = None
    ones = None
    num_bits = None
    
    for line in text.splitlines():
        line = line.strip()
        if '#' in line: line = line.split('#')[0].strip()
        if '//' in line: line = line.split('//')[0].strip()
        if not line: continue
        
        if '=' in line or ':' in line:
            sep = '=' if '=' in line else ':'
            k, v = [p.strip() for p in line.split(sep, 1)]
            kl = k.lower()
            if kl in ['variables', 'vars', 'var']:
                variables = [x.strip().upper() for x in re.split(r'[,; ]+', v) if x.strip().isalnum()]
            elif kl in ['bits', 'num_bits', 'n_bits']:
                num_bits = int(v)
            elif kl in ['f', 'salidas_en_0', 'salidas_0', 'ceros', 'maxiterminos', 'maxterms']:
                nums = [int(x) for x in re.findall(r'\b\d+\b', v)]
                zeros = sorted(list(set(nums)))
            elif kl in ["f'", 'f_prime', 'fprime', 'salidas_en_1', 'salidas_1', 'unos', 'miniterminos', 'minterms']:
                nums = [int(x) for x in re.findall(r'\b\d+\b', v)]
                ones = sorted(list(set(nums)))
                
    max_idx = max((zeros or [0]) + (ones or [0]))
    req_bits = num_bits or (len(variables) if variables else max(2, max_idx.bit_length()))
    req_bits = min(5, max(2, req_bits))
    
    if variables is None:
        default_names = ['A', 'B', 'C', 'D', 'E']
        variables = default_names[:req_bits]
    else:
        variables = variables[:req_bits]
        req_bits = len(variables)
        
    total_states = 2 ** req_bits
    if zeros is not None:
        zeros = sorted(list(set([z for z in zeros if 0 <= z < total_states])))
    if ones is not None:
        ones = sorted(list(set([o for o in ones if 0 <= o < total_states])))

    if zeros is not None and ones is not None:
        conflict = set(zeros).intersection(set(ones))
        if conflict:
            raise ValueError(f"Conflicto lógico: los índices {sorted(list(conflict))} están definidos en 0 y en 1 simultáneamente.")
        if len(zeros) + len(ones) < total_states:
            missing = [i for i in range(total_states) if i not in zeros and i not in ones]
            zeros = sorted(zeros + missing)
    elif zeros is not None and ones is None:
        ones = sorted([i for i in range(total_states) if i not in zeros])
    elif ones is not None and zeros is None:
        zeros = sorted([i for i in range(total_states) if i not in ones])
    elif zeros is None and ones is None:
        zeros = [0, 1, 2, 5, 6, 7, 11, 15] if req_bits == 4 else [0]
        ones = sorted([i for i in range(total_states) if i not in zeros])
        
    return variables, zeros, ones

def parse_config_file(filepath="funcion.txt"):
    if not os.path.exists(filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(DEFAULT_CONFIG)
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    return parse_function_text(text)
