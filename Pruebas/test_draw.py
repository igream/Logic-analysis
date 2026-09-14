import schemdraw
from schemdraw import logic

with schemdraw.Drawing(file='test_circuit.png') as d:
    g1 = d.add(logic.Nand(inputs=2).at((0, 6)).label('A', 'in1', loc='left').label("C'", 'in2', loc='left'))
    g2 = d.add(logic.Nand(inputs=2).at((0, 4)).label('A', 'in1', loc='left').label("D'", 'in2', loc='left'))
    g3 = d.add(logic.Nand(inputs=3).at((0, 2)).label('B', 'in1', loc='left').label("C'", 'in2', loc='left').label("D'", 'in3', loc='left'))
    g4 = d.add(logic.Nand(inputs=4).at((0, 0)).label("A'", 'in1', loc='left').label("B'", 'in2', loc='left').label('C', 'in3', loc='left').label('D', 'in4', loc='left'))
    
    out_gate = d.add(logic.Nand(inputs=4).at((6, 3)))
    d.add(logic.Wire('c').at(g1.out).to(out_gate.in1))
    d.add(logic.Wire('c').at(g2.out).to(out_gate.in2))
    d.add(logic.Wire('c').at(g3.out).to(out_gate.in3))
    d.add(logic.Wire('c').at(g4.out).to(out_gate.in4))
    d.add(logic.Line().right(1).at(out_gate.out).label('F', loc='right'))
print('Circuit test success!')
