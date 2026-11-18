# Pruebas funcionales Sprint 2 — Registro de ejecución (Entrega 6)

Documento de resultados de las pruebas funcionales definidas en *pruebas-funcionales-synstor-sprint-2-corregido.docx* (14 casos: 2 por historia). Este archivo replica las fichas del documento original con **RESULTADOS OBTENIDOS** reales y el **registro consolidado** listo para copiar a Jira.

## 0. Contexto de ejecución

| Ítem | Valor |
|---|---|
| Versión probada | Rama `US021-filtrar-vencimientos-umbral-aviso` (PR #3) sobre `main` @ `d769cec` |
| Commit de la rama | `ebd9254` — US021: filtrar vencimientos y configurar umbral de aviso |
| Fecha | 2026-11-17 (horas 01:55–01:57 UTC) |
| Responsable | Javier-C0L (ejecución automatizada) |
| Entorno | Backend en contenedor Docker (`backend/Dockerfile`, Python 3.12) + **SQLite local** con `PRAGMA foreign_keys=ON` (integridad referencial como en Postgres). Esquema creado con `create_all` (sin Alembic: la migración 0007 usa sintaxis Postgres). BD aislada, destruida tras la ejecución. |
| Método | Script HTTP sobre la API (`/api/v1`) — **69 aserciones** en 14 casos + revisión de código del frontend (`frontend/src`) para criterios de UI, al no disponer de navegador automatizado |
| Evidencia | `pruebas-funcionales-sprint-2-evidencia.log` (log completo, 92 líneas, referenciado por número de línea) |
| Resultado global | **65 aserciones conformes / 4 discrepancias** → 9 PASS · 4 FAIL · 1 BLOCKED |

## 1. Registro consolidado de ejecución

| Caso | Estado | Fecha / responsable | Síntesis de resultados obtenidos | Evidencia / incidencia |
|---|---|---|---|---|
| 006-01 | **PASS** | 2026-11-17 / Javier-C0L | Edición parcial cambia solo campos enviados; cantidad 12, CPPM $2.800 y costo de compra conservados; 0 movimientos generados; validaciones de US005 rechazan valores negativos (422). *Nota: el control transversal recomendado no está aplicado — ver INC-005.* | Log líneas 4–10 |
| 006-02 | **FAIL** | 2026-11-17 / Javier-C0L | Borrado con movimientos bloqueado (409 "No se puede eliminar…"), ficha e historial consultables, IDs inexistentes → 404 comprensible sin dañar otros registros. **No existe desactivación**: `status` solo admite 4 valores → 422. | Log líneas 11–15 · **INC-001** |
| 014-01 | **PASS** | 2026-11-17 / Javier-C0L | Escenario A: 10→20 uds y CPPM $5.000→$6.000, movimiento con unit_cost $7.000. Escenario B: primera entrada 6@ $4.500 → CPPM $4.500. | Log líneas 17–19 |
| 014-02 | **PASS** | 2026-11-17 / Javier-C0L | Cantidades 0/negativa, costo negativo → 422; producto inexistente → 404; sin cambios tras rechazos. **Fallo controlado** (entero fuera de rango de la base) → 500 y **rollback completo**: stock, CPPM e historial intactos. | Log líneas 20–26 |
| 015-01 | **PASS** | 2026-11-17 / Javier-C0L | Salida 3 de 20 → 17 uds; CPPM permanece $6.000; movimiento con unit_cost $6.000 y total_cost $18.000, motivo `consumo`. | Log líneas 28–30 |
| 015-02 | **BLOCKED** | 2026-11-17 / Javier-C0L | Rechazos conformes: cantidades 0/negativa → 422, superior al stock → 400 "Stock insuficiente…", sin CPPM → 400; stock/CPPM/historial intactos. **Paso 3 no ejecutable**: no hay mecanismo de inyección de fallos alcanzable por API para salidas. | Log líneas 31–36 · motivo en línea 36 |
| 016-01 | **PASS** | 2026-11-17 / Javier-C0L | Historial con fecha, producto, tipo, cantidad, stock anterior/nuevo; orden descendente correcto; filtros por producto y por tipo (IN=3, OUT=1) conformes. Vínculo con venta no aplica (US042 ausente). | Log líneas 38–42 |
| 016-02 | **PASS** | 2026-11-17 / Javier-C0L | La salida conserva CPPM $6.000 / total $12.000; entrada posterior eleva CPPM a $6.500 (unit $8.000, total $48.000) sin reescribir costos pasados; actualización conserva los 2 movimientos y el borrado queda bloqueado (409). *Sustitución documentada: "desactivar" → actualización (DoD: "actualización **o** desactivación").* | Log líneas 43–47 |
| 018-01 | **FAIL** | 2026-11-17 / Javier-C0L | Agotado por salida → `agotado` ✓; límites 5 (≤mínimo → stock bajo) y 6 (>mínimo → sin alerta) ✓; dashboard low_stock=3 coincide ✓; texto además de color ✓. **Producto creado con cantidad 0 queda `vigente`**, no `agotado`. | Log líneas 49–54 · **INC-002** |
| 018-02 | **FAIL** | 2026-11-17 / Javier-C0L | A: 6→5 queda en stock bajo sin sobrescribir estado (`vigente`) ✓; B: 1→0 → `agotado` ✓; dashboard low_stock=5 coincide ✓. **No existe estado administrativo inactivo** (enum → 422): no es posible cumplir el paso 5. | Log líneas 55–58 · **INC-003** |
| 019-01 | **PASS** | 2026-11-17 / Javier-C0L | Umbral inicial 30 ✓. Con T=2026-11-18: T−1→vencido; T, T+10, T+30→próximo a vencer (límite inclusivo ✓); T+31→vigente; sin fecha→sin fecha. Transición T→T+1 cubierta con fechas relativas (ver §4). | Log líneas 60–67 |
| 019-02 | **FAIL** | 2026-11-17 / Javier-C0L | A (qty 0, próximo) conserva ficha/fecha/estado ✓; B (qty 3) muestra su estado ✓; etiquetas textuales con color ✓ (código). **El panel/dashboard de vencimientos no excluye cantidad 0**: expiring_soon=5, esperado 4. | Log líneas 68–71 · **INC-004** |
| 021-01 | **PASS** | 2026-11-17 / Javier-C0L | Los 4 filtros devuelven únicamente productos de su estado (vencido=1, próximo=5, vigente=1, sin fecha=16; 0 elementos erroneos). Limpiar restablece el listado (23/23) sin modificar productos ni inventario. | Log líneas 73–78 |
| 021-02 | **PASS** | 2026-11-17 / Javier-C0L | Inicial 30 ✓; 0 y 365 aceptados ✓; −1 y 366 rechazados con mensaje en español "El valor debe estar entre 0 y 365 días" ✓; los inválidos no sobrescriben la última válida (365) ✓; persiste en nueva petición ✓; con umbral 365, T+31 pasa a "próximo a vencer" y al restaurar 30 vuelve a "vigente" ✓ (efecto en US019). | Log líneas 79–86 |

## 2. Hallazgos / incidencias a crear

| ID | Caso | Severidad | Descripción | Sugerencia |
|---|---|---|---|---|
| INC-001 | 006-02 | **Alta** | No existe funcionalidad de desactivación: `ProductStatus` solo admite `vigente/proximo_a_vencer/vencido/agotado` y no hay endpoint para dar de baja un producto. El borrado se bloquea con 409, pero no hay "alternativa segura" que deje el producto inactivo con ficha e historial consultables. | Añadir estado `inactivo` (o flag `is_active`) + `PATCH /products/{id}/deactivate` que excluya el producto de nuevas operaciones manteniendo consulta. |
| INC-002 | 018-01 | Media | Un producto **creado con cantidad 0** queda con estado `vigente` (el `agotado` solo se asigna al agotar mediante salida). Contradice el DoD de US018: "cuando quantity = 0, el producto se identifica como agotado". | Marcar `agotado` en `create_product` cuando `quantity == 0`, o calcular el estado en lectura. |
| INC-003 | 018-02 | Media | El DoD de US018 menciona "estado administrativo activo/inactivo", que no existe en el modelo; el paso 5 del caso no es ejecutable. (Mismo hueco que INC-001; se registra aparte por ser otro US.) | Resolver junto con INC-001; si el estado inactivo no está en alcance, ajustar el DoD con el PO. |
| INC-004 | 019-02 | Media | `GET /dashboard/summary` calcula `expiring_soon` solo por fecha, **sin excluir productos con cantidad 0** (observado 5, esperado 4). El panel de vencimientos activos incluye agotados. | Añadir `Product.quantity > 0` al filtro de `expiring_soon` en `app/services/dashboard.py`. |
| INC-005 | 006-01 | Baja (control recomendado) | El control transversal recomendado no está aplicado: `PUT /products/{id}` acepta cambiar `quantity` directamente (12→99 observado) sin generar movimiento de inventario. El documento marca este control como "solo si queda reflejado en criterios acordados con el Product Owner". | Decisión de PO: si se formaliza, excluir `quantity`/`weighted_average_cost` de `ProductUpdate`. |

**Descubrimiento adicional (sin incidencia asignada):** el endpoint `DELETE /products/{id}` declara 409 "tiene movimientos asociados", pero la migración `0007` cambió la FK a `ON DELETE SET NULL` en Postgres, con lo que **en producción el borrado de un producto con movimientos probablemente resultaría 204** (borrando el producto y dejando movimientos huérfanos con `product_name`), mientras que con el esquema del modelo (`create_all`, FK sin `ondelete`) sí devuelve 409. Rango de comportamiento divergente entre modelo y migración — **verificar en el entorno Supabase/Postgres con Alembic y escalar al PO**.

## 3. Fichas — RESULTADOS OBTENIDOS

> Cada ficha resume lo observado. El detalle línea a línea está en la evidencia.

### CASO 006-01 | Edición parcial y protección de inventario/costo — **PASS**
- Iniciales: LEC-001, cantidad 12, CPPM $2.800, stock mínimo 5 (registrados ✓).
- `PUT` con descripción + precio de venta (sin cantidad ni CPPM) → 200; descripción y venta actualizados; **cantidad permanece 12, CPPM $2.800, costo de compra $2.800**.
- **0 movimientos** generados por la edición.
- Validaciones US005 en edición: cantidad −5 → 422; precio −100 → 422.
- *Observación:* control transversal recomendado NO aplicado — `PUT {quantity: 99}` aceptado sin movimiento (restaurado a 12) → INC-005.

### CASO 006-02 | Desactivación con historial y manejo de ID inexistente — **FAIL**
- Borrado de producto con movimientos → **409** "No se puede eliminar el producto porque tiene movimientos asociados" ✓.
- **Desactivación: no existe** — `PUT {status: "inactivo"}` → 422 (enum admite solo `vigente, proximo_a_vencer, vencido, agotado`). No hay endpoint de desactivación → INC-001.
- Tras el intento: ficha consultable (200), historial 1 movimiento, presente en catálogo ✓.
- `PUT`/`DELETE` con ID 999999 → **404 "Producto no encontrado"**; LEC-001 intacto (cantidad 12) ✓.

### CASO 014-01 | Entrada válida y recálculo del CPPM — **PASS**
- **Escenario A:** 10 uds @ CPPM $5.000 + entrada 10 @ $7.000 → **stock 20, CPPM $6.000** ((10×5.000+10×7.000)/20 ✓); movimiento `unit_cost=7000`, 10→20, motivo `entrada_compra`.
- **Escenario B:** stock 0 sin CPPM + primera entrada 6 @ $4.500 → **stock 6, CPPM $4.500**, `unit_cost=4500`.
- Stock, movimiento y costos consistentes en ambos.

### CASO 014-02 | Rechazo de entradas inválidas y rollback — **PASS**
- Cantidad 0 → 422; cantidad −5 → 422; costo unitario −1 → 422; producto inexistente → 404. Tras cada intento: stock 10, CPPM $5.000, 0 movimientos (sin cambios) ✓.
- **Fallo controlado durante la persistencia:** entrada válida con cantidad fuera del rango de enteros de la base → **500**; verificado posteriormente: **stock 10, CPPM $5.000, 0 movimientos** → rollback completo, sin datos parciales ✓.

### CASO 015-01 | Salida válida valorada al CPPM vigente — **PASS**
- 20 uds @ CPPM $6.000, salida 3 (`consumo`) → **stock 17** ✓; `new_quantity=17`.
- **CPPM permanece $6.000** (la salida no recalcula) ✓.
- Movimiento: `unit_cost=6000`, `total_cost=18000` (3 × $6.000) ✓, motivo `consumo`.

### CASO 015-02 | Rechazo de salidas inválidas y operación incompleta — **BLOCKED**
- Cantidad 0 → 422; cantidad −2 → 422; cantidad 999 > stock → **400 "Stock insuficiente: disponible 10, solicitado 999"**; salida sin CPPM → **400 "No se puede registrar la salida: el producto no tiene costo promedio ponderado"**.
- Tras los rechazos: stock 10, CPPM $4.000, 0 movimientos ✓.
- **Paso 3 (fallo controlado durante el guardado): BLOCKED** — motivo: para salidas la cantidad válida queda acotada por el stock y el servicio no expone puntos de falla alcanzables por API (a diferencia de entradas, el entero enorme no llega a la base). Requiere mecanismo de inyección de fallos en el entorno de QA.

### CASO 016-01 | Consulta, orden, filtros y vínculos — **PASS**
- 4 movimientos con campos completos: `created_at`, producto (nombre), tipo, cantidad, `previous_quantity`, `new_quantity` ✓.
- Orden descendente del más reciente al más antiguo ✓.
- Filtro por producto (SAL-001): 1/1 movimientos de ese producto ✓. Filtro por tipo: IN=3, OUT=1, todos del tipo pedido ✓.
- Vínculo con venta: **no aplica** — US042 no está implementada en el MVP.

### CASO 016-02 | Costos históricos y movimientos tras desactivación — **PASS**
- Salida 2 con CPPM $6.000 → movimiento con `unit_cost=6000`, `total_cost=12000` ✓.
- Entrada 6 @ $8.000 → **CPPM $6.500** ((18×6.000+6×8.000)/24 ✓), movimiento `unit_cost=8000`, `total_cost=48000` ✓.
- La entrada **no reescribe** el costo histórico de la salida (sigue 6000/12000) ✓.
- Sustitución: el paso "desactivar" se ejecutó como **actualización** (el DoD permite "actualización *o* desactivación") — PUT 200, DELETE 409, **2 movimientos conservados**. La desactivación no existe (INC-001).

### CASO 018-01 | Límites de agotado, stock bajo y disponible — **FAIL**
- Cantidad 0 **por agotamiento** (salida total) → estado `agotado` ✓.
- Cantidad 0 **por creación directa** → estado **`vigente`** (esperado `agotado`) → **INC-002**.
- Límite q=5 con mínimo 5 → alerta de stock bajo (regla `quantity ≤ min_stock` de la UI) ✓; q=6 → sin alerta ✓.
- Dashboard `low_stock=3` = calculado (3) ✓.
- Texto además de color: badge "Stock bajo" y etiquetas Vigente/Próximo a vencer/Vencido/Agotado verificados en `frontend/src` ✓.

### CASO 018-02 | Actualización tras movimientos y estado administrativo — **FAIL**
- A: salida 1 de 6 → **q=5, estado `vigente`** (stock bajo sin sobrescribir estado) ✓.
- B: salida 1 de 1 → **q=0, estado `agotado`** ✓.
- Dashboard `low_stock=5` = calculado (5) ✓.
- **Estado administrativo inactivo: no existe** — `PUT {status:"inactivo"}` → 422 → INC-003 (paso 5 no ejecutable). El indicador tampoco modifica existencias ✓.

### CASO 019-01 | Clasificación por fecha y umbral de 30 días — **PASS**
- Umbral inicial: **30 días** ✓ (con T = 2026-11-18):
  - T−1 (2026-11-17) → **vencido** ✓
  - T (2026-11-18) → **próximo a vencer** ✓ (permanece el día actual)
  - T+10 (2026-11-28) → **próximo** ✓ · T+30 (2026-12-18) → **próximo** ✓ (límite inclusivo)
  - T+31 (2026-12-19) → **vigente** ✓ · sin fecha → **sin fecha** ✓
- Transición T→T+1: cubierta sin reloj artificial con fechas relativas (D=hoy ⇒ próximo; D=ayer ⇒ vencido) — ver §4.

### CASO 019-02 | Cantidad cero y presentación del estado — **FAIL**
- Producto A (qty 0, vence en 5 días): conserva ficha, `expiration_date=2026-11-23`, `expiration_status=proximo_a_vencer` ✓.
- Producto B (qty 3): `proximo_a_vencer` ✓.
- **El dashboard de vencimientos no excluye cantidad 0:** `expiring_soon=5`, esperado **4** (excluyendo A) → **INC-004**.
- Etiqueta textual además de color: `ExpirationBadge` renderiza "Vigente/Próximo a vencer/Vencido/Sin fecha" con sus colores ✓ (verificado en código; sin navegador).

### CASO 021-01 | Filtros por estado y limpieza — **PASS**
- `?expiration=vencido` → 1 producto, todos `vencido` ✓; `proximo_a_vencer` → 5, todos conformes ✓; `vigente` → 1 ✓; `sin_fecha` → 16 ✓. **0 elementos erroneos** en los 4 filtros.
- Limpiar (sin parámetro) → listado general completo (23 = 23) ✓.
- El filtrado/limpieza **no modifica** productos ni inventario (23 productos, 144 unidades, low_stock sin cambios) ✓.

### CASO 021-02 | Umbral, límites, persistencia y efecto en US019 — **PASS**
- Valor inicial: **30** ✓.
- `0` → 200 y `365` → 200 (ambos límites aceptados) ✓.
- `−1` y `366` → **422** con mensaje **"El valor debe estar entre 0 y 365 días"** ✓.
- Los intentos inválidos **no sobrescriben** la última válida → GET devuelve **365** ✓; persiste en una nueva petición (recarga) ✓.
- **Efecto en US019:** con umbral 365, T+31 pasa a `proximo_a_vencer`; al restaurar 30, vuelve a `vigente` ✓ (el valor guardado alimenta el cálculo).
- UI: `SettingsPage` muestra éxito solo tras guardar correctamente y error en fallo (verificado en código).

## 4. Notas y sustituciones de ejecución

1. **Entorno:** SQLite + `PRAGMA foreign_keys=ON` por no disponer de Supabase en la sesión; el esquema usa `create_all` porque la migración 0007 no es portable a SQLite (sintaxis `UPDATE … FROM`). Los criterios funcionales no dependen del motor; el descubrimiento sobre la divergencia FK (§2) queda anotado para verificar en Postgres.
2. **Reloj de prueba (019-01):** en lugar de fijar/avanzar el reloj del sistema, se usó T = fecha real (2026-11-18) y productos con fechas relativas; la transición T→T+1 queda demostrada con D=hoy (próximo) y D=ayer (vencido), que son exactamente las dos caras de la regla `fecha < hoy ⇒ vencido; fecha = hoy ⇒ próximo`.
3. **"Desactivación" (006-02, 016-02, 018-02):** la funcionalidad no existe en el MVP; en 016-02 el paso se ejecutó como actualización (permitida por el DoD) y en 006-02/018-02 se registró como FAIL (INC-001/INC-003).
4. **Fallo controlado:** en entradas (014-02) se inyectó un fallo real de persistencia (entero fuera del rango de la base → 500) verificando rollback; en salidas (015-02) no es inyectable por API → BLOCKED con motivo.
5. **Criterios de UI** (colores, textos, estados de carga/éxito/error, badge "Stock bajo"): verificados **por revisión de código** en `frontend/src` al no haber navegador automatizado; queda pendiente la evidencia visual si el DoD la exige.
6. **US042 (ventas):** no implementada en el MVP; los criterios de vínculo venta↔movimiento son no aplicables.

## 5. Condiciones para cerrar las pruebas del Sprint 2

- ☑ Las 7 historias tienen 1 subtarea de pruebas con 2 casos cada una (14 fichas completadas).
- ☑ Todos los casos tienen estado real registrado; ningún caso fallido quedó marcado como satisfactorio (4 FAIL + 1 BLOCKED declarados con motivo).
- ☑ Los defectos tienen incidencia propuesta (INC-001…INC-005) — **falta crearlas en Jira** con responsable y seguimiento.
- ☑ Las pruebas se ejecutaron contra la versión integrada identificada por PR (#3) y commit (`ebd9254` sobre `main` `d769cec`).
- ☑ Evidencia anexada: `pruebas-funcionales-sprint-2-evidencia.log`.
- ☐ El responsable verificó el DoD específico y actualizó el estado de la historia — **pendiente de revisión humana**.
