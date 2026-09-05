---
id: DOC-SECLOG
title: "Security Audit Log"
owner: "Edgar Edmundo Coronel Navarrete"
status: active
source_of_truth: true
tags: [security, audit, log]
---

# Security Audit Log — FARO

> Registro único de hallazgos de seguridad. Detalle con [[vault/_Templates/Security_Finding_template]].
> → [[vault/07_Security/_index]]

| SEC | Título | Severidad | Estado | Encontrado | Remediación (PR) | Verificado |
|---|---|---|---|---|---|---|
| SEC-001 | | high | open | 2026-08-01 | | ☐ |
| SEC-002 | `state` de OAuth constante (`faro`): el callback no estaba protegido contra login CSRF | high | resolved | 2026-09-02 | `state` firmado de un solo uso + cookie `HttpOnly` (US-402) | ☑ |
| SEC-003 | Rate limiting en memoria por proceso: con varias instancias el límite efectivo se multiplica | medium | accepted_risk | 2026-09-02 | Follow-up: backend compartido (Redis) o límite en el balanceador — C5 | ☐ |
| SEC-004 | JWT propios con HS256 (simétrico): quien lea el secreto puede **emitir** tokens | medium | accepted_risk | 2026-09-02 | Follow-up: migrar a RS256 con llaves en Secret Manager | ☐ |
| SEC-005 | Refresh tokens sin rotación ni revocación (vigencia 7 días) | medium | accepted_risk | 2026-09-02 | Follow-up: rotación en cada canje + lista de revocación | ☐ |
| SEC-007 | Almacen de codigos de login degrada a memoria del proceso si falta permiso de `CREATE` o la base no responde: con varias instancias el login falla de forma intermitente | medium | accepted_risk | 2026-09-03 | Degradacion deliberada (mejor un login que funciona con 1 instancia que ninguno). Verificar el permiso tras el redeploy — C5 | ☐ |
| SEC-008 | FARO Web autentica contra Superset con la credencial **admin** (`SUPERSET_ADMIN_PASSWORD`) para emitir guest tokens: la credencial mas privilegiada de Superset vive en el componente mas expuesto | medium | open | 2026-09-03 | Consecuencia de la decision de arquitectura (el front habla directo con Superset). Mitigacion: usuario de Superset con permisos minimos para emitir guest tokens, no `admin` — C5 provisiona, C2 consume | ☐ |
| SEC-009 | `at_hash` del `id_token` de Google **no se verifica**: `_verificar_id_token` pasa `options={"verify_at_hash": False}` porque `_intercambiar_code` descarta el `access_token` que Google devuelve en el mismo JSON | low | accepted_risk | 2026-09-04 | Consecuencia del fix de `BUG-046`. Sin `access_token`, jose lanza `JWTClaimsError` y **todo** login real muere con 401. Riesgo real **nulo** en *authorization code flow*: `at_hash` ata dos tokens que llegan por canales distintos (defensa del *implicit flow*), y aqui ambos llegan en el mismo cuerpo TLS del token endpoint; OIDC Core lo declara OPTIONAL en code flow. Firma RS256, `aud`, `iss` y `exp` siguen activas (`defaults.update(options)`). **Cierre:** propagar el `access_token` desde `_intercambiar_code` y quitar el `options` — Christian Ruiz (C4), post-freeze. Revisado en [[vault/07_Security/Security_Review_US402_US403_US404]] Anexo A | ☐ |
| SEC-006 | `AUTH_LECTURA_PUBLICA=true` en el entorno desplegado: la lectura no exige sesión | low | accepted_risk | 2026-09-02 | Decisión de demo; se apaga por configuración cuando el login e2e esté validado — C5 | ☐ |

## Estados
open → mitigating → resolved (o accepted_risk con firma del owner).

> `SEC-002`…`SEC-009` los levantó y firmó Christian Ruiz (dueño de `vault/07_Security/**`) en
> [[vault/07_Security/Security_Review_US402_US403_US404]] — revisión humana explícita de la regla 7
> para el cierre de US-402, US-403 y US-404. El Anexo A de ese mismo documento (2026-09-04) es la
> revisión de regla 7 sobre el parche de `BUG-046`, que C5 diagnosticó y el PO mergeó como excepción
> de propiedad sobre `src/api/security/**`; de ahí sale `SEC-009`.
