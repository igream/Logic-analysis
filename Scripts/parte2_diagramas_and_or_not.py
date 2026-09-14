import sys
if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

import matplotlib.pyplot as plt
from schemdraw.parsing import logicparse
import os

# Set working directory to the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Diagram 1: SOP f' with AND/OR/NOT
expr_sop = "(((not A) and ((not B) and (not C))) or ((not A) and (C and (not D)))) or (((not A) and (B and D)) or (A and (C and D)))"
d1 = logicparse(expr_sop, outlabel="F'")
fig1, ax1 = plt.subplots(figsize=(14, 8))
d1.draw(show=False, canvas=ax1)
ax1.set_title("Expresión reducida de minitérminos (SOP) - AND/OR/NOT\nF' = A'B'C' + A'CD' + A'BD + ACD\nCompuertas: 4 NOT + 8 AND + 3 OR = 15 total", pad=20)
plt.savefig("diagrama_SOP_AND_OR_NOT.png", dpi=300, bbox_inches='tight')
plt.close(fig1)

# Diagram 2: POS f with AND/OR/NOT
expr_pos = "((A or (B or C)) and (A or ((not C) or D))) and ((A or ((not B) or (not D))) and ((not A) or ((not C) or (not D))))"
d2 = logicparse(expr_pos, outlabel='F')
fig2, ax2 = plt.subplots(figsize=(14, 8))
d2.draw(show=False, canvas=ax2)
ax2.set_title("Expresión reducida de maxitérminos (POS) - AND/OR/NOT\nF = (A+B+C)(A+C'+D)(A+B'+D')(A'+C'+D')\nCompuertas: 4 NOT + 8 OR + 3 AND = 15 total", pad=20)
plt.savefig("diagrama_POS_AND_OR_NOT.png", dpi=300, bbox_inches='tight')
plt.close(fig2)
