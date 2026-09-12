---
id: DOC-DEVLOG-2026-09-12-diana-alvarez-pantalla-login-p0
title: "Pantalla 0 (Login) construida -- primer hueco real cerrado de la auditoría mockups vs código"
owner: Diana Aracely Alvarez Varela
status: done
fecha: 2026-09-12
---

# Pantalla 0 (Login) construida

Primer hueco de la auditoría de esta misma fecha que Diana pidió cerrar de inmediato, para poder
verlo en su localhost: hasta esta entrega la SPA no tenía una pantalla de login propia. `App.jsx`
montaba el shell completo (`Sidebar`/`Header`) sin importar la sesión, y cada pantalla fallaba por su
cuenta con "sin sesión iniciada" -- el error que Diana venía reportando en Panorama.

## Qué cambia

- `pages/Login.jsx` (nueva): pantalla completa, sin `Sidebar`/`Header`, contra la ficha "Mockup 0 --
  Login" de `01_UX_Architecture.md` -- un único botón "Iniciar sesión con Google"
  (`getAuthLoginUrl()`, ya existente de `US-405`/`ADR-012`, sin tocar), sin campos de usuario ni
  contraseña. Estado "redirigiendo" real tras el clic (no bloquea la navegación, solo la retrasa un
  tick para que se vea antes de salir a Google). Sin estado de "credenciales inválidas": el spec deja
  explícito que un fallo de OAuth no vuelve por aquí, lo resuelve el backend en el callback
  (`src/api/v1/auth.py`).
- Copy propia de este frente, en el mismo tono llano de `Home.jsx` -- **no** se copió la narrativa de
  "sensores/telemetría" del mockup Stitch (`00_Login.html`: "Sistema Nacional de Observación
  Socioescolar", "La Escuela como Sensor Social"). Mismo criterio ya aplicado a P1: esa narrativa no
  está en el spec aprobado, y la ficha de Mockup 0 solo pide "identidad y narrativa", sin dictar texto.
- `App.jsx`: el layout raíz ahora hace la compuerta -- `session.status === "anonimo"` muestra
  `Login.jsx` a pantalla completa; `"loading"` no muestra nada (evita parpadeo Login/shell mientras
  resuelve `GET /auth/me`); `"autenticado"` sigue mostrando el shell de siempre, sin cambio.
- **Guarda explícita para no romper el modo demo:** `session.jsx` sigue llamando a `GET /auth/me` sin
  importar `VITE_USE_MOCK`, así que sin backend real ese request falla y el status queda en
  "anonimo" -- sin excepción, la compuerta nueva mostraría Login.jsx en modo demo también, rompiendo
  "Solo quiero previsualizar sin logearme" (construido hoy mismo, más temprano). La compuerta ahora
  se salta por completo si `isDemoMode()` es `true`.

## Verificado antes de tocar el flujo real

`getAuthLoginUrl()` **no** se tocó para intentar volver a la URL exacta solicitada (que el spec sí
menciona: "o a la URL solicitada si venía de un enlace directo a P4/P6") -- `src/api/v1/auth.py`
valida el parámetro `redirect` por **coincidencia exacta** contra `FRONTEND_REDIRECT_URIS`
(`_validar_redirect`, comentario explícito: "un `startswith` deja pasar
`https://faro.example.com.evil.tld`"). Agregar el `pathname` actual al `redirect` habría hecho que
la comparación exacta fallara y el login se rechazara con 400 -- se verificó el código del backend
antes de tocar nada y se descartó ese cambio. Preservar el deep-link a través del *round trip* de
OAuth necesitaría un parámetro nuevo y separado en el backend (`return_path`, validado con otra
regla), fuera de alcance de este frente.

## Pendiente, no resuelto en este commit

- `Sidebar.jsx`/`Header.jsx` conservan sus ramas para `status === "loading"`/`"anonimo"` (el panel de
  sesión y el botón "Iniciar sesión" del Header) -- con la compuerta nueva en `App.jsx`, ambos
  componentes solo se montan ya con `"autenticado"`, así que esas ramas quedan sin usar. Se dejaron
  como código defensivo en vez de removerlas en esta misma entrega (menor riesgo sin poder correr el
  build aquí) -- limpieza menor para una iteración posterior, no bloquea nada.
- Deep-link a través del login real (ver arriba) sigue sin resolver -- hoy cualquier acceso
  autenticado vuelve siempre al origen, no a la ruta original.

Sin `vault_lint` corrido (cambios solo en `frontend/src`).
