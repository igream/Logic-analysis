import sys
if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

import schemdraw
import schemdraw.logic as logic
import matplotlib.pyplot as plt

def add_title(d, title):
    # Add title using matplotlib after drawing
    # But since schemdraw manages the plot, we can just add a label, or draw it.
    pass

def draw_pos_nor_universal():
    d = schemdraw.Drawing()
    
    # Inputs (A, B, C, D)
    N1 = d.add(logic.Nor(inputs=2).at((2, -1)).label('A', 'in1').label('A', 'in2').label("A'", 'out'))
    N2 = d.add(logic.Nor(inputs=2).at((2, -3)).label('B', 'in1').label('B', 'in2').label("B'", 'out'))
    N3 = d.add(logic.Nor(inputs=2).at((2, -5)).label('C', 'in1').label('C', 'in2').label("C'", 'out'))
    N4 = d.add(logic.Nor(inputs=2).at((2, -7)).label('D', 'in1').label('D', 'in2').label("D'", 'out'))

    # S1 = A+B+C
    G5 = d.add(logic.Nor(inputs=2).at((5, 0)).label('B', 'in1').label('C', 'in2'))
    G6 = d.add(logic.Nor(inputs=2).at((8, 0)))
    d.add(logic.Wire('c').at(G5.out).to(G6.in1))
    d.add(logic.Wire('c').at(G5.out).to(G6.in2))
    G7 = d.add(logic.Nor(inputs=2).at((11, 0)).label('A', 'in1'))
    d.add(logic.Wire('c').at(G6.out).to(G7.in2))
    G8 = d.add(logic.Nor(inputs=2).at((14, 0)))
    d.add(logic.Wire('c').at(G7.out).to(G8.in1))
    d.add(logic.Wire('c').at(G7.out).to(G8.in2))

    # S2 = A+C'+D
    G9 = d.add(logic.Nor(inputs=2).at((5, -2)).label('D', 'in2'))
    d.add(logic.Wire('c').at(N3.out).to(G9.in1))
    G10 = d.add(logic.Nor(inputs=2).at((8, -2)))
    d.add(logic.Wire('c').at(G9.out).to(G10.in1))
    d.add(logic.Wire('c').at(G9.out).to(G10.in2))
    G11 = d.add(logic.Nor(inputs=2).at((11, -2)).label('A', 'in1'))
    d.add(logic.Wire('c').at(G10.out).to(G11.in2))
    G12 = d.add(logic.Nor(inputs=2).at((14, -2)))
    d.add(logic.Wire('c').at(G11.out).to(G12.in1))
    d.add(logic.Wire('c').at(G11.out).to(G12.in2))

    # S3 = A+B'+D'
    G13 = d.add(logic.Nor(inputs=2).at((5, -4)))
    d.add(logic.Wire('c').at(N2.out).to(G13.in1))
    d.add(logic.Wire('c').at(N4.out).to(G13.in2))
    G14 = d.add(logic.Nor(inputs=2).at((8, -4)))
    d.add(logic.Wire('c').at(G13.out).to(G14.in1))
    d.add(logic.Wire('c').at(G13.out).to(G14.in2))
    G15 = d.add(logic.Nor(inputs=2).at((11, -4)).label('A', 'in1'))
    d.add(logic.Wire('c').at(G14.out).to(G15.in2))
    G16 = d.add(logic.Nor(inputs=2).at((14, -4)))
    d.add(logic.Wire('c').at(G15.out).to(G16.in1))
    d.add(logic.Wire('c').at(G15.out).to(G16.in2))

    # S4 = A'+C'+D'
    G17 = d.add(logic.Nor(inputs=2).at((5, -6)))
    d.add(logic.Wire('c').at(N1.out).to(G17.in1))
    d.add(logic.Wire('c').at(N3.out).to(G17.in2))
    G18 = d.add(logic.Nor(inputs=2).at((8, -6)))
    d.add(logic.Wire('c').at(G17.out).to(G18.in1))
    d.add(logic.Wire('c').at(G17.out).to(G18.in2))
    G19 = d.add(logic.Nor(inputs=2).at((11, -6)))
    d.add(logic.Wire('c').at(G18.out).to(G19.in1))
    d.add(logic.Wire('c').at(N4.out).to(G19.in2))
    G20 = d.add(logic.Nor(inputs=2).at((14, -6)))
    d.add(logic.Wire('c').at(G19.out).to(G20.in1))
    d.add(logic.Wire('c').at(G19.out).to(G20.in2))

    # AND tree
    G21 = d.add(logic.Nor(inputs=2).at((17, 0)))
    d.add(logic.Wire('c').at(G8.out).to(G21.in1))
    d.add(logic.Wire('c').at(G8.out).to(G21.in2))
    
    G22 = d.add(logic.Nor(inputs=2).at((17, -2)))
    d.add(logic.Wire('c').at(G12.out).to(G22.in1))
    d.add(logic.Wire('c').at(G12.out).to(G22.in2))
    
    G23 = d.add(logic.Nor(inputs=2).at((20, -1)))
    d.add(logic.Wire('c').at(G21.out).to(G23.in1))
    d.add(logic.Wire('c').at(G22.out).to(G23.in2))

    G24 = d.add(logic.Nor(inputs=2).at((17, -4)))
    d.add(logic.Wire('c').at(G16.out).to(G24.in1))
    d.add(logic.Wire('c').at(G16.out).to(G24.in2))
    
    G25 = d.add(logic.Nor(inputs=2).at((17, -6)))
    d.add(logic.Wire('c').at(G20.out).to(G25.in1))
    d.add(logic.Wire('c').at(G20.out).to(G25.in2))
    
    G26 = d.add(logic.Nor(inputs=2).at((20, -5)))
    d.add(logic.Wire('c').at(G24.out).to(G26.in1))
    d.add(logic.Wire('c').at(G25.out).to(G26.in2))

    G27 = d.add(logic.Nor(inputs=2).at((23, -1)))
    d.add(logic.Wire('c').at(G23.out).to(G27.in1))
    d.add(logic.Wire('c').at(G23.out).to(G27.in2))
    
    G28 = d.add(logic.Nor(inputs=2).at((23, -5)))
    d.add(logic.Wire('c').at(G26.out).to(G28.in1))
    d.add(logic.Wire('c').at(G26.out).to(G28.in2))
    
    G29 = d.add(logic.Nor(inputs=2).at((26, -3)).label('F', 'out'))
    d.add(logic.Wire('c').at(G27.out).to(G29.in1))
    d.add(logic.Wire('c').at(G28.out).to(G29.in2))

    d.draw()
    plt.title("POS NOR Universal - 29 compuertas NOR")
    d.save('diagrama_POS_NOR.png', dpi=200)
    plt.close()

def draw_pos_nor_reduced():
    d = schemdraw.Drawing()
    
    # Inputs
    N1 = d.add(logic.Nor(inputs=2).at((2, -1)).label('A', 'in1').label('A', 'in2').label("A'", 'out'))
    N2 = d.add(logic.Nor(inputs=2).at((2, -3)).label('B', 'in1').label('B', 'in2').label("B'", 'out'))
    N3 = d.add(logic.Nor(inputs=2).at((2, -5)).label('C', 'in1').label('C', 'in2').label("C'", 'out'))
    N4 = d.add(logic.Nor(inputs=2).at((2, -7)).label('D', 'in1').label('D', 'in2').label("D'", 'out'))

    # S1
    G5 = d.add(logic.Nor(inputs=2).at((5, 0)).label('B', 'in1').label('C', 'in2'))
    G6 = d.add(logic.Nor(inputs=2).at((8, 0)))
    d.add(logic.Wire('c').at(G5.out).to(G6.in1))
    d.add(logic.Wire('c').at(G5.out).to(G6.in2))
    G7 = d.add(logic.Nor(inputs=2).at((11, 0)).label('A', 'in1'))
    d.add(logic.Wire('c').at(G6.out).to(G7.in2))

    # S2
    G9 = d.add(logic.Nor(inputs=2).at((5, -2)).label('D', 'in2'))
    d.add(logic.Wire('c').at(N3.out).to(G9.in1))
    G10 = d.add(logic.Nor(inputs=2).at((8, -2)))
    d.add(logic.Wire('c').at(G9.out).to(G10.in1))
    d.add(logic.Wire('c').at(G9.out).to(G10.in2))
    G11 = d.add(logic.Nor(inputs=2).at((11, -2)).label('A', 'in1'))
    d.add(logic.Wire('c').at(G10.out).to(G11.in2))

    # S3
    G13 = d.add(logic.Nor(inputs=2).at((5, -4)))
    d.add(logic.Wire('c').at(N2.out).to(G13.in1))
    d.add(logic.Wire('c').at(N4.out).to(G13.in2))
    G14 = d.add(logic.Nor(inputs=2).at((8, -4)))
    d.add(logic.Wire('c').at(G13.out).to(G14.in1))
    d.add(logic.Wire('c').at(G13.out).to(G14.in2))
    G15 = d.add(logic.Nor(inputs=2).at((11, -4)).label('A', 'in1'))
    d.add(logic.Wire('c').at(G14.out).to(G15.in2))

    # S4
    G17 = d.add(logic.Nor(inputs=2).at((5, -6)))
    d.add(logic.Wire('c').at(N1.out).to(G17.in1))
    d.add(logic.Wire('c').at(N3.out).to(G17.in2))
    G18 = d.add(logic.Nor(inputs=2).at((8, -6)))
    d.add(logic.Wire('c').at(G17.out).to(G18.in1))
    d.add(logic.Wire('c').at(G17.out).to(G18.in2))
    G19 = d.add(logic.Nor(inputs=2).at((11, -6)))
    d.add(logic.Wire('c').at(G18.out).to(G19.in1))
    d.add(logic.Wire('c').at(N4.out).to(G19.in2))

    # AND tree reduced
    G23 = d.add(logic.Nor(inputs=2).at((14, -1)))
    d.add(logic.Wire('c').at(G7.out).to(G23.in1))
    d.add(logic.Wire('c').at(G11.out).to(G23.in2))

    G26 = d.add(logic.Nor(inputs=2).at((14, -5)))
    d.add(logic.Wire('c').at(G15.out).to(G26.in1))
    d.add(logic.Wire('c').at(G19.out).to(G26.in2))

    G27 = d.add(logic.Nor(inputs=2).at((17, -1)))
    d.add(logic.Wire('c').at(G23.out).to(G27.in1))
    d.add(logic.Wire('c').at(G23.out).to(G27.in2))
    
    G28 = d.add(logic.Nor(inputs=2).at((17, -5)))
    d.add(logic.Wire('c').at(G26.out).to(G28.in1))
    d.add(logic.Wire('c').at(G26.out).to(G28.in2))
    
    G29 = d.add(logic.Nor(inputs=2).at((20, -3)).label('F', 'out'))
    d.add(logic.Wire('c').at(G27.out).to(G29.in1))
    d.add(logic.Wire('c').at(G28.out).to(G29.in2))

    d.draw()
    plt.title("POS NOR Reducido (Doble Negación) - 21 compuertas NOR")
    d.save('diagrama_POS_NOR_reducido.png', dpi=200)
    plt.close()

def draw_sop_nor_universal():
    d = schemdraw.Drawing()
    
    # Inputs
    N1 = d.add(logic.Nor(inputs=2).at((2, -1)).label('A', 'in1').label('A', 'in2').label("A'", 'out'))
    N2 = d.add(logic.Nor(inputs=2).at((2, -3)).label('B', 'in1').label('B', 'in2').label("B'", 'out'))
    N3 = d.add(logic.Nor(inputs=2).at((2, -5)).label('C', 'in1').label('C', 'in2').label("C'", 'out'))
    N4 = d.add(logic.Nor(inputs=2).at((2, -7)).label('D', 'in1').label('D', 'in2').label("D'", 'out'))

    # P1 = A'B'C'
    G5 = d.add(logic.Nor(inputs=2).at((5, 0)))
    d.add(logic.Wire('c').at(N2.out).to(G5.in1)); d.add(logic.Wire('c').at(N2.out).to(G5.in2))
    G6 = d.add(logic.Nor(inputs=2).at((5, -1)))
    d.add(logic.Wire('c').at(N3.out).to(G6.in1)); d.add(logic.Wire('c').at(N3.out).to(G6.in2))
    G7 = d.add(logic.Nor(inputs=2).at((8, -0.5)))
    d.add(logic.Wire('c').at(G5.out).to(G7.in1)); d.add(logic.Wire('c').at(G6.out).to(G7.in2))
    
    G8 = d.add(logic.Nor(inputs=2).at((11, 0)))
    d.add(logic.Wire('c').at(N1.out).to(G8.in1)); d.add(logic.Wire('c').at(N1.out).to(G8.in2))
    G9 = d.add(logic.Nor(inputs=2).at((11, -1)))
    d.add(logic.Wire('c').at(G7.out).to(G9.in1)); d.add(logic.Wire('c').at(G7.out).to(G9.in2))
    G10 = d.add(logic.Nor(inputs=2).at((14, -0.5)))
    d.add(logic.Wire('c').at(G8.out).to(G10.in1)); d.add(logic.Wire('c').at(G9.out).to(G10.in2))

    # P2 = A'CD'
    G11 = d.add(logic.Nor(inputs=2).at((5, -2)))
    d.add(logic.Wire('c').at(N1.out).to(G11.in1)); d.add(logic.Wire('c').at(N1.out).to(G11.in2))
    G12 = d.add(logic.Nor(inputs=2).at((5, -3)).label('C', 'in1').label('C', 'in2'))
    G13 = d.add(logic.Nor(inputs=2).at((8, -2.5)))
    d.add(logic.Wire('c').at(G11.out).to(G13.in1)); d.add(logic.Wire('c').at(G12.out).to(G13.in2))
    
    G14 = d.add(logic.Nor(inputs=2).at((11, -2)))
    d.add(logic.Wire('c').at(G13.out).to(G14.in1)); d.add(logic.Wire('c').at(G13.out).to(G14.in2))
    G15 = d.add(logic.Nor(inputs=2).at((11, -3)))
    d.add(logic.Wire('c').at(N4.out).to(G15.in1)); d.add(logic.Wire('c').at(N4.out).to(G15.in2))
    G16 = d.add(logic.Nor(inputs=2).at((14, -2.5)))
    d.add(logic.Wire('c').at(G14.out).to(G16.in1)); d.add(logic.Wire('c').at(G15.out).to(G16.in2))

    # P3 = A'BD
    G17 = d.add(logic.Nor(inputs=2).at((5, -4)))
    d.add(logic.Wire('c').at(N1.out).to(G17.in1)); d.add(logic.Wire('c').at(N1.out).to(G17.in2))
    G18 = d.add(logic.Nor(inputs=2).at((5, -5)).label('B', 'in1').label('B', 'in2'))
    G19 = d.add(logic.Nor(inputs=2).at((8, -4.5)))
    d.add(logic.Wire('c').at(G17.out).to(G19.in1)); d.add(logic.Wire('c').at(G18.out).to(G19.in2))
    
    G20 = d.add(logic.Nor(inputs=2).at((11, -4)))
    d.add(logic.Wire('c').at(G19.out).to(G20.in1)); d.add(logic.Wire('c').at(G19.out).to(G20.in2))
    G21 = d.add(logic.Nor(inputs=2).at((11, -5)).label('D', 'in1').label('D', 'in2'))
    G22 = d.add(logic.Nor(inputs=2).at((14, -4.5)))
    d.add(logic.Wire('c').at(G20.out).to(G22.in1)); d.add(logic.Wire('c').at(G21.out).to(G22.in2))

    # P4 = ACD
    G23 = d.add(logic.Nor(inputs=2).at((5, -6)).label('A', 'in1').label('A', 'in2'))
    G24 = d.add(logic.Nor(inputs=2).at((5, -7)).label('C', 'in1').label('C', 'in2'))
    G25 = d.add(logic.Nor(inputs=2).at((8, -6.5)))
    d.add(logic.Wire('c').at(G23.out).to(G25.in1)); d.add(logic.Wire('c').at(G24.out).to(G25.in2))
    
    G26 = d.add(logic.Nor(inputs=2).at((11, -6)))
    d.add(logic.Wire('c').at(G25.out).to(G26.in1)); d.add(logic.Wire('c').at(G25.out).to(G26.in2))
    G27 = d.add(logic.Nor(inputs=2).at((11, -7)).label('D', 'in1').label('D', 'in2'))
    G28 = d.add(logic.Nor(inputs=2).at((14, -6.5)))
    d.add(logic.Wire('c').at(G26.out).to(G28.in1)); d.add(logic.Wire('c').at(G27.out).to(G28.in2))

    # OR tree
    G29 = d.add(logic.Nor(inputs=2).at((17, -1.5)))
    d.add(logic.Wire('c').at(G10.out).to(G29.in1)); d.add(logic.Wire('c').at(G16.out).to(G29.in2))
    G30 = d.add(logic.Nor(inputs=2).at((20, -1.5)))
    d.add(logic.Wire('c').at(G29.out).to(G30.in1)); d.add(logic.Wire('c').at(G29.out).to(G30.in2))

    G31 = d.add(logic.Nor(inputs=2).at((17, -5.5)))
    d.add(logic.Wire('c').at(G22.out).to(G31.in1)); d.add(logic.Wire('c').at(G28.out).to(G31.in2))
    G32 = d.add(logic.Nor(inputs=2).at((20, -5.5)))
    d.add(logic.Wire('c').at(G31.out).to(G32.in1)); d.add(logic.Wire('c').at(G31.out).to(G32.in2))

    G33 = d.add(logic.Nor(inputs=2).at((23, -3.5)))
    d.add(logic.Wire('c').at(G30.out).to(G33.in1)); d.add(logic.Wire('c').at(G32.out).to(G33.in2))
    G34 = d.add(logic.Nor(inputs=2).at((26, -3.5)).label("F'", 'out'))
    d.add(logic.Wire('c').at(G33.out).to(G34.in1)); d.add(logic.Wire('c').at(G33.out).to(G34.in2))

    d.draw()
    plt.title("SOP NOR Universal - 34 compuertas NOR")
    d.save('diagrama_SOP_NOR.png', dpi=200)
    plt.close()

def draw_sop_nor_reduced():
    d = schemdraw.Drawing()
    
    # Inputs
    N1 = d.add(logic.Nor(inputs=2).at((2, -1)).label('A', 'in1').label('A', 'in2').label("A'", 'out'))
    N2 = d.add(logic.Nor(inputs=2).at((2, -3)).label('B', 'in1').label('B', 'in2').label("B'", 'out'))
    N3 = d.add(logic.Nor(inputs=2).at((2, -5)).label('C', 'in1').label('C', 'in2').label("C'", 'out'))
    N4 = d.add(logic.Nor(inputs=2).at((2, -7)).label('D', 'in1').label('D', 'in2').label("D'", 'out'))

    # P1 = A'B'C' -> NOR(A, (B'C')') -> NOR(A, NOR(B,C))
    G7 = d.add(logic.Nor(inputs=2).at((8, -0.5)).label('B', 'in1').label('C', 'in2'))
    G9 = d.add(logic.Nor(inputs=2).at((11, -1)))
    d.add(logic.Wire('c').at(G7.out).to(G9.in1)); d.add(logic.Wire('c').at(G7.out).to(G9.in2))
    G10 = d.add(logic.Nor(inputs=2).at((14, -0.5)).label('A', 'in1'))
    d.add(logic.Wire('c').at(G9.out).to(G10.in2))

    # P2 = A'CD' -> NOR((A'C)', D) -> NOR(NOR(A, C'), D) -> NOR(NOR(A, N3), D)
    G13 = d.add(logic.Nor(inputs=2).at((8, -2.5)).label('A', 'in1'))
    d.add(logic.Wire('c').at(N3.out).to(G13.in2))
    G14 = d.add(logic.Nor(inputs=2).at((11, -2)))
    d.add(logic.Wire('c').at(G13.out).to(G14.in1)); d.add(logic.Wire('c').at(G13.out).to(G14.in2))
    G16 = d.add(logic.Nor(inputs=2).at((14, -2.5)).label('D', 'in2'))
    d.add(logic.Wire('c').at(G14.out).to(G16.in1))

    # P3 = A'BD -> NOR((A'B)', D') -> NOR(NOR(A, B'), D') -> NOR(NOR(A, N2), N4)
    G19 = d.add(logic.Nor(inputs=2).at((8, -4.5)).label('A', 'in1'))
    d.add(logic.Wire('c').at(N2.out).to(G19.in2))
    G20 = d.add(logic.Nor(inputs=2).at((11, -4)))
    d.add(logic.Wire('c').at(G19.out).to(G20.in1)); d.add(logic.Wire('c').at(G19.out).to(G20.in2))
    G22 = d.add(logic.Nor(inputs=2).at((14, -4.5)))
    d.add(logic.Wire('c').at(G20.out).to(G22.in1)); d.add(logic.Wire('c').at(N4.out).to(G22.in2))

    # P4 = ACD -> NOR((AC)', D') -> NOR(NOR(A', C'), D') -> NOR(NOR(N1, N3), N4)
    G25 = d.add(logic.Nor(inputs=2).at((8, -6.5)))
    d.add(logic.Wire('c').at(N1.out).to(G25.in1)); d.add(logic.Wire('c').at(N3.out).to(G25.in2))
    G26 = d.add(logic.Nor(inputs=2).at((11, -6)))
    d.add(logic.Wire('c').at(G25.out).to(G26.in1)); d.add(logic.Wire('c').at(G25.out).to(G26.in2))
    G28 = d.add(logic.Nor(inputs=2).at((14, -6.5)))
    d.add(logic.Wire('c').at(G26.out).to(G28.in1)); d.add(logic.Wire('c').at(N4.out).to(G28.in2))

    # OR tree
    G29 = d.add(logic.Nor(inputs=2).at((17, -1.5)))
    d.add(logic.Wire('c').at(G10.out).to(G29.in1)); d.add(logic.Wire('c').at(G16.out).to(G29.in2))
    G30 = d.add(logic.Nor(inputs=2).at((20, -1.5)))
    d.add(logic.Wire('c').at(G29.out).to(G30.in1)); d.add(logic.Wire('c').at(G29.out).to(G30.in2))

    G31 = d.add(logic.Nor(inputs=2).at((17, -5.5)))
    d.add(logic.Wire('c').at(G22.out).to(G31.in1)); d.add(logic.Wire('c').at(G28.out).to(G31.in2))
    G32 = d.add(logic.Nor(inputs=2).at((20, -5.5)))
    d.add(logic.Wire('c').at(G31.out).to(G32.in1)); d.add(logic.Wire('c').at(G31.out).to(G32.in2))

    G33 = d.add(logic.Nor(inputs=2).at((23, -3.5)))
    d.add(logic.Wire('c').at(G30.out).to(G33.in1)); d.add(logic.Wire('c').at(G32.out).to(G33.in2))
    G34 = d.add(logic.Nor(inputs=2).at((26, -3.5)).label("F'", 'out'))
    d.add(logic.Wire('c').at(G33.out).to(G34.in1)); d.add(logic.Wire('c').at(G33.out).to(G34.in2))

    d.draw()
    plt.title("SOP NOR Reducido (Doble Negación) - 22 compuertas NOR")
    d.save('diagrama_SOP_NOR_reducido.png', dpi=200)
    plt.close()

if __name__ == '__main__':
    draw_pos_nor_universal()
    draw_pos_nor_reduced()
    draw_sop_nor_universal()
    draw_sop_nor_reduced()
    print("Generated 4 diagrams successfully.")
