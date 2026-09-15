# Logic Analysis

Reductor booleano y sintetizador de circuitos digitales con compuertas de dos entradas.

Repositorio: https://github.com/igream/Logic-analysis
Acceso a prueba: https://logic-analysis.onrender.com

## Descripcion

Logic Analysis es una aplicacion interactiva que permite:
- Simplificar funciones booleanas mediante mapas de Karnaugh para miniterminos (SOP) y maxiterminos (POS).
- Generar mapas de Karnaugh con lazos de agrupacion coloreados.
- Sintetizar 10 esquematicos de circuitos logicos empleando exclusivamente compuertas de 2 entradas (AND/OR/NOT, universal NAND y universal NOR).
- Contar de forma exacta el numero de compuertas requeridas por cada topologia.
- Editar y evaluar funciones mediante una tabla de verdad dinamica configurable de 2 a 5 variables.
- Descargar resultados individuales en alta resolucion o en paquete comprimido ZIP.

## Requisitos

- Python 3.10 o superior
- Dependencias incluidas en requirements.txt:
  - Flask
  - SymPy
  - Matplotlib
  - Schemdraw
  - Gunicorn

## Instalacion y ejecucion local

1. Clonar el repositorio:
```bash
git clone https://github.com/igream/Logic-analysis.git
cd Logic-analysis
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Iniciar la aplicacion web:
```bash
python app.py
```
Abrir en el navegador: http://localhost:5000

4. Ejecucion por linea de comandos (CLI):
```bash
python main.py
```
o especificando un archivo:
```bash
python main.py funcion.txt
```

## Estructura del proyecto

- app.py: Servidor web Flask y API de procesamiento.
- main.py: Punto de entrada para ejecucion por consola.
- core/: Modulos de logica booleana, simplificacion, conteo y trazado de esquematicos.
- templates/: Plantillas de la interfaz de usuario.
- static/: Archivos estaticos (JavaScript, estilos e imagenes generadas).
- requirements.txt: Dependencias del proyecto.
- funcion.txt: Archivo de ejemplo para funciones booleanas.
