# -*- coding: utf-8 -*-
"""
Módulo de Detección Dinámica de Recursos (Resource Manager)
Detecta automáticamente el entorno de ejecución (Render, Docker con límites de cgroup,
o máquina local con abundantes recursos) y configura los perfiles de memoria, DPI y limpieza.
Totalmente resiliente: funciona incluso si psutil no está instalado usando /proc/meminfo.
"""

import os
import gc

try:
    import psutil
except ImportError:
    psutil = None

# Límite para considerar un entorno de memoria restringida (1.2 GB en bytes)
RESTRICTED_RAM_THRESHOLD_BYTES = 1.2 * 1024 * 1024 * 1024

def _detect_cgroup_memory_limit():
    """
    Intenta leer los límites de memoria impuestos por cgroups v1 o v2 en Linux/Docker.
    Retorna el límite en bytes o None si no está disponible.
    """
    # cgroups v2
    cgroup_v2 = "/sys/fs/cgroup/memory.max"
    if os.path.exists(cgroup_v2):
        try:
            with open(cgroup_v2, "r") as f:
                val = f.read().strip()
                if val != "max":
                    return int(val)
        except Exception:
            pass

    # cgroups v1
    cgroup_v1 = "/sys/fs/cgroup/memory/memory.limit_in_bytes"
    if os.path.exists(cgroup_v1):
        try:
            with open(cgroup_v1, "r") as f:
                val = f.read().strip()
                limit = int(val)
                # Valores gigantescos indican sin límite
                if limit < (1 << 60):
                    return limit
        except Exception:
            pass

    return None


def get_system_profile():
    """
    Analiza el entorno y retorna un diccionario con el perfil de ejecución adecuado:
    - is_low_resource: True si está en Render o sistema con <= 1GB RAM.
    - dpi: Resolución adecuada (100 en Render para bajo uso de RAM, 160 en local).
    - max_canvas_w, max_canvas_h: Límites máximos en pulgadas del lienzo.
    - aggressive_gc: True para forzar recolección de basura y liberación de páginas OS.
    """
    override = os.environ.get("LOW_MEMORY_MODE", "").lower()
    is_render = "RENDER" in os.environ or os.environ.get("IS_RENDER", "").lower() in ["1", "true"]
    
    cgroup_limit = _detect_cgroup_memory_limit()
    
    total_ram = None
    avail_ram = None

    if psutil is not None:
        try:
            total_ram = psutil.virtual_memory().total
            avail_ram = psutil.virtual_memory().available
        except Exception:
            pass

    # Fallback sin psutil para Linux (/proc/meminfo)
    if total_ram is None and os.path.exists("/proc/meminfo"):
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        total_ram = int(line.split()[1]) * 1024
                    elif line.startswith("MemAvailable:"):
                        avail_ram = int(line.split()[1]) * 1024
        except Exception:
            pass

    # Determinar si es entorno de baja memoria
    if override in ["1", "true", "yes"]:
        is_low_resource = True
    elif override in ["0", "false", "no"]:
        is_low_resource = False
    elif is_render:
        is_low_resource = True
    elif cgroup_limit and cgroup_limit <= RESTRICTED_RAM_THRESHOLD_BYTES:
        is_low_resource = True
    elif total_ram and (total_ram <= RESTRICTED_RAM_THRESHOLD_BYTES or (avail_ram and avail_ram < (550 * 1024 * 1024))):
        is_low_resource = True
    elif total_ram is None:
        # En caso de no poder detectar la RAM (ej. contenedor minimalista), activar modo seguro
        is_low_resource = True
    else:
        is_low_resource = False

    if is_low_resource:
        return {
            "mode": "cloud_low_memory",
            "is_low_resource": True,
            "dpi": 100,
            "max_canvas_w": 25.0,
            "max_canvas_h": 14.0,
            "aggressive_gc": True,
            "render_batch_size": 1,
        }
    else:
        return {
            "mode": "local_high_performance",
            "is_low_resource": False,
            "dpi": 160,
            "max_canvas_w": 40.0,
            "max_canvas_h": 24.0,
            "aggressive_gc": False,
            "render_batch_size": 4,
        }


def cleanup_memory(force=False):
    """
    Libera memoria agresivamente:
    1. Cierra todas las figuras de Matplotlib.
    2. Ejecuta gc.collect().
    3. En Linux (Render), llama a malloc_trim(0) para devolver memoria física al SO.
    """
    try:
        import matplotlib.pyplot as plt
        plt.close('all')
    except Exception:
        pass

    gc.collect()

    # En Linux / glibc (Render / Docker), liberar arenas de memoria sin usar al kernel
    try:
        import ctypes
        libc = ctypes.CDLL("libc.so.6")
        libc.malloc_trim(0)
    except Exception:
        pass
