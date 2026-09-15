# -*- coding: utf-8 -*-
"""
Módulo de Versionado Dinámico y Fecha de Actualización Automática.
Calcula la versión del proyecto a partir del historial de commits de Git:
Inicia en v1.0, escala secuencialmente en cada corrección (v1.1, v1.2 ... v1.9),
avanzando a v2.0, v2.1, etc., de manera 100% automática y sin intervención manual.
"""

import os
import subprocess
import datetime

# Conteo base de commits para anclar la versión inicial en v1.0 (commit actual #20)
BASE_COMMIT_COUNT = 20

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

    total_commits = None
    commit_time = None
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 1. Intentar consultar Git
    try:
        count_out = subprocess.check_output(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=repo_dir,
            stderr=subprocess.DEVNULL
        ).decode().strip()
        total_commits = int(count_out)
    except Exception:
        pass

    try:
        time_out = subprocess.check_output(
            ["git", "log", "-1", "--format=%ct"],
            cwd=repo_dir,
            stderr=subprocess.DEVNULL
        ).decode().strip()
        commit_time = datetime.datetime.fromtimestamp(int(time_out))
    except Exception:
        pass

    # 2. Fallbacks si git no está disponible
    if total_commits is None:
        # Fallback a conteo base si no hay git
        total_commits = BASE_COMMIT_COUNT

    if commit_time is None:
        # Usar la fecha de modificación del archivo más reciente del core o app.py
        app_file = os.path.join(repo_dir, "app.py")
        if os.path.exists(app_file):
            mtime = os.path.getmtime(app_file)
            commit_time = datetime.datetime.fromtimestamp(mtime)
        else:
            commit_time = datetime.datetime.now()

    # 3. Regla matemática de progresión de versiones:
    # offset = 0 -> v1.0
    # offset = 1 -> v1.1 ... offset = 9 -> v1.9
    # offset = 10 -> v2.0 ... offset = 19 -> v2.9
    # offset = 20 -> v3.0 ...
    offset = max(0, total_commits - BASE_COMMIT_COUNT)
    major = 1 + (offset // 10)
    minor = offset % 10
    version = f"v{major}.{minor}"

    updated_str = _format_spanish_date(commit_time)

    _VERSION_CACHE = version
    _UPDATED_CACHE = updated_str
    return version, updated_str
