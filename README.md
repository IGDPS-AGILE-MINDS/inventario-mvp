# Inventario — MVP

Herramienta web para gestión de inventario. Ver `PLAN.md` para la arquitectura y fases.

## Stack
- Frontend: React 18 + TypeScript + Vite + Tailwind + nginx
- Backend: FastAPI + SQLModel + Alembic
- DB: PostgreSQL en Supabase (local y producción pueden compartir el mismo proyecto)

## Configurar el entorno

```bash
Copy-Item .env.example .env
```

Si `.env` ya existe, no lo sobrescribas. Reemplaza `DATABASE_URL` por la cadena PostgreSQL de Supabase en formato pooler de sesión (`5432`); usa literalmente el usuario que incluye la referencia del proyecto. No uses los marcadores de `.env.example`. Si la contraseña contiene caracteres especiales, usa la URI codificada que entrega Supabase. No subas `.env` al repositorio.

## Desarrollo local

En PowerShell, desde la raíz del repositorio, abre dos terminales.

Terminal 1 — backend:

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Terminal 2 — frontend:

```bash
cd frontend
npm ci
npm run dev
```

Abre http://localhost:5173. Vite reenvía `/api` al backend local en `http://localhost:8000`; no configures `VITE_API_URL` para este modo. El backend lee el `.env` de la raíz incluso al ejecutarlo desde `backend/`. Tanto el backend local como Render usan la Supabase indicada por `DATABASE_URL`, así que ambos ven y modifican los mismos datos.

## Levantar con Docker Compose

```bash
docker compose up --build
```

- Frontend: http://localhost:80
- API docs (Swagger): http://localhost:8000/docs
- Health: http://localhost:8000/health

Este modo usa `DATABASE_URL`; no levanta una base local y conecta a Supabase.

## Despliegue gratis: Supabase + Render + Vercel

1. **Supabase:** crea un proyecto PostgreSQL y copia la cadena de conexión de Session Pooler desde Connect. Usa el puerto `5432`; local y Render pueden usar esta URL.
2. **Render:** crea un Web Service desde `backend`, runtime Docker y Dockerfile `backend/Dockerfile`. Configura `DATABASE_URL` con la URL de Supabase y `CORS_ORIGINS` con `http://localhost:5173` más la URL final de Vercel, separadas por coma. El Dockerfile aplica `alembic upgrade head` antes de iniciar FastAPI. Health check path: `/health`.
3. **Vercel:** importa el repositorio con Root Directory `frontend`, framework Vite y build `npm run build`. Añade `VITE_API_URL` con la URL HTTPS de Render, sin `/api/v1` (por ejemplo `https://tu-api.onrender.com`), y despliega de nuevo tras cada cambio de variable.
4. Cuando Vercel asigne el dominio, añade ese origen exacto a `CORS_ORIGINS` de Render y vuelve a desplegar el backend.

El navegador llama directamente a Render desde el dominio de Vercel; no hay proxy común en producción. `VITE_API_URL` es pública y nunca debe guardar secretos. No habilites CORS con `*`. Los planes gratis pueden dormir el backend, limitar recursos o cambiar sus condiciones; una primera solicitud puede tardar y debes verificar cuotas/disponibilidad vigentes antes de la demo. La app no tiene autenticación, así que usa solo datos ficticios mientras esté expuesta públicamente.


## Tests

```bash
docker compose exec -e DATABASE_URL=sqlite:// backend pytest
```

Cubren reglas de negocio: stock (nunca negativo, agotado/reactivación), cálculo de vencimientos, configuración, CRUD de productos y filtros. Usan SQLite en memoria, sin tocar la base de datos real.

## Datos de demostración (seed)

```bash
docker compose exec backend python -m scripts.seed 1000   # 1000 productos
docker compose exec backend python -m scripts.seed 25     # solo 25
```

El seed es idempotente: reutiliza categorías/proveedores existentes y no genera SKUs duplicados. Compatible con `docker compose down -v` (limpiar y volver a poblar).
