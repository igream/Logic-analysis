import sys
import schemdraw
import schemdraw.logic as logic
import matplotlib.pyplot as plt

if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

def draw_nand_as_not(d, x, y, in_label):
    gate = d.add(logic.Nand(inputs=2).at((x, y)))
    d.add(logic.Wire('c').at(gate.in1).to((x-1, y+0.25)))
    d.add(logic.Wire('c').at(gate.in2).to((x-1, y-0.25)))
    d.add(logic.Line().at((x-1, y)).to((x-1.5, y)).label(in_label, loc='left'))
    d.add(logic.Line().at((x-1, y+0.25)).to((x-1, y-0.25)))
    return gate

def draw_nand(d, x, y, in1=None, in2=None, label1=None, label2=None):
    gate = d.add(logic.Nand(inputs=2).at((x, y)))
    if in1 is not None:
        d.add(logic.Wire('c').at(gate.in1).to(in1.out))
    elif label1 is not None:
        d.add(logic.Line().left(0.5).at(gate.in1).label(label1, loc='left'))
        
    if in2 is not None:
        d.add(logic.Wire('c').at(gate.in2).to(in2.out))
    elif label2 is not None:
        d.add(logic.Line().left(0.5).at(gate.in2).label(label2, loc='left'))
        
    return gate

def save_drawing(d, filename, title):
    d.config(fontsize=12)
    fig, ax = plt.subplots(figsize=(18, 11), dpi=200)
    d.draw(canvas=ax, show=False)
    ax.set_title(title, pad=20, fontsize=14, fontweight='bold')
    ax.axis('off')
    plt.savefig(filename, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f"[OK] {filename} generado.")

# ----------------- Diagram 1: SOP NAND Universal -----------------
d1 = schemdraw.Drawing()
N1 = draw_nand_as_not(d1, 2, 14, 'A')
N2 = draw_nand_as_not(d1, 2, 12, 'B')
N3 = draw_nand_as_not(d1, 2, 10, 'C')
N4 = draw_nand_as_not(d1, 2, 8, 'D')

# P1 = A'B'C'
G5 = draw_nand(d1, 6, 13, label1="B'", label2="C'")
G6 = draw_nand(d1, 9, 13)
d1.add(logic.Wire('c').at(G6.in1).to(G5.out))
d1.add(logic.Wire('c').at(G6.in2).to(G5.out))
G7 = draw_nand(d1, 12, 12, in2=G6, label1="A'")
G8 = draw_nand(d1, 15, 12)
d1.add(logic.Wire('c').at(G8.in1).to(G7.out))
d1.add(logic.Wire('c').at(G8.in2).to(G7.out))

# P2 = A'CD'
G9 = draw_nand(d1, 6, 9, label1="A'", label2="C")
G10 = draw_nand(d1, 9, 9)
d1.add(logic.Wire('c').at(G10.in1).to(G9.out))
d1.add(logic.Wire('c').at(G10.in2).to(G9.out))
G11 = draw_nand(d1, 12, 8, in1=G10, label2="D'")
G12 = draw_nand(d1, 15, 8)
d1.add(logic.Wire('c').at(G12.in1).to(G11.out))
d1.add(logic.Wire('c').at(G12.in2).to(G11.out))

# P3 = A'BD
G13 = draw_nand(d1, 6, 5, label1="A'", label2="B")
G14 = draw_nand(d1, 9, 5)
d1.add(logic.Wire('c').at(G14.in1).to(G13.out))
d1.add(logic.Wire('c').at(G14.in2).to(G13.out))
G15 = draw_nand(d1, 12, 4, in1=G14, label2="D")
G16 = draw_nand(d1, 15, 4)
d1.add(logic.Wire('c').at(G16.in1).to(G15.out))
d1.add(logic.Wire('c').at(G16.in2).to(G15.out))

# P4 = ACD
G17 = draw_nand(d1, 6, 1, label1="A", label2="C")
G18 = draw_nand(d1, 9, 1)
d1.add(logic.Wire('c').at(G18.in1).to(G17.out))
d1.add(logic.Wire('c').at(G18.in2).to(G17.out))
G19 = draw_nand(d1, 12, 0, in1=G18, label2="D")
G20 = draw_nand(d1, 15, 0)
d1.add(logic.Wire('c').at(G20.in1).to(G19.out))
d1.add(logic.Wire('c').at(G20.in2).to(G19.out))

# OR Layer
G21 = draw_nand(d1, 18, 12)
d1.add(logic.Wire('c').at(G21.in1).to(G8.out))
d1.add(logic.Wire('c').at(G21.in2).to(G8.out))
G22 = draw_nand(d1, 18, 8)
d1.add(logic.Wire('c').at(G22.in1).to(G12.out))
d1.add(logic.Wire('c').at(G22.in2).to(G12.out))
G23 = draw_nand(d1, 21, 10, in1=G21, in2=G22)

G24 = draw_nand(d1, 18, 4)
d1.add(logic.Wire('c').at(G24.in1).to(G16.out))
d1.add(logic.Wire('c').at(G24.in2).to(G16.out))
G25 = draw_nand(d1, 18, 0)
d1.add(logic.Wire('c').at(G25.in1).to(G20.out))
d1.add(logic.Wire('c').at(G25.in2).to(G20.out))
G26 = draw_nand(d1, 21, 2, in1=G24, in2=G25)

G27 = draw_nand(d1, 24, 10)
d1.add(logic.Wire('c').at(G27.in1).to(G23.out))
d1.add(logic.Wire('c').at(G27.in2).to(G23.out))
G28 = draw_nand(d1, 24, 2)
d1.add(logic.Wire('c').at(G28.in1).to(G26.out))
d1.add(logic.Wire('c').at(G28.in2).to(G26.out))
G29 = draw_nand(d1, 27, 6, in1=G27, in2=G28)
d1.add(logic.Line().right(0.5).at(G29.out).label("F'", loc='right'))

save_drawing(d1, 'diagrama_SOP_NAND.png', 'SOP NAND Universal - 29 compuertas NAND')


# ----------------- Diagram 2: SOP NAND Reduced -----------------
d2 = schemdraw.Drawing()
N1 = draw_nand_as_not(d2, 2, 14, 'A')
N2 = draw_nand_as_not(d2, 2, 12, 'B')
N3 = draw_nand_as_not(d2, 2, 10, 'C')
N4 = draw_nand_as_not(d2, 2, 8, 'D')

G5 = draw_nand(d2, 6, 13, label1="B'", label2="C'")
G6 = draw_nand(d2, 9, 13)
d2.add(logic.Wire('c').at(G6.in1).to(G5.out))
d2.add(logic.Wire('c').at(G6.in2).to(G5.out))
G7 = draw_nand(d2, 12, 12, in2=G6, label1="A'")

G9 = draw_nand(d2, 6, 9, label1="A'", label2="C")
G10 = draw_nand(d2, 9, 9)
d2.add(logic.Wire('c').at(G10.in1).to(G9.out))
d2.add(logic.Wire('c').at(G10.in2).to(G9.out))
G11 = draw_nand(d2, 12, 8, in1=G10, label2="D'")

G13 = draw_nand(d2, 6, 5, label1="A'", label2="B")
G14 = draw_nand(d2, 9, 5)
d2.add(logic.Wire('c').at(G14.in1).to(G13.out))
d2.add(logic.Wire('c').at(G14.in2).to(G13.out))
G15 = draw_nand(d2, 12, 4, in1=G14, label2="D")

G17 = draw_nand(d2, 6, 1, label1="A", label2="C")
G18 = draw_nand(d2, 9, 1)
d2.add(logic.Wire('c').at(G18.in1).to(G17.out))
d2.add(logic.Wire('c').at(G18.in2).to(G17.out))
G19 = draw_nand(d2, 12, 0, in1=G18, label2="D")

G23 = draw_nand(d2, 18, 10, in1=G7, in2=G11)
G26 = draw_nand(d2, 18, 2, in1=G15, in2=G19)

G27 = draw_nand(d2, 21, 10)
d2.add(logic.Wire('c').at(G27.in1).to(G23.out))
d2.add(logic.Wire('c').at(G27.in2).to(G23.out))
G28 = draw_nand(d2, 21, 2)
d2.add(logic.Wire('c').at(G28.in1).to(G26.out))
d2.add(logic.Wire('c').at(G28.in2).to(G26.out))
G29 = draw_nand(d2, 24, 6, in1=G27, in2=G28)
d2.add(logic.Line().right(0.5).at(G29.out).label("F'", loc='right'))

save_drawing(d2, 'diagrama_SOP_NAND_reducido.png', 'SOP NAND Reducido (Doble Negación) - 21 compuertas NAND')


# ----------------- Diagram 3: POS NAND Universal -----------------
d3 = schemdraw.Drawing()
N1 = draw_nand_as_not(d3, 2, 14, 'A')
N2 = draw_nand_as_not(d3, 2, 12, 'B')
N3 = draw_nand_as_not(d3, 2, 10, 'C')
N4 = draw_nand_as_not(d3, 2, 8, 'D')

# S1
G5 = draw_nand_as_not(d3, 6, 14, 'B')
G6 = draw_nand_as_not(d3, 6, 12, 'C')
G7 = draw_nand(d3, 9, 13, in1=G5, in2=G6)
G8 = draw_nand_as_not(d3, 12, 14, 'A')
G9 = draw_nand(d3, 12, 12)
d3.add(logic.Wire('c').at(G9.in1).to(G7.out))
d3.add(logic.Wire('c').at(G9.in2).to(G7.out))
G10 = draw_nand(d3, 15, 13, in1=G8, in2=G9)

# S2
G11 = draw_nand_as_not(d3, 6, 10, "C'")
G12 = draw_nand_as_not(d3, 6, 8, 'D')
G13 = draw_nand(d3, 9, 9, in1=G11, in2=G12)
G14 = draw_nand_as_not(d3, 12, 10, 'A')
G15 = draw_nand(d3, 12, 8)
d3.add(logic.Wire('c').at(G15.in1).to(G13.out))
d3.add(logic.Wire('c').at(G15.in2).to(G13.out))
G16 = draw_nand(d3, 15, 9, in1=G14, in2=G15)

# S3
G17 = draw_nand_as_not(d3, 6, 6, "B'")
G18 = draw_nand_as_not(d3, 6, 4, "D'")
G19 = draw_nand(d3, 9, 5, in1=G17, in2=G18)
G20 = draw_nand_as_not(d3, 12, 6, 'A')
G21 = draw_nand(d3, 12, 4)
d3.add(logic.Wire('c').at(G21.in1).to(G19.out))
d3.add(logic.Wire('c').at(G21.in2).to(G19.out))
G22 = draw_nand(d3, 15, 5, in1=G20, in2=G21)

# S4
G23 = draw_nand_as_not(d3, 6, 2, "C'")
G24 = draw_nand_as_not(d3, 6, 0, "D'")
G25 = draw_nand(d3, 9, 1, in1=G23, in2=G24)
G26 = draw_nand_as_not(d3, 12, 2, "A'")
G27 = draw_nand(d3, 12, 0)
d3.add(logic.Wire('c').at(G27.in1).to(G25.out))
d3.add(logic.Wire('c').at(G27.in2).to(G25.out))
G28 = draw_nand(d3, 15, 1, in1=G26, in2=G27)

# AND Tree
G29 = draw_nand(d3, 18, 11, in1=G10, in2=G16)
G30 = draw_nand(d3, 21, 11)
d3.add(logic.Wire('c').at(G30.in1).to(G29.out))
d3.add(logic.Wire('c').at(G30.in2).to(G29.out))

G31 = draw_nand(d3, 18, 3, in1=G22, in2=G28)
G32 = draw_nand(d3, 21, 3)
d3.add(logic.Wire('c').at(G32.in1).to(G31.out))
d3.add(logic.Wire('c').at(G32.in2).to(G31.out))

G33 = draw_nand(d3, 24, 7, in1=G30, in2=G32)
G34 = draw_nand(d3, 27, 7)
d3.add(logic.Wire('c').at(G34.in1).to(G33.out))
d3.add(logic.Wire('c').at(G34.in2).to(G33.out))
d3.add(logic.Line().right(0.5).at(G34.out).label('F', loc='right'))

save_drawing(d3, 'diagrama_POS_NAND.png', 'POS NAND Universal - 34 compuertas NAND')


# ----------------- Diagram 4: POS NAND Reduced -----------------
d4 = schemdraw.Drawing()
N1 = draw_nand_as_not(d4, 2, 14, 'A')
N2 = draw_nand_as_not(d4, 2, 12, 'B')
N3 = draw_nand_as_not(d4, 2, 10, 'C')
N4 = draw_nand_as_not(d4, 2, 8, 'D')

# S1
t1 = draw_nand(d4, 9, 13, label1="B'", label2="C'")
t1_not = draw_nand(d4, 12, 12)
d4.add(logic.Wire('c').at(t1_not.in1).to(t1.out))
d4.add(logic.Wire('c').at(t1_not.in2).to(t1.out))
S1 = draw_nand(d4, 15, 13, label1="A'", in2=t1_not)

# S2
t2 = draw_nand(d4, 9, 9, label1="C", label2="D'")
t2_not = draw_nand(d4, 12, 8)
d4.add(logic.Wire('c').at(t2_not.in1).to(t2.out))
d4.add(logic.Wire('c').at(t2_not.in2).to(t2.out))
S2 = draw_nand(d4, 15, 9, label1="A'", in2=t2_not)

# S3
t3 = draw_nand(d4, 9, 5, label1="B", label2="D")
t3_not = draw_nand(d4, 12, 4)
d4.add(logic.Wire('c').at(t3_not.in1).to(t3.out))
d4.add(logic.Wire('c').at(t3_not.in2).to(t3.out))
S3 = draw_nand(d4, 15, 5, label1="A'", in2=t3_not)

# S4
t4 = draw_nand(d4, 9, 1, label1="C", label2="D")
t4_not = draw_nand(d4, 12, 0)
d4.add(logic.Wire('c').at(t4_not.in1).to(t4.out))
d4.add(logic.Wire('c').at(t4_not.in2).to(t4.out))
S4 = draw_nand(d4, 15, 1, label1="A", in2=t4_not)

# AND Tree
G29 = draw_nand(d4, 18, 11, in1=S1, in2=S2)
G30 = draw_nand(d4, 21, 11)
d4.add(logic.Wire('c').at(G30.in1).to(G29.out))
d4.add(logic.Wire('c').at(G30.in2).to(G29.out))

G31 = draw_nand(d4, 18, 3, in1=S3, in2=S4)
G32 = draw_nand(d4, 21, 3)
d4.add(logic.Wire('c').at(G32.in1).to(G31.out))
d4.add(logic.Wire('c').at(G32.in2).to(G31.out))

G33 = draw_nand(d4, 24, 7, in1=G30, in2=G32)
G34 = draw_nand(d4, 27, 7)
d4.add(logic.Wire('c').at(G34.in1).to(G33.out))
d4.add(logic.Wire('c').at(G34.in2).to(G33.out))
d4.add(logic.Line().right(0.5).at(G34.out).label('F', loc='right'))

save_drawing(d4, 'diagrama_POS_NAND_reducido.png', 'POS NAND Reducido (Doble Negación) - 22 compuertas NAND')
