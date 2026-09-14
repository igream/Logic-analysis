import sys
import subprocess

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

for pkg in ['sympy', 'schemdraw', 'matplotlib']:
    try:
        __import__(pkg)
    except ImportError:
        print(f'[*] Instalando {pkg}...')
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg])

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import schemdraw
from schemdraw.logic import kmap

maxterminos = {0, 1, 2, 5, 6, 7, 11, 15}
truthtable = [(f'{i:04b}', '0' if i in maxterminos else '1') for i in range(16)]

# -------------------------------------------------------------
# 1. MAPA DE KARNAUGH PARA MAXITERMINOS (Agrupando ceros - POS)
# -------------------------------------------------------------
groups_pos = {
    '000.': {'color': '#D32F2F', 'fill': '#FFCDD266', 'lw': 2.5},  # M0, M1   -> (A + B + C)
    '0.10': {'color': '#1976D2', 'fill': '#BBDEFB66', 'lw': 2.5},  # M2, M6   -> (A + C' + D)
    '01.1': {'color': '#388E3C', 'fill': '#C8E6C966', 'lw': 2.5},  # M5, M7   -> (A + B' + D')
    '1.11': {'color': '#E65100', 'fill': '#FFE0B266', 'lw': 2.5},  # M11, M15 -> (A' + C' + D')
}

fig, ax = plt.subplots(figsize=(8, 9), dpi=300)
d1 = schemdraw.Drawing()
k1 = kmap.Kmap(names='ABCD', truthtable=truthtable, groups=groups_pos)
d1.add(k1)
d1.draw(show=False, canvas=ax)
ax.axis('off')
ax.set_aspect('equal')

legend_patches_pos = [
    mpatches.Patch(facecolor='#FFCDD2', edgecolor='#D32F2F', label="Grupo {M0, M1} : (A + B + C)"),
    mpatches.Patch(facecolor='#BBDEFB', edgecolor='#1976D2', label="Grupo {M2, M6} : (A + C' + D)"),
    mpatches.Patch(facecolor='#C8E6C9', edgecolor='#388E3C', label="Grupo {M5, M7} : (A + B' + D')"),
    mpatches.Patch(facecolor='#FFE0B2', edgecolor='#E65100', label="Grupo {M11, M15} : (A' + C' + D')"),
]
ax.legend(handles=legend_patches_pos, loc='upper center', bbox_to_anchor=(0.5, -0.05),
          fontsize=10.5, frameon=True, fancybox=True, shadow=True, title="Lazos de Maxitérminos (Ceros)")

ax.set_title("Mapa de Karnaugh - Reducción por Maxitérminos (POS)\nF = (A + B + C)(A + C' + D)(A + B' + D')(A' + C' + D')",
             fontsize=13, fontweight='bold', color='#B71C1C', pad=25)

plt.savefig('kmap_maxiterminos_pos.png', bbox_inches='tight', dpi=300)
plt.close(fig)
print("[OK] 'kmap_maxiterminos_pos.png' generado.")

# -------------------------------------------------------------
# 2. MAPA DE KARNAUGH PARA MINITERMINOS (Agrupando unos - SOP)
# -------------------------------------------------------------
groups_sop = {
    '1.0.': {'color': '#1976D2', 'fill': '#BBDEFB66', 'lw': 2.5},  # m8, m9, m12, m13 -> AC'
    '1..0': {'color': '#7B1FA2', 'fill': '#E1BEE766', 'lw': 2.5},  # m8, m10, m12, m14 -> AD'
    '.100': {'color': '#388E3C', 'fill': '#C8E6C966', 'lw': 2.5},  # m4, m12          -> BC'D'
    '0011': {'color': '#D32F2F', 'fill': '#FFCDD266', 'lw': 2.5},  # m3               -> A'B'CD
}

fig, ax = plt.subplots(figsize=(8, 9), dpi=300)
d2 = schemdraw.Drawing()
k2 = kmap.Kmap(names='ABCD', truthtable=truthtable, groups=groups_sop)
d2.add(k2)
d2.draw(show=False, canvas=ax)
ax.axis('off')
ax.set_aspect('equal')

legend_patches_sop = [
    mpatches.Patch(facecolor='#BBDEFB', edgecolor='#1976D2', label="Grupo {m8, m9, m12, m13} : AC'"),
    mpatches.Patch(facecolor='#E1BEE7', edgecolor='#7B1FA2', label="Grupo {m8, m10, m12, m14} : AD'"),
    mpatches.Patch(facecolor='#C8E6C9', edgecolor='#388E3C', label="Grupo {m4, m12} : BC'D'"),
    mpatches.Patch(facecolor='#FFCDD2', edgecolor='#D32F2F', label="Grupo {m3} : A'B'CD"),
]
ax.legend(handles=legend_patches_sop, loc='upper center', bbox_to_anchor=(0.5, -0.05),
          fontsize=10.5, frameon=True, fancybox=True, shadow=True, title="Lazos de Minitérminos (Unos)")

ax.set_title("Mapa de Karnaugh - Reducción por Minitérminos (SOP)\nF = AC' + AD' + BC'D' + A'B'CD",
             fontsize=13, fontweight='bold', color='#0D47A1', pad=25)

plt.savefig('kmap_miniterminos_sop.png', bbox_inches='tight', dpi=300)
plt.close(fig)
print("[OK] 'kmap_miniterminos_sop.png' generado.")

# -------------------------------------------------------------
# 3. IMAGEN COMPARATIVA LADO A LADO
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8.5), dpi=300)

d_comp1 = schemdraw.Drawing()
k_comp1 = kmap.Kmap(names='ABCD', truthtable=truthtable, groups=groups_pos)
d_comp1.add(k_comp1)
d_comp1.draw(show=False, canvas=ax1)
ax1.axis('off')
ax1.set_aspect('equal')
ax1.set_title("1. Reducción por Maxitérminos (POS)\nF = (A + B + C)(A + C' + D)(A + B' + D')(A' + C' + D')",
              fontsize=11.5, pad=20, color='#B71C1C', fontweight='bold')
ax1.legend(handles=legend_patches_pos, loc='upper center', bbox_to_anchor=(0.5, -0.05),
           fontsize=9.5, frameon=True, fancybox=True, shadow=True)

d_comp2 = schemdraw.Drawing()
k_comp2 = kmap.Kmap(names='ABCD', truthtable=truthtable, groups=groups_sop)
d_comp2.add(k_comp2)
d_comp2.draw(show=False, canvas=ax2)
ax2.axis('off')
ax2.set_aspect('equal')
ax2.set_title("2. Reducción por Minitérminos (SOP)\nF = AC' + AD' + BC'D' + A'B'CD",
              fontsize=11.5, pad=20, color='#0D47A1', fontweight='bold')
ax2.legend(handles=legend_patches_sop, loc='upper center', bbox_to_anchor=(0.5, -0.05),
           fontsize=9.5, frameon=True, fancybox=True, shadow=True)

fig.suptitle("Comparativa de Reducción en Mapa de Karnaugh (4 Variables)", fontsize=16, fontweight='bold', y=0.98)
plt.subplots_adjust(top=0.85, bottom=0.15, wspace=0.3)
plt.savefig('kmap_comparacion.png', bbox_inches='tight', dpi=300)
plt.close(fig)
print("[OK] 'kmap_comparacion.png' generado.")
