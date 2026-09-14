# -*- coding: utf-8 -*-
"""
Servidor Web Flask para Reductor Lógico y Síntesis de Circuitos.
Punto de entrada web desacoplado y ligero.
"""

import io
import os
import zipfile
from flask import Flask, render_template, request, jsonify, send_file

try:
    import spaces

    @spaces.GPU(duration=1)
    def _hf_zerogpu_check():
        return None
except Exception:
    pass

from core import (
    process_logic,
    parse_function_text,
    DEFAULT_CONFIG,
    DIAGRAM_FILENAMES,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_GEN_DIR = os.path.join(BASE_DIR, "static", "generated")
os.makedirs(STATIC_GEN_DIR, exist_ok=True)

app = Flask(__name__, static_folder="static", template_folder="templates")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/process", methods=["POST"])
def api_process():
    data = request.get_json(silent=True) or {}

    if "zeros" in data and "num_bits" in data:
        num_bits = int(data.get("num_bits", 4))
        num_bits = min(5, max(2, num_bits))
        default_vars = ['A', 'B', 'C', 'D', 'E'][:num_bits]
        variables = data.get("variables", default_vars)[:num_bits]
        zeros = sorted(list(set(data.get("zeros", []))))
        total = 2 ** num_bits
        ones = sorted([i for i in range(total) if i not in zeros])
    else:
        config_text = data.get("config_text", "").strip()
        if not config_text:
            config_text = DEFAULT_CONFIG
        variables, zeros, ones = parse_function_text(config_text)

    try:
        results = process_logic(variables, zeros, ones, out_dir=STATIC_GEN_DIR, base_dir=BASE_DIR)
        return jsonify({"success": True, "data": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/download_config", methods=["POST"])
def download_config():
    data = request.get_json(silent=True) or {}
    variables = data.get("variables", ["A", "B", "C", "D"])
    zeros = data.get("zeros", [0, 1, 2, 5, 6, 7, 11, 15])

    text = "# ==============================================================================\n"
    text += "# CONFIGURACIÓN GENERADA DESDE LA TABLA DE VERDAD (Logic Analysis)\n"
    text += "# ==============================================================================\n"
    text += f"variables = {', '.join(variables)}\n"
    text += f"f = ({', '.join(str(x) for x in zeros)})  # Salidas en 0 (Maxitérminos)\n"

    buffer = io.BytesIO()
    buffer.write(text.encode("utf-8"))
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="funcion.txt", mimetype="text/plain")


@app.route("/api/download_zip")
def download_zip():
    selected = request.args.get("diagrams", "").strip()
    selected_files = set()

    if selected:
        for k in selected.split(","):
            k = k.strip()
            if k in DIAGRAM_FILENAMES:
                selected_files.add(DIAGRAM_FILENAMES[k])
            elif k.endswith(".png"):
                selected_files.add(k)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        if os.path.exists(STATIC_GEN_DIR):
            for fname in os.listdir(STATIC_GEN_DIR):
                if fname.endswith(".png"):
                    if not selected_files or fname in selected_files or fname.startswith("kmap_"):
                        fpath = os.path.join(STATIC_GEN_DIR, fname)
                        zf.write(fpath, arcname=f"Resultados/{fname}")
        zf.writestr("funcion_ejemplo.txt", DEFAULT_CONFIG)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="Resultados_Logic_Analysis.zip", mimetype="application/zip")


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


if __name__ == "__main__":
    is_hf = "SPACE_ID" in os.environ
    default_port = 7860 if is_hf else 5000
    port = int(os.environ.get("PORT", default_port))
    print(f"Iniciando Servidor Web Logic Analysis en http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
