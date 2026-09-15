# -*- coding: utf-8 -*-
"""
Módulo de Versionado Dinámico y Fecha de Actualización Automática.
Calcula la versión del proyecto de forma dinámica y alineada con las Releases de Git:
Toma como referencia la última Release/Tag creada (ej: v1.0).
Cada nuevo commit incrementa automáticamente el dígito menor (v1.1, v1.2 ... v1.9),
avanzando a v2.0, v2.1, etc. Al crear una nueva Release/Tag en el repositorio,
el conteo se sincroniza automáticamente con ella.
"""

import os
import subprocess
import datetime

_VERSION_CACHE = None
_UPDATED_CACHE = None


def _format_spanish_date(dt):
    months = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    return f"{dt.day} de {months[dt.month - 1]} de {dt.year}, {dt.strftime('%H:%M')}"


def get_version_info():
    """
    Obtiene la versión dinámica y la fecha de última actualización.
    Retorna una tupla: (version, updated_date_str).
    """
    global _VERSION_CACHE, _UPDATED_CACHE
    if _VERSION_CACHE is not None and _UPDATED_CACHE is not None:
        return _VERSION_CACHE, _UPDATED_CACHE

    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    version = None
    commit_time = None

    # 1. Intentar calcular versión dinámica a partir de git describe (Tags / Releases)
    try:
        desc = subprocess.check_output(
            ["git", "describe", "--tags", "--match=v*", "--long"],
            cwd=repo_dir,
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        # Formato esperado: v1.0-0-g17834a6
        parts = desc.split("-")
        tag_str = parts[0].lstrip("v")
        count = int(parts[1])

        tag_parts = [int(p) for p in tag_str.split(".")]
        base_major = tag_parts[0] if len(tag_parts) > 0 else 1
        base_minor = tag_parts[1] if len(tag_parts) > 1 else 0

        total_offset = base_minor + count
        major = base_major + (total_offset // 10)
        minor = total_offset % 10
        version = f"v{major}.{minor}"
    except Exception:
        pass

    # 2. Obtener timestamp del commit
    try:
        time_out = subprocess.check_output(
            ["git", "log", "-1", "--format=%ct"],
            cwd=repo_dir,
            stderr=subprocess.DEVNULL
        ).decode().strip()
        commit_time = datetime.datetime.fromtimestamp(int(time_out))
    except Exception:
        pass

    # 3. Fallbacks si git no está disponible
    if version is None:
        version = "v1.0"

    if commit_time is None:
        app_file = os.path.join(repo_dir, "app.py")
        if os.path.exists(app_file):
            mtime = os.path.getmtime(app_file)
            commit_time = datetime.datetime.fromtimestamp(mtime)
        else:
            commit_time = datetime.datetime.now()

    updated_str = _format_spanish_date(commit_time)

    _VERSION_CACHE = version
    _UPDATED_CACHE = updated_str
    return version, updated_str
