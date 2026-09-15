# -*- coding: utf-8 -*-
"""
Servidor Web Flask para Reductor Lógico y Síntesis de Circuitos.
Punto de entrada web desacoplado, ligero y optimizado dinámicamente para Render (512MB) y local.
"""

import io
import os
import json
import zipfile
import hashlib
from flask import Flask, render_template, request, jsonify, send_file

from core import (
    process_logic,
    parse_function_text,
    deduce_and_simplify,
    render_single_diagram,
    DEFAULT_CONFIG,
    DIAGRAM_FILENAMES,
    get_system_profile,
    cleanup_memory,
    get_version_info,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_GEN_DIR = os.path.join(BASE_DIR, "static", "generated")
os.makedirs(STATIC_GEN_DIR, exist_ok=True)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.context_processor
def inject_version_metadata():
    """Inyecta dinámicamente la versión actual y la fecha de última actualización a todas las plantillas."""
    ver, updated = get_version_info()
    return {
        "app_version": ver,
        "app_updated": updated,
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/profile")
def api_profile():
    """Retorna información del perfil de recursos asignado dinámicamente y versión."""
    prof = get_system_profile()
    ver, updated = get_version_info()
    prof["app_version"] = ver
    prof["app_updated"] = updated
    return jsonify(prof)


@app.route("/api/process", methods=["POST"])
def api_process():
    data = request.get_json(silent=True) or {}

    if "zeros" in data and "num_bits" in data:
        num_bits = int(data.get("num_bits", 4))
        num_bits = min(5, max(2, num_bits))
        default_vars = ['A', 'B', 'C', 'D', 'E'][:num_bits]
        variables = data.get("variables", default_vars)[:num_bits]
        total = 2 ** num_bits
        zeros = sorted(list(set([int(z) for z in data.get("zeros", []) if 0 <= int(z) < total])))
        ones = sorted([i for i in range(total) if i not in zeros])
    else:
        config_text = data.get("config_text", "").strip()
        if not config_text:
            config_text = DEFAULT_CONFIG
        variables, zeros, ones = parse_function_text(config_text)

    # Identificador unívoco para aislar estados concurrentes sin colisiones
    func_key = f"{','.join(variables)}|{','.join(str(x) for x in zeros)}"
    func_hash = hashlib.md5(func_key.encode('utf-8')).hexdigest()[:10]

    state_payload = {"variables": variables, "zeros": zeros, "ones": ones, "hash": func_hash}
    try:
        with open(os.path.join(STATIC_GEN_DIR, "current_state.json"), "w", encoding="utf-8") as f:
            json.dump(state_payload, f)
        with open(os.path.join(STATIC_GEN_DIR, f"state_{func_hash}.json"), "w", encoding="utf-8") as f:
            json.dump(state_payload, f)
    except Exception:
        pass

    selected_diagrams = data.get("selected_diagrams")

    try:
        results = process_logic(
            variables=variables,
            zeros=zeros,
            ones=ones,
            out_dir=STATIC_GEN_DIR,
            base_dir=BASE_DIR,
            selected_diagrams=selected_diagrams
        )
        return jsonify({"success": True, "data": results, "hash": func_hash})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/diagram/<diagram_id>", methods=["GET", "POST"])
def api_diagram(diagram_id):
    """
    Genera o sirve un único diagrama bajo demanda.
    Permite cargar imágenes perezosamente sin colapsar la memoria de 512MB.
    Aísla las solicitudes concurrentes mediante el parámetro de hash opcional (?h=... o ?hash=...).
    """
    if diagram_id not in DIAGRAM_FILENAMES:
        return jsonify({"error": "Diagrama no válido"}), 404

    base_filename = DIAGRAM_FILENAMES[diagram_id]
    func_hash = request.args.get("h") or request.args.get("hash")

    if func_hash:
        name_part, ext = os.path.splitext(base_filename)
        filename = f"{name_part}_{func_hash}{ext}"
        filepath = os.path.join(STATIC_GEN_DIR, filename)

        if request.method == "GET" and os.path.exists(filepath):
            return send_file(filepath, mimetype="image/png")

        state_path = os.path.join(STATIC_GEN_DIR, f"state_{func_hash}.json")
        if not os.path.exists(state_path):
            state_path = os.path.join(STATIC_GEN_DIR, "current_state.json")
    else:
        filename = base_filename
        filepath = os.path.join(STATIC_GEN_DIR, filename)
        if request.method == "GET" and os.path.exists(filepath):
            return send_file(filepath, mimetype="image/png")
        state_path = os.path.join(STATIC_GEN_DIR, "current_state.json")

    if not os.path.exists(state_path):
        return jsonify({"error": "No hay función previa procesada"}), 400

    try:
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
        variables = state.get("variables", ["A", "B", "C", "D"])
        zeros = state.get("zeros", [])
        ones = state.get("ones", [])
    except Exception as e:
        return jsonify({"error": f"Error leyendo estado: {e}"}), 500

    try:
        ded = deduce_and_simplify(variables, zeros, ones)
        render_single_diagram(
            diagram_id=diagram_id,
            reduced_sop=ded["reduced_sop"],
            reduced_pos=ded["reduced_pos"],
            sop_terms=ded["sop_terms"],
            pos_clauses=ded["pos_clauses"],
            out_dir=STATIC_GEN_DIR
        )
        default_gen_path = os.path.join(STATIC_GEN_DIR, base_filename)
        if func_hash and default_gen_path != filepath and os.path.exists(default_gen_path):
            import shutil
            shutil.copy2(default_gen_path, filepath)

        cleanup_memory()
        final_to_send = filepath if (func_hash and os.path.exists(filepath)) else default_gen_path
        return send_file(final_to_send, mimetype="image/png")
    except Exception as e:
        return jsonify({"error": f"Error al generar diagrama: {e}"}), 500


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
    func_hash = request.args.get("h", "").strip()
    if func_hash and (len(func_hash) != 8 or not all(c in "0123456789abcdef" for c in func_hash.lower())):
        func_hash = ""

    target_diag_ids = []

    if selected:
        for k in selected.split(","):
            k = k.strip()
            if k in DIAGRAM_FILENAMES:
                target_diag_ids.append(k)
    else:
        target_diag_ids = list(DIAGRAM_FILENAMES.keys())

    # Verificar si falta generar algún diagrama solicitado
    state_path = os.path.join(STATIC_GEN_DIR, f"state_{func_hash}.json") if func_hash else os.path.join(STATIC_GEN_DIR, "current_state.json")
    if not os.path.exists(state_path):
        state_path = os.path.join(STATIC_GEN_DIR, "current_state.json")

    if os.path.exists(state_path):
        try:
            with open(state_path, "r", encoding="utf-8") as f:
                state = json.load(f)
            variables = state.get("variables", ["A", "B", "C", "D"])
            zeros = state.get("zeros", [])
            ones = state.get("ones", [])
            ded = None

            for did in target_diag_ids:
                base_fname = DIAGRAM_FILENAMES[did]
                fname = f"{base_fname.replace('.png', '')}_{func_hash}.png" if func_hash else base_fname
                fpath = os.path.join(STATIC_GEN_DIR, fname)
                if not os.path.exists(fpath):
                    if ded is None:
                        ded = deduce_and_simplify(variables, zeros, ones)
                    render_single_diagram(
                        diagram_id=did,
                        reduced_sop=ded["reduced_sop"],
                        reduced_pos=ded["reduced_pos"],
                        sop_terms=ded["sop_terms"],
                        pos_clauses=ded["pos_clauses"],
                        out_dir=STATIC_GEN_DIR
                    )
                    default_gen = os.path.join(STATIC_GEN_DIR, base_fname)
                    if func_hash and os.path.exists(default_gen) and default_gen != fpath:
                        import shutil
                        shutil.copy2(default_gen, fpath)
                    cleanup_memory()
        except Exception as e:
            print(f"Aviso en generación bajo demanda para ZIP: {e}")

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        if os.path.exists(STATIC_GEN_DIR):
            for did in target_diag_ids:
                base_fname = DIAGRAM_FILENAMES.get(did)
                if base_fname:
                    fpath_hashed = os.path.join(STATIC_GEN_DIR, f"{base_fname.replace('.png', '')}_{func_hash}.png") if func_hash else None
                    fpath_base = os.path.join(STATIC_GEN_DIR, base_fname)
                    fpath = fpath_hashed if (fpath_hashed and os.path.exists(fpath_hashed)) else fpath_base
                    if os.path.exists(fpath):
                        zf.write(fpath, arcname=f"Resultados/{base_fname}")

            # Incluir mapas de Karnaugh generados
            for kmap_file in ["kmap_miniterminos.png", "kmap_maxiterminos.png"]:
                kpath_hashed = os.path.join(STATIC_GEN_DIR, f"{kmap_file.replace('.png', '')}_{func_hash}.png") if func_hash else None
                kpath_base = os.path.join(STATIC_GEN_DIR, kmap_file)
                kpath = kpath_hashed if (kpath_hashed and os.path.exists(kpath_hashed)) else kpath_base
                if os.path.exists(kpath):
                    zf.write(kpath, arcname=f"Resultados/{kmap_file}")

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
    port = int(os.environ.get("PORT", 5000))
    profile = get_system_profile()
    print(f"Iniciando Servidor Web Logic Analysis en http://localhost:{port}")
    print(f"Modo de recursos activo: {profile['mode']} (DPI: {profile['dpi']}, GC agresivo: {profile['aggressive_gc']})")
    app.run(host="0.0.0.0", port=port, debug=False)
