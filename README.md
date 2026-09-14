# Logic Analysis: Reductor Booleano y Síntesis de Circuitos Digitales

Aplicación interactiva y sistema de análisis para reducción de funciones booleanas (SOP y POS), generación de mapas de Karnaugh y síntesis de esquemáticos lógicos empleando **exclusivamente compuertas de 2 entradas** (estándar AND/OR/NOT, universal NAND y universal NOR, con optimización por el principio de doble negación).

🔗 **Repositorio GitHub:** [https://github.com/igream/Logic-analysis](https://github.com/igream/Logic-analysis)

---

## 🚀 Aplicación Web Interactiva

La aplicación incluye un servidor web local (Flask) interactivo donde puedes:
1. **Introducir tu función directamente en el editor** o **cargar un archivo `.txt`**.
2. **Descargar la función actual** que estás editando en formato `.txt` (`funcion.txt`).
3. **Calcular automáticamente:**
   - Expresiones no reducidas de minitérminos ($f'$) y maxitérminos ($f$).
   - Expresiones simplificadas por mapa de Karnaugh.
   - Mapas de Karnaugh resueltos con lazos coloreados.
   - 10 diagramas lógicos con símbolos ANSI/IEEE Std 91-1984 y compuertas estrictamente de 2 entradas.
   - Tabla concluyente con el conteo exacto de compuertas por circuito.
4. **Descargar los resultados:**
   - Descarga individual de cada imagen en alta resolución (PNG).
   - Descarga del paquete completo comprimido en un solo clic (**`.ZIP`**).

### Cómo iniciar la Aplicación Web:
```bash
python app.py
```
Abre tu navegador en: [http://localhost:5000](http://localhost:5000)

---

## 💻 Uso desde Línea de Comandos (CLI)

También puedes ejecutar el reductor directamente desde la consola:
```bash
python main.py
```
o especificando un archivo personalizado:
```bash
python main.py mi_funcion.txt
```

### Formato del archivo de entrada (`funcion.txt`):
```text
# Puedes especificar las salidas en 0 (Maxitérminos) o salidas en 1 (Minitérminos)
variables = A, B, C, D
f = (0, 1, 2, 5, 6, 7, 11, 15)
```

---

## 📁 Estructura del Proyecto

```
Logic-Analysis/
│
├── app.py                                     # Servidor Web Flask (Frontend y API)
├── main.py                                    # Script ejecutable CLI con soporte para archivos externos
├── funcion.txt                                # Archivo de configuración de entrada
├── README.md                                  # Documentación técnica completa
│
├── templates/
│   └── index.html                             # Interfaz web responsiva con Tailwind CSS
│
├── static/
│   └── generated/                             # Diagramas y mapas K servidos por la web
│
├── Resultados/                                # Resultados organizados en alta resolución
│   ├── 01_Mapas_Karnaugh/
│   │   ├── kmap_miniterminos.png              # Mapa K para f' (agrupamiento de unos)
│   │   ├── kmap_maxiterminos.png              # Mapa K para f (agrupamiento de ceros)
│   │   └── kmap_comparacion.png
│   ├── 02_Diagramas_AND_OR_NOT/
│   │   ├── diagrama_SOP_AND_OR_NOT.png        # 15 compuertas
│   │   └── diagrama_POS_AND_OR_NOT.png        # 15 compuertas
│   ├── 03_Diagramas_NAND/
│   │   ├── diagrama_SOP_NAND.png              # 29 compuertas
│   │   ├── diagrama_SOP_NAND_reducido.png     # 21 compuertas (ahorro de 8 por doble negación)
│   │   ├── diagrama_POS_NAND.png              # 34 compuertas
│   │   └── diagrama_POS_NAND_reducido.png     # 22 compuertas
│   └── 04_Diagramas_NOR/
│       ├── diagrama_POS_NOR.png              # 29 compuertas
│       ├── diagrama_POS_NOR_reducido.png     # 21 compuertas (ahorro de 8 por doble negación)
│       ├── diagrama_SOP_NOR.png              # 34 compuertas
│       └── diagrama_SOP_NOR_reducido.png     # 22 compuertas
│
├── Scripts/                                   # Módulos y generadores independientes en Python
│   ├── generar_diagramas_manuales.py
│   ├── generar_mapas_karnaugh.py
│   ├── generar_todo.py
│   └── parte1_expresiones_kmaps.py
│
└── Pruebas/                                   # Prototipos y scripts de verificación
```

---

## 📊 Tabla Resumen de Conteo de Compuertas

*(Todas las compuertas utilizadas son estrictamente de 2 entradas)*

| # | Circuito Lógico | NOT | AND (2-in) | OR (2-in) | NAND (2-in) | NOR (2-in) | TOTAL | Archivo |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| 1 | **SOP Minitérminos ($f'$)** | 4 | 8 | 3 | 0 | 0 | **15** | `diagrama_SOP_AND_OR_NOT.png` |
| 2 | **POS Maxitérminos ($f$)** | 4 | 3 | 8 | 0 | 0 | **15** | `diagrama_POS_AND_OR_NOT.png` |
| 3 | **SOP NAND Universal Directo** | 0 | 0 | 0 | 29 | 0 | **29** | `diagrama_SOP_NAND.png` |
| 4 | **SOP NAND Reducido (Doble Negación)** | 0 | 0 | 0 | 21 | 0 | **21** | `diagrama_SOP_NAND_reducido.png` |
| 5 | **POS NAND Universal Directo** | 0 | 0 | 0 | 34 | 0 | **34** | `diagrama_POS_NAND.png` |
| 6 | **POS NAND Reducido (Doble Negación)** | 0 | 0 | 0 | 22 | 0 | **22** | `diagrama_POS_NAND_reducido.png` |
| 7 | **POS NOR Universal Directo** | 0 | 0 | 0 | 0 | 29 | **29** | `diagrama_POS_NOR.png` |
| 8 | **POS NOR Reducido (Doble Negación)** | 0 | 0 | 0 | 0 | 21 | **21** | `diagrama_POS_NOR_reducido.png` |
| 9 | **SOP NOR Universal Directo** | 0 | 0 | 0 | 0 | 34 | **34** | `diagrama_SOP_NOR.png` |
| 10 | **SOP NOR Reducido (Doble Negación)** | 0 | 0 | 0 | 0 | 22 | **22** | `diagrama_SOP_NOR_reducido.png` |
