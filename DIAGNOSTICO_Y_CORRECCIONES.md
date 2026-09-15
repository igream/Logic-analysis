# Diagnóstico Técnico y Auditoría de Correcciones

**Proyecto:** Logic Analysis (Reductor Booleano y Síntesis de Circuitos)  
**Entorno de Producción:** Render (Límite: 512 MB RAM)  
**Fecha de Revisión:** 15 de septiembre de 2026  
**Estado:** Documento de contraste y planificación. *Solo análisis y directrices; sin cambios en código aún.*

---

## 1. Matriz de Contraste y Clasificación

Se contrastaron los 10 puntos propuestos por la IA externa con el estado real del repositorio, los requerimientos explícitos del usuario y las restricciones del servidor Render (512 MB).

| ID | Módulo / Área | Severidad | Diagnóstico Original | Contraste / Validación Real | Acción Definitiva |
|---|---|---|---|---|---|
| **ERR-01** | `main.py` | **Alta** | Diagramas NAND DAG se guardan en AND/OR/NOT | **REAL Y CRÍTICO:** Falta en `folder_routing` de `main.py`. | **SÍ REALIZAR:** Mapear `sop_nand_dag` y `pos_nand_dag` a `dir_nand`. |
| **ERR-02** | `main.py`, `funcion.txt` | **Media** | Rotulación de minitérminos como $f'$ en vez de $f$ | **REAL:** Inconsistencia de texto en consola (`main.py`). `core/boolean_logic.py` calcula $f$ para ambos ($SOP \equiv POS \equiv f$). | **SÍ REALIZAR:** Estandarizar impresiones de consola a $f$. |
| **ERR-03** | `core/dag_drawer.py` | **Alta (Lógica)** | Cláusulas POS unitarias conectan el riel invertido | **REAL Y CRÍTICO:** En `_render_structured_circuit`, los literales de POS se invierten para NAND, pero en cláusulas unitarias no hay compuerta y debe ir directo. | **SÍ REALIZAR:** Conectar riel directo cuando `len(t) == 1` en POS. |
| **ERR-04** | `app.py` | **Media** | Concurrencia por archivo global `current_state.json` | **PARCHE NECESARIO CON MATICES:** El estado en disco permite el lazy-loading en Render (512 MB). Pero un archivo único sufre si hay colisión. | **MODIFICAR:** Mantener lazy-loading pero parametrizar por hash o query string, sin romper el límite de RAM. |
| **ERR-05** | `app.py`, `core/parser.py` | **Media** | Sin filtrado de índices $\ge 2^{\text{num\_bits}}$ ni validación | **REAL:** Si el usuario reduce bits en la UI, quedan índices residuales fuera de rango. | **SÍ REALIZAR:** Sanitizar listas con $0 \le i < 2^n$ y validar solapamientos. |
| **ERR-06** | Raíz / `app.py` | **Baja (Limpieza)** | Archivos residuales de Hugging Face (`huggingface.yaml`, `spaces`) | **REAL (Código muerto):** Restos de pruebas pasadas; el despliegue es exclusivamente en Render. | **SÍ REALIZAR:** Purgar `huggingface.yaml` y el decorador `spaces.GPU`. |
| **ERR-07** | Git / `.gitignore` | **Crítica (Riesgo)** | Remover `.png` de Git (`git rm --cached static/generated/*.png`) | **PELIGROSO / PARCIALMENTE INCORRECTO:** Si se borran del repo, Render iniciará en frío con **404 Not Found** en la carga inicial o sufrirá OOM al arrancar. | **NO BORRAR BASE:** Mantener las imágenes del ejemplo por defecto de 4 bits. Ignorar únicamente archivos de sesión o `Resultados/`. |
| **ERR-08** | `core/version.py` | **Informativa** | Versión no cumple SemVer por saltar a 2.0 tras 1.9 | **FALSO POSITIVO (Requerimiento del usuario):** El usuario solicitó explícitamente: *"cuando llegue a la 1.9, iniciar en 2.x y así"*. | **NO CAMBIAR:** Respetar la regla de negocio solicitada por el usuario. |
| **ERR-09** | `Scripts/` | **Baja** | Scripts viejos no consumen `core/` | **REAL PERO NO BLOQUEANTE:** Son scripts históricos de versiones previas. | **OPCIONAL:** Mover a `Scripts/legacy/` o archivar sin afectar la app. |
| **ERR-10** | Pruebas / CI | **Media** | No hay tests formales automatizados (`pytest`) | **DESEABLE:** Agilizaría verificar que no haya regresiones lógicas. | **SÍ REALIZAR:** Crear suite ligera con `pytest` para equivalencia $SOP \equiv POS$ y 2 entradas. |

---

## 2. Detalle de Análisis: ¿Qué es Parche, qué es Error y qué es Requerimiento?

### ERR-01: Enrutamiento en `main.py`
* **Diagnóstico:** En `main.py`, `folder_routing.get(diag_id, dir_and_or)` envía los diagramas no listados a `Resultados/02_Diagramas_AND_OR_NOT/`. Al crearse recientemente `sop_nand_dag` y `pos_nand_dag`, no fueron añadidos al diccionario.
* **Veredicto:** **Error de integración real.** Debe corregirse para que la CLI guarde los esquemáticos DAG en `Resultados/03_Diagramas_NAND/`.

### ERR-02: Nomenclatura $f$ vs $f'$ en `main.py` y `funcion.txt`
* **Diagnóstico:** En el motor matemático [`core/boolean_logic.py`](file:///c:/Users/Admin/Documents/VS%20Code/Reductor/core/boolean_logic.py):
  - Las salidas en 1 generan la Suma de Productos de $f$.
  - Las salidas en 0 generan el Producto de Sumas de $f$.
  - La verificación formal comprueba: $SOP(f) \equiv POS(f) \equiv f$.
  En `main.py`, sin embargo, se imprimió erróneamente `f' = ...` para la Suma de Productos, contradiciendo la web, los K-maps y los títulos de los esquemáticos (que correctamente dicen $f$).
* **Veredicto:** **Inconsistencia cosmética real.** Corregir las cadenas de texto impresas en consola.

### ERR-03: Conexión de riel en cláusulas POS unitarias en `core/dag_drawer.py`
* **Diagnóstico:** En síntesis POS con compuertas NAND, una suma se expresa como $(A+B) = \text{NAND}(A', B')$, por lo que los literales entran invertidos a la compuerta. Sin embargo, si una cláusula tiene un solo literal (ej. término aislado $(A)$), este no atraviesa ninguna compuerta NAND; su valor directo es $A$. El código actual en `core/dag_drawer.py` invertía el literal indiscriminadamente antes de evaluar la longitud, conectando el riel $A'$ en lugar de $A$.
* **Veredicto:** **Bug lógico crítico en el motor de dibujo estructurado.** Debe condicionarse la inversión de literales únicamente a cláusulas con $\ge 2$ literales, o corregir la selección de riel cuando `len(t) == 1`.

### ERR-04: Concurrencia y estado en disco (`app.py`)
* **Diagnóstico:** La otra IA lo categorizó como mala práctica de arquitectura.
* **Contexto Real (El por qué del parche):** En Render solo se cuenta con **512 MB de RAM**. Generar los 12 esquemáticos simultáneamente agota la memoria del contenedor y dispara el OOM killer de Linux. Por ello, se implementó generación *bajo demanda* (lazy-loading por diagrama). El archivo `current_state.json` guarda la última función para permitir que el frontend pida solo la imagen que el usuario va a ver.
* **Veredicto:** **Es un parche indispensable por recursos, pero mejorable.** 
  - *Lo que NO se debe hacer:* Volver a generar todo en memoria de golpe (causará OOM crash en Render).
  - *Lo que SÍ se debe hacer:* Pasar el estado o un identificador ligero (hash de variables + ceros) como parámetro de consulta o token en la URL (`/api/diagram/<id>?hash=...`), de modo que múltiples usuarios no sobreescriban el mismo estado global.

### ERR-05: Sanitización de índices fuera de rango
* **Diagnóstico:** Si en la tabla de verdad el usuario cambia de 4 a 2 variables pero la lista enviada conserva ceros con valores $> 3$, estos índices se evalúan en la lógica de bits produciendo expresiones corruptas.
* **Veredicto:** **Vulnerabilidad de validación real.** Requiere filtrado estricto `0 <= idx < (2 ** num_bits)`.

### ERR-06: Residuos de Hugging Face
* **Diagnóstico:** `huggingface.yaml` y la importación de `@spaces.GPU` en `app.py` son restos de un intento previo de despliegue en HF Spaces antes de optimizar para Render.
* **Veredicto:** **Código muerto confirmado.** Limpiar de forma segura.

### ERR-07: Manejo de binarios `.png` en Git
* **Diagnóstico:** La otra IA propuso ejecutar `git rm -r --cached static/generated/*.png` e ignorar todo.
* **Contraste Crítico (¡Cuidado con romper producción!):**
  - Si se eliminan las imágenes por defecto del repositorio, cuando Render clone el proyecto y levante la aplicación, la carpeta `static/generated/` estará vacía.
  - Al abrir la página principal por primera vez, **todos los diagramas aparecerán como enlaces rotos (error 404)**.
  - Generar los 12 diagramas en el momento en que el servidor arranca retrasará el despliegue y arriesgará superar los 512 MB en el arranque.
* **Veredicto:** **Propuesta de la otra IA rechazada / reformulada.** 
  - Los diagramas de la función por defecto (4 bits) deben mantenerse commiteados como caché estático inicial de producción.
  - Solo se deben ignorar los subdirectorios temporales de usuario, archivos `.zip` y la carpeta `Resultados/`.

### ERR-08: Esquema de versiones en `core/version.py`
* **Diagnóstico:** La otra IA señaló que incrementar la versión mayor cada 10 commits (`total_offset // 10`) viola Semantic Versioning y propuso cambiarlo a `v1.0.X`.
* **Contraste Crítico (Requerimiento Explícito del Usuario):**
  - En la conversación previa (Requerimiento 5), el usuario indicó explícitamente:
    > *"Agrega en el index principal que versión es esta (iniciaremos diciendo que esta es v1.0) y la fecha de actualización, que esto se maneje de manera dinámica automáticamente, para no modificarlo en cada corrección, cuando llegue a la 1.9, iniciar en 2.x y así."*
* **Veredicto:** **FALSO POSITIVO de la otra IA.** No se debe alterar la fórmula de incremento $1.0 \to 1.9 \to 2.0$ porque fue una instrucción directa y deliberada del usuario.

### ERR-09 y ERR-10: Scripts heredados y Pruebas Unitarias
* **Diagnóstico:** Reorganización y testing automatizado.
* **Veredicto:** Válidos pero secundarios. La prioridad inmediata son los errores de trazado esquemático (ERR-03) y enrutamiento (ERR-01).

---

## 3. Plan de Acción Técnico Filtrado

Una vez aprobado por el usuario, este es el orden de ejecución correcto:

```mermaid
graph TD
    subgraph "Bloque 1: Correcciones Lógicas Inmediatas"
        B1["ERR-03: Corregir selección de riel directo para cláusulas POS unitarias en core/dag_drawer.py"]
        B2["ERR-01: Corregir folder_routing en main.py para incluir sop_nand_dag y pos_nand_dag"]
        B3["ERR-02: Corregir impresiones en consola de main.py (f' -> f)"]
    end

    subgraph "Bloque 2: Sanitización y Limpieza"
        B4["ERR-05: Sanitizar índices en app.py y core/parser.py asegurando 0 <= z < 2^n"]
        B5["ERR-06: Eliminar huggingface.yaml e imports no utilizados de spaces en app.py"]
    end

    subgraph "Bloque 3: Concurrencia Robusta en Render (Sin Aumentar RAM)"
        B6["ERR-04: Parametrizar API de diagramas con hash de función para evitar colisiones"]
    end

    subgraph "Reglas Descartadas / Preservadas"
        D1["ERR-07: PRESERVAR imágenes base en static/generated/ para evitar 404 en Render"]
        D2["ERR-08: PRESERVAR dinámica v1.0-v1.9-v2.0 solicitada por el usuario"]
    end

    Bloque 1 --> Bloque 2 --> Bloque 3
```

---

## 4. Próximo Paso

Esperar la confirmación del usuario antes de aplicar cualquiera de las modificaciones de código en los archivos correspondientes.
