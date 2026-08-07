# FARO Web (frontend Streamlit)

Capa web integrada del proyecto. Diseño: `03_Architecture/Frontend_Architecture.md` · Decisión:
`03_Architecture/ADRs/ADR-002-frontend-streamlit.md`.

## Estructura (andamiaje)
- `app.py` — entrada, router y sesión.
- `auth.py` — login/logout con el OAuth2/JWT de la API y `require_role()`.
- `pages/` — Dashboards (Superset embebido), Panel de ML, Chat del agente.

## Correr en local (cuando esté implementado)
```bash
pip install -r requirements/celula-2.txt   # incluye streamlit
streamlit run src/frontend/app.py
```

> Estado: **andamiaje**. Las historias US-206, US-207 (C2), US-405 (C4) y US-305 (C3) implementan la lógica.
