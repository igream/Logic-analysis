# Reducción Booleana y Síntesis de Circuitos Lógicos (4 Bits, Compuertas de 2 Entradas)

Este proyecto contiene la resolución analítica, minimización por mapas de Karnaugh, esquemáticos en compuertas estándar de 2 entradas (AND/OR/NOT) y adopciones universales mediante compuertas NAND y NOR (directas y reducidas por el principio de doble negación).

---

## Estructura del Proyecto

```
Reductor/
│
├── README.md                                  # Documentación general del proyecto
│
├── Resultados/                                # Archivos finales y diagramas
│   ├── 01_Mapas_Karnaugh/                     # Mapas de Karnaugh de minitérminos y maxitérminos
│   │   ├── kmap_miniterminos.png              # Mapa de Karnaugh para f' (agrupamiento de unos)
│   │   ├── kmap_maxiterminos.png              # Mapa de Karnaugh para f (agrupamiento de ceros)
│   │   └── kmap_comparacion.png               # Comparación visual lado a lado
│   │
│   ├── 02_Diagramas_AND_OR_NOT/               # Circuitos estándar con compuertas de 2 entradas
│   │   ├── diagrama_SOP_AND_OR_NOT.png        # Minitérminos (SOP): 4 NOT, 8 AND, 3 OR (15 compuertas)
│   │   └── diagrama_POS_AND_OR_NOT.png        # Maxitérminos (POS): 4 NOT, 8 OR, 3 AND (15 compuertas)
│   │
│   ├── 03_Diagramas_NAND/                     # Implementaciones universales NAND (2 entradas)
│   │   ├── diagrama_SOP_NAND.png              # SOP Universal NAND Directo (29 compuertas)
│   │   ├── diagrama_SOP_NAND_reducido.png     # SOP Universal NAND Reducido por Doble Negación (21 compuertas)
│   │   ├── diagrama_POS_NAND.png              # POS Universal NAND Directo (34 compuertas)
│   │   └── diagrama_POS_NAND_reducido.png     # POS Universal NAND Reducido por Doble Negación (22 compuertas)
│   │
│   └── 04_Diagramas_NOR/                      # Implementaciones universales NOR (2 entradas)
│       ├── diagrama_POS_NOR.png              # POS Universal NOR Directo (29 compuertas)
│       ├── diagrama_POS_NOR_reducido.png     # POS Universal NOR Reducido por Doble Negación (21 compuertas)
│       ├── diagrama_SOP_NOR.png              # SOP Universal NOR Directo (34 compuertas)
│       └── diagrama_SOP_NOR_reducido.png     # SOP Universal NOR Reducido por Doble Negación (22 compuertas)
│
├── Scripts/                                   # Código fuente generador en Python
│   ├── parte1_expresiones_kmaps.py            # Deducción booleana y mapas K-map
│   ├── parte2_diagramas_and_or_not.py         # Generación de diagramas AND/OR/NOT
│   ├── parte3_diagramas_nand.py               # Generación y validación NAND
│   ├── parte4_diagramas_nor.py                # Generación y validación NOR
│   ├── generar_diagramas_manuales.py          # Generador de circuitos con Schemdraw
│   ├── generar_mapas_karnaugh.py              # Generador gráfico de K-maps
│   ├── generar_todo.py                        # Script maestro de ejecución
│   └── reduccion_logica.py                    # Validación matemática con SymPy
│
└── Pruebas/                                   # Pruebas intermedias y prototipos de renderizado
    ├── test_*.py
    └── test_*.png
```

---

## Resumen Teórico

### 1. Definición de la Función
- $f(A,B,C,D) = \sum 0 \text{ en } \{0, 1, 2, 5, 6, 7, 11, 15\}$ (Maxitérminos)
- $f'(A,B,C,D) = \sum 1 \text{ en } \{0, 1, 2, 5, 6, 7, 11, 15\}$ (Minitérminos)

### 2. Expresiones Lógicas
- **Minitérminos no reducida ($f'$):**
  $$f' = A'B'C'D' + A'B'C'D + A'B'CD' + A'BC'D + A'BCD' + A'BCD + AB'CD + ABCD$$
- **Maxitérminos no reducida ($f$):**
  $$f = (A+B+C+D)(A+B+C+D')(A+B+C'+D)(A+B'+C+D')(A+B'+C'+D)(A+B'+C'+D')(A'+B+C'+D')(A'+B'+C'+D')$$
- **Minitérminos reducida ($f'$ - SOP):**
  $$f' = A'B'C' + A'CD' + A'BD + ACD$$
- **Maxitérminos reducida ($f$ - POS):**
  $$f = (A+B+C)(A+C'+D)(A+B'+D')(A'+C'+D')$$

---

## Tabla Resumen de Conteo de Compuertas

Todas las compuertas utilizadas tienen estrictamente **2 entradas**.

| # | Circuito | NOT | AND (2-in) | OR (2-in) | NAND (2-in) | NOR (2-in) | Total | Ubicación del Archivo |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| 1 | **SOP Minitérminos ($f'$)** | 4 | 8 | 3 | 0 | 0 | **15** | `Resultados/02_Diagramas_AND_OR_NOT/diagrama_SOP_AND_OR_NOT.png` |
| 2 | **POS Maxitérminos ($f$)** | 4 | 3 | 8 | 0 | 0 | **15** | `Resultados/02_Diagramas_AND_OR_NOT/diagrama_POS_AND_OR_NOT.png` |
| 3 | **SOP NAND Directo** | 0 | 0 | 0 | 29 | 0 | **29** | `Resultados/03_Diagramas_NAND/diagrama_SOP_NAND.png` |
| 4 | **SOP NAND Reducido** | 0 | 0 | 0 | 21 | 0 | **21** | `Resultados/03_Diagramas_NAND/diagrama_SOP_NAND_reducido.png` |
| 5 | **POS NAND Directo** | 0 | 0 | 0 | 34 | 0 | **34** | `Resultados/03_Diagramas_NAND/diagrama_POS_NAND.png` |
| 6 | **POS NAND Reducido** | 0 | 0 | 0 | 22 | 0 | **22** | `Resultados/03_Diagramas_NAND/diagrama_POS_NAND_reducido.png` |
| 7 | **POS NOR Directo** | 0 | 0 | 0 | 0 | 29 | **29** | `Resultados/04_Diagramas_NOR/diagrama_POS_NOR.png` |
| 8 | **POS NOR Reducido** | 0 | 0 | 0 | 0 | 21 | **21** | `Resultados/04_Diagramas_NOR/diagrama_POS_NOR_reducido.png` |
| 9 | **SOP NOR Directo** | 0 | 0 | 0 | 0 | 34 | **34** | `Resultados/04_Diagramas_NOR/diagrama_SOP_NOR.png` |
| 10 | **SOP NOR Reducido** | 0 | 0 | 0 | 0 | 22 | **22** | `Resultados/04_Diagramas_NOR/diagrama_SOP_NOR_reducido.png` |
