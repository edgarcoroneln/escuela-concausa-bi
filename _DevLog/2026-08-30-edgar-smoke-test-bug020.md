---
project: "FARO"
date: "2026-08-30"
author_human: "Edgar Edmundo Coronel Navarrete"
agent: "Claude Code"
model: "Sonnet 5"
session_duration: "corta — diagnóstico de causa raíz de BUG-020 y guion de prueba por etapas"
touches: ["BUG-020", "US-411", "US-412", "US-504", "US-501", "REQ-004", "REQ-005"]
tags: [devlog, devops, qa, bug, cloud-run]
---

# DevLog — 2026-08-30 — Causa raíz de BUG-020 y guion de prueba por etapas

→ [[_DevLog/_index|Volver al índice]] · [[06_Quality_Testing/Bug_Register]] ·
[[08_CICD_DevOps/Cloud_Run_Deploy]]

## La causa raíz, confirmada leyendo el código

BUG-020 llevaba tres días descrito por su síntoma. La causa está en el comando de despliegue:

```
gcloud run deploy faro-api ... --set-env-vars="ENVIRONMENT=production"
```

**Esa es toda la configuración que recibe el servicio.** Ninguna variable de base de datos. En
`src/api/config.py` los valores por defecto son `postgres_host: str = "localhost"` y
`postgres_password: str = ""`, así que dentro del contenedor de Cloud Run la API intenta abrir
sesión contra un Postgres en `localhost` que no existe.

Eso explica los dos síntomas a la vez, sin necesidad de más hipótesis:

- `/api/v1/health` responde **200** porque no toca la base.
- Toda ruta de datos responde **500** al construir el engine.
- Y con token, sin token o con token inválido da **siempre 500 y nunca 401**, porque la dependencia
  de sesión revienta **antes** de que se evalúe la autenticación.

No es el RBAC de Célula 4. Es configuración de despliegue de Célula 5.

## El guion de prueba

`08_CICD_DevOps/scripts/smoke-test-bug020.sh`, con cuatro etapas ordenadas de modo que **cada fallo
apunte a una causa distinta**:

| Etapa | Qué verifica | Si falla |
|---|---|---|
| 1 | `/api/v1/health` → 200 | El contenedor no sirve |
| 2 | Una ruta de datos deja de dar 500 | No hay sesión de base de datos |
| 3 | Esa ruta devuelve filas | Gold está vacío en Cloud SQL |
| 4 | Sin token da 401, no 500 | Revienta antes de validar auth |

El orden importa: **un 500 en la etapa 2 y un 500 en la etapa 4 tienen causas opuestas.** Sin esa
distinción, el diagnóstico vuelve a empezar de cero cada vez.

## Línea base capturada antes de tocar nada

```
Etapa 1 ✅ /api/v1/health → 200
Etapa 2 ❌ /api/v1/escuelas → 500
Etapa 3 ⚠️ omitida
Etapa 4 ❌ /api/v1/predicciones/{cct} → 500 sin token
exit code: 2
```

Tenerla registrada importa porque cuando la Fase 2 se despliegue, la diferencia entre «antes» y
«después» será evidencia, no impresión.

## Lo que el guion dejó a la vista y no estaba en el plan

**La Fase 2 tiene dos mitades, no una.** Conectar Cloud Run a Cloud SQL resuelve la etapa 2, pero la
base `faro` se creó vacía: no tiene esquema `gold` ni tablas. Con la conexión funcionando, las rutas
pasarían de 500 a responder sin filas, o a fallar con «relation gold.dim_escuela does not exist».

Por eso la etapa 3 existe por separado. Cargar Gold en Cloud SQL —correr dbt contra la instancia o
restaurar un dump desde el ambiente donde ya está materializado— es trabajo que nadie tiene asignado
y que no aparece en la descripción de la Fase 2.

## Nota de acceso

Al intentar verificar los recursos de la Fase 1 con `gcloud describe`, el proyecto
`faro-escuela-sensor` respondió `PERMISSION_DENIED` para la cuenta del PM. El proyecto es de Célula 5,
así que **el despliegue de la Fase 2 lo tiene que ejecutar Luis Téllez**; el PM puede verificar el
resultado desde fuera con este guion, que solo necesita la URL pública.

## Uso de IA

Claude Code leyó `config.py`, `db.py` y el script de despliegue para localizar la causa raíz,
escribió el guion de prueba y capturó la línea base contra la URL pública. Verifiqué la salida del
guion antes de registrarla como evidencia en BUG-020.

## Pendiente

- Fase 2: redesplegar Cloud Run con connector, service account, variables y secretos (Luis).
- Cargar `gold.*` en Cloud SQL — sin dueño asignado.
- Reejecutar el guion y adjuntar el «después» a BUG-020.
