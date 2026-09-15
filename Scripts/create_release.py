# -*- coding: utf-8 -*-
"""
Script Utilitario para Crear y Publicar Releases en GitHub.
Uso:
    python scripts/create_release.py
    python scripts/create_release.py v1.1
Calcula automáticamente la siguiente versión dinámica y la publica como Release/Tag en el repositorio.
"""

import sys
import os
import subprocess

# Asegurar importación del paquete core
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.version import get_version_info

def main():
    auto_ver, last_updated = get_version_info()
    target_tag = sys.argv[1] if len(sys.argv) > 1 else auto_ver

    if not target_tag.startswith("v"):
        target_tag = f"v{target_tag}"

    print("=" * 60)
    print(f"PUBLICADOR DE RELEASES - Logic Analysis")
    print(f"Versión dinámica calculada: {auto_ver}")
    print(f"Tag objetivo a publicar:    {target_tag}")
    print(f"Última actualización:       {last_updated}")
    print("=" * 60)

    # Verificar si el tag ya existe localmente
    existing_tags = subprocess.check_output(["git", "tag"]).decode().split()
    if target_tag in existing_tags:
        print(f"[!] El tag '{target_tag}' ya existe localmente.")
        resp = input("¿Deseas sobreescribirlo y republicarlo? (s/n): ").strip().lower()
        if resp != 's':
            print("Operación cancelada.")
            return
        subprocess.run(["git", "tag", "-d", target_tag], check=True)

    # Crear tag anotado
    msg = f"Release {target_tag} - Reductor Booleano y Síntesis de Circuitos de 2 Entradas"
    print(f"\n[+] Creando tag local: {target_tag}...")
    subprocess.run(["git", "tag", "-a", target_tag, "-m", msg], check=True)

    # Pushear tag a GitHub
    print(f"[+] Enviando tag a origin ({target_tag})...")
    res = subprocess.run(["git", "push", "origin", target_tag])

    if res.returncode == 0:
        print(f"\n[✓] ¡Release {target_tag} publicada con éxito en GitHub!")
        print(f"    URL: https://github.com/igream/Logic-analysis/releases/tag/{target_tag}")
    else:
        print(f"\n[✗] Error al enviar el tag a GitHub. Revisa tu conexión o permisos.")

if __name__ == "__main__":
    main()
