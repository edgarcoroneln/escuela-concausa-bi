---
id: SEC-THREAT-MODEL
title: "Threat Model & Security Policy — FARO"
owner: "Luis Téllez Domínguez"
co_owners: ["Christian Ruiz"]
status: approved
version: "1.2"
traces_up: ["US-502"]
traces_down: ["SEC-HARDENING-S3", "SEC-HARDENING-S4"]
last_reviewed: "2026-09-10"
tags: [security, threat-model, cis-controls, vulnerabilities, audit]
---

# 🔒 Threat Model & Security Policy — Proyecto FARO

> **Nivel actual:** Desarrollo Local (Score CIS: 7.0/10)  
> → [[vault/07_Security/_index|Volver a Security]]

---

## 📋 Tabla de Contenidos

1. [Modelo de Amenazas](#modelo-de-amenazas)
2. [Superficie de Ataque](#superficie-de-ataque)
3. [Vulnerabilidades Conocidas](#vulnerabilidades-conocidas)
4. [Mitigaciones Implementadas](#mitigaciones-implementadas)
5. [Roadmap de Seguridad](#roadmap-de-seguridad)
6. [Reporte de Vulnerabilidades](#reporte-de-vulnerabilidades)

---

## 🎯 Modelo de Amenazas

### Actores de Amenaza

| Actor | Motivación | Capacidad | Probabilidad |
|-------|------------|-----------|--------------|
| **Desarrollador malicioso** | Exfiltrar datos de prueba | Media | Baja |
| **Atacante en red local** | Acceso no autorizado | Media | Media |
| **Malware en laptop** | Escalación de privilegios | Alta | Media |
| **Insider threat** | Sabotaje/robo de IP | Alta | Baja |

### Activos Críticos

1. **Datos de prueba** (sensibilidad: baja)
   - Fixtures anonimizados del Formato 911
   - Sin datos reales de estudiantes
   
2. **Modelos ML** (sensibilidad: media)
   - Experimentos y métricas en MLflow
   - Artifacts de modelos entrenados
   
3. **Credenciales** (sensibilidad: alta)
   - Passwords de servicios
   - Tokens de API (cuando se implementen)
   - Secret keys de aplicaciones

4. **Código fuente** (sensibilidad: media)
   - Algoritmos de ML
   - Lógica de negocio
   - Configuración de infraestructura

---

## 🌐 Superficie de Ataque

### Puertos Expuestos (localhost:*)

| Puerto | Servicio | Autenticación | Cifrado | Riesgo |
|--------|----------|---------------|---------|--------|
| 5432 | PostgreSQL | ✅ Sí (password) | ❌ No | Media |
| 8000 | FastAPI | ⚠️ Opcional | ❌ No | Media |
| 8080 | Airflow | ✅ Sí (login) | ❌ No | Media |
| 5001 | MLflow | ❌ No | ❌ No | **Alta** |
| 8088 | Superset | ✅ Sí (login) | ❌ No | Media |
| 8001 | ChromaDB | ❌ No | ❌ No | **Alta** |

### Vectores de Ataque

#### 1. Network-based
- ✅ **Mitigado:** Puertos vinculados solo a `127.0.0.1` (desde commit actual)
- ⚠️ **Riesgo residual:** Malware en host puede acceder a localhost
- 🔮 **Mitigación futura:** Nginx reverse proxy + SSL/TLS (Sprint 3)

#### 2. Credential-based
- ⚠️ **Riesgo:** Passwords en `.env` accesibles por `docker inspect`
- ⚠️ **Riesgo:** Sin rotación automática de credenciales
- 🔮 **Mitigación futura:** GCP Secret Manager (Sprint 4)

#### 3. Application-based
- ⚠️ **Riesgo:** MLflow y ChromaDB sin autenticación
- ⚠️ **Riesgo:** Sin rate limiting (vulnerable a brute force)
- 🔮 **Mitigación futura:** Auth obligatorio (Sprint 3)

#### 4. Data-based
- ✅ **Mitigado:** Solo datos de prueba (no sensibles)
- ⚠️ **Riesgo:** Volúmenes Docker sin cifrado en reposo
- 🔮 **Mitigación futura:** Cloud SQL cifrado (Sprint 4)

---

## 🐛 Vulnerabilidades Conocidas

### Críticas (1)

**V8: ChromaDB sin autenticación**
- **CWE:** CWE-306 (Missing Authentication for Critical Function)
- **CVSS:** 9.1 (Critical)
- **Impacto:** Acceso completo al vector store
- **Estado:** Aceptado para desarrollo, mitigación en Sprint 3
- **CIS Control:** 6.1, 6.8

### Altas (5)

**V1: MLflow sin autenticación**
- **CWE:** CWE-306
- **CVSS:** 7.5 (High)
- **Impacto:** Lectura/modificación de experimentos ML
- **Estado:** Aceptado para desarrollo, mitigación en Sprint 3

**V2: Credenciales de BD en texto plano**
- **CWE:** CWE-312 (Cleartext Storage of Sensitive Information)
- **CVSS:** 7.5 (High)
- **Estado:** Aceptado para desarrollo, mitigación en Sprint 4

**V4: Superset SECRET_KEY estático**
- **CWE:** CWE-798 (Use of Hard-coded Credentials)
- **CVSS:** 7.5 (High)
- **Estado:** Aceptado para desarrollo, rotación en Sprint 3

**V6: Tráfico HTTP sin cifrar**
- **CWE:** CWE-319 (Cleartext Transmission of Sensitive Information)
- **CVSS:** 7.5 (High)
- **Estado:** Aceptado para desarrollo, SSL/TLS en Sprint 3

**V10: Datos sin cifrar en reposo**
- **CWE:** CWE-311 (Missing Encryption of Sensitive Data)
- **CVSS:** 7.5 (High)
- **Estado:** Aceptado para desarrollo, CMEK en Sprint 4

### Medias (5)

- V3, V5, V7, V9, V11 (ver `docker/README-SECURITY.md` para detalles)

### Bajas (2)

- V12, V13 (logs y healthchecks)

**Total:** 13 vulnerabilidades → 7 mitigadas en Nivel 1, 6 pendientes para Sprints 3-4

---

## 🔐 Sesión del frontend de React — residual aceptado (ADR-012, 2026-09-10)

> Registrado por Christian Ruiz (C4) a petición de Luis Téllez, como parte de la decisión de
> arquitectura del frontend nuevo. **Esto es un residual aceptado, no un riesgo resuelto.**

### El riesgo que se evitó

El frontend nuevo es **estático** (Vite compilado, servido por nginx) y no tiene servidor donde
guardar el token, a diferencia del shell de Streamlit que sí lo mantenía del lado servidor
(`ADR-010`). La opción evaluada primero fue **Bearer administrado por el navegador**, y se
**descartó**: el `refresh_token` vive **7 días**, así que en `localStorage` un XSS equivale a una
semana de acceso a la cuenta — con `analista`, eso alcanza `/admin/export`. En CIS v8 bajaba el
Control 16 de ~9 a ~7 (evaluación de C5).

### Lo que se implementó

Sesión por **cookie `httpOnly`** emitida por la API a través del `proxy_pass` de nginx: mismo
origen, así que la cookie queda **host-only** del frontend y **el token nunca toca JavaScript**.
Sin construir un servicio nuevo. Detalle en `src/api/security/cookies.py`.

> No contradice `BUG-059`: allí el hallazgo fue que `.run.app` está en la **Public Suffix List** y
> la API no puede poner una cookie compartida entre subdominios. Aquí es host-only del propio
> origen, puesta por el proxy.

| Control | Estado |
|---|---|
| Token inaccesible a JavaScript (`HttpOnly`) | ✅ |
| `Secure` fuera de local | ✅ (`Settings.cookies_seguras`) |
| Refresh token acotado a `/api/v1/auth/refresh` | ✅ El navegador no lo manda en ninguna otra petición |
| Logout borra **ambas** cookies | ✅ |
| `X-Content-Type-Options`, `Referrer-Policy`, HSTS | ✅ Middleware de la API |
| `Content-Security-Policy`, `X-Frame-Options` | ✅ **nginx (C5)**, `docker/nginx-frontend.conf.template` (PR #302) — es donde contienen el XSS del chat |

### Qué modo usa cada cliente

| Cliente | Modo | Qué hace |
|---|---|---|
| **Frontend de React** (`ADR-012`) | **cookie** | `POST /api/v1/auth/exchange?sesion=cookie` con el `code_faro`; después solo `credentials: "same-origin"`; `POST /api/v1/auth/refresh` **sin cuerpo** antes de `expira_en` (el access token vive 15 min) o ante un 401; `POST /api/v1/auth/logout` para cerrar |
| Shell de Streamlit, pruebas, clientes no-navegador | legacy | Sin cambios: `TokenPair` en el cuerpo y `Authorization: Bearer` |

Para UX (`E3`): **el flujo visible no cambia** —mismo Google OAuth, mismas pantallas—; cambia dónde
vive la credencial. Los estados de sesión del front se diseñan contra este contrato: *sin sesión*
(`/auth/me` → 401 → "Inicia sesión"), *sesión activa*, *sesión por vencer* (refresco silencioso
guiado por `expira_en`) y *sesión cerrada* (logout o refresco fallido → vuelve a "Inicia sesión").

### Corrección tras la revisión del PO (PR #304)

La primera implementación tenía un hueco que el PO detectó al revisar: `/auth/refresh` aceptaba la
cookie **y devolvía el `TokenPair` en el JSON**. Como la cookie de refresco está acotada a esa ruta,
el navegador la adjunta ahí — así que **un XSS podía hacer `fetch()` contra ese endpoint y leer los
dos tokens de la respuesta**, dejando `HttpOnly` sin ningún efecto.

Corregido separando los dos modos, que ya **no se mezclan**:

| Endpoint | Modo | Cómo se elige | Cookies | Cuerpo |
|---|---|---|---|---|
| `/auth/exchange` | legacy *(default)* | sin `?sesion` | no las toca | `TokenPair` |
| `/auth/exchange` | cookie | `?sesion=cookie` | siembra | `SesionOut` — **sin JWT** |
| `/auth/refresh` | legacy | token en el **cuerpo** | no las toca | `TokenPair` |
| `/auth/refresh` | cookie | token en la **cookie** | renueva | `SesionOut` — **sin JWT** |

El modo cookie solo informa `expira_en`, que es una duración y no un secreto: permite al frontend
refrescar **antes** del vencimiento en vez de descubrirlo con un 401. Seis pruebas lo fijan,
incluida una que busca la forma `eyJ` en el texto crudo de la respuesta por si alguien anidara el
token bajo otro nombre.

### Residual: CSRF

Con sesión por cookie, un sitio de terceros puede provocar peticiones que el navegador acompaña con
la credencial. **Se contiene con `SameSite=Lax`**, que no envía la cookie en un POST cross-site; los
POST del sistema son `/agente/consulta`, `/auth/*` y `/admin/*`.

**No hay token anti-CSRF.** Se acepta para la ventana del proyecto, con el mismo criterio de
`SEC-003/004/005`. Cierre posterior: token de doble envío o `SameSite=Strict` en la cookie de
sesión, evaluando el costo en el flujo de vuelta de Google.

### Residual: XSS sigue siendo el vector principal

`HttpOnly` impide **leer** el token, no impide que un XSS **use** la sesión desde el propio
navegador. El vector concreto de esta app es **la respuesta del agente renderizada en el chat**, que
es texto libre de un LLM. Mitigación acordada con C5 y C1: **nada del chat se renderiza como HTML**
(sin `dangerouslySetInnerHTML`, `react-markdown` con HTML crudo desactivado) y **CSP en nginx**.

---

## ✅ Mitigaciones Implementadas (Nivel 1)

### M1: Documentación de riesgos
- ✅ `SECURITY.md` (este archivo)
- ✅ `docker/README-SECURITY.md`
- ✅ Comentarios en `.env`
- **CIS Control:** 5.4 (Documentation)

### M2: Reducción de superficie de ataque
- ✅ Bind de puertos solo a `127.0.0.1`
- ✅ Sin acceso desde red local
- **CIS Control:** 12.4 (Port Security)

### M3: Separación de ambientes
- ✅ Variable `ENVIRONMENT=local`
- ✅ Warnings al arrancar servicios
- **CIS Control:** 4.1 (Secure Configuration)

### M4: Gestión de credenciales
- ✅ Script de generación seguro (`scripts/generate-keys.py`)
- ✅ Política documentada (`vault/07_Security/Credentials_Policy.md`)
- ✅ Passwords de 20 caracteres
- **CIS Control:** 5.2 (Use Unique Passwords) · _(antes citaba 5.3 por error: 5.3 es "Disable Dormant Accounts")_

### M5: Control de acceso a código
- ✅ `.env` en `.gitignore`
- ✅ Pull requests obligatorios
- ✅ Sin credenciales en código
- **CIS Control:** 3.12 (Code Security)

---

## 🗺️ Roadmap de Seguridad

### Sprint 2 (Actual) — Score: 7.0/10
- [x] Documentación de amenazas
- [x] Bind localhost only
- [x] Warnings de seguridad
- [x] Política de credenciales

> **Nota (v1.0.1):** los US IDs de este roadmap se reconciliaron con el catálogo real de
> Célula 5 (US-501..505); antes usaban IDs incorrectos (US-503/504/505 cruzados y el
> fantasma US-601). La entrega vigente se rige por las **Fases** del plan de despliegue
> GCP: Fase 1 = US-504 (ya aprovisionada ✅); Fases 3-4 = US-505.

### Sprint 3 (Staging) — Score: 8.5/10
- [ ] Autenticación en MLflow — IAP delante de la UI admin (US-505, Fase 3)
- [ ] Token auth en ChromaDB — IAP delante de la UI admin (US-505, Fase 3)
- [ ] Reverse proxy / TLS en el borde: Cloud Load Balancing (HTTPS) + Cloud Armor (US-505, Fase 3/4)
- [ ] SSL/TLS gestionado por Cloud LB (certificados administrados; no self-signed en prod)
- [ ] Rate limiting (reglas Cloud Armor) (US-505, Fase 4)
- [ ] Segmentación de red: VPC + Cloud SQL IP privada + Serverless VPC Connector (US-504, Fase 1 ✅)
- [ ] Rotación de SECRET_KEYs vía Secret Manager (US-504)

### Sprint 4 (Producción) — Score: 9.5/10
- [ ] GCP Secret Manager (US-504, Fase 1 ✅)
- [ ] Cloud SQL cifrado at-rest (default) (US-504, Fase 1 ✅)
- [ ] Cloud Armor WAF (US-505, Fase 4)
- [ ] Identity-Aware Proxy (OAuth2) para UIs admin (US-505, Fase 3)
- [ ] Security Command Center (US-505)
- [ ] Cloud Logging / Audit Logs centralizado (US-504, Fase 1 ✅ — Data Access)
- [ ] Alertas de seguridad (Cloud Monitoring) (US-505)

---

## 🚨 Reporte de Vulnerabilidades

### Para el Equipo Interno

Si encuentras una vulnerabilidad de seguridad:

1. **NO la reportes en issues públicos de GitHub**
2. Contacta directamente a:
   - **Security Lead:** Christian Ruiz (Célula 4)
   - **DevOps Lead:** Luis Téllez (Célula 5)
   - **PO:** Edgar Coronel

3. Envía correo a: `security@faro.local` (interno)

4. Incluye:
   - Descripción de la vulnerabilidad
   - Pasos para reproducir
   - Impacto potencial
   - Sugerencias de mitigación (opcional)

### Tiempo de Respuesta

- **Críticas (CVSS 9.0-10.0):** 24 horas
- **Altas (CVSS 7.0-8.9):** 72 horas
- **Medias (CVSS 4.0-6.9):** 1 semana
- **Bajas (CVSS 0.1-3.9):** 1 sprint

### Divulgación Responsable

- **Embargo:** 90 días después de fix
- **Crédito:** Se reconocerá al reportero (con permiso)
- **Hall of Fame:** `SECURITY-CREDITS.md`

---

## 📚 Referencias

- [CIS Controls v8](https://www.cisecurity.org/controls)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)

---

## 📝 Change Log

| Fecha | Versión | Cambios | Autor |
|-------|---------|---------|-------|
| 2026-08-16 | 1.0 | Creación inicial, threat model, 13 vulnerabilidades documentadas | Luis Téllez |
| 2026-08-29 | 1.0.1 | Reconciliación de US IDs del roadmap con el catálogo real (US-501..505; elimina el fantasma US-601); corrige tech stale (nginx/self-signed → Cloud LB/Armor + certs administrados); corrige cita CIS 5.3→5.2 en M4 | Luis Téllez |
| TBD | 1.1 | Actualización post-Sprint 3 (auth implementado) | Christian Ruiz |
| TBD | 2.0 | Actualización post-Sprint 4 (GCP production) | Luis Téllez |

---

**Este documento es revisado cada sprint y actualizado cuando:**
- Se descubre una nueva vulnerabilidad
- Se implementa una mitigación
- Cambia el modelo de amenazas
- Se despliega a un nuevo ambiente

**Próxima revisión:** Sprint 3 kickoff (2026-08-26)
