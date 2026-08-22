---
owner: Edward Ruiz
status: done
traces_up:
  - US-523c
traces_down:
  - .github/workflows/quality_gate.yml
---

# Configuración de Quality Gate para PRs

Se implementó un flujo automatizado en GitHub Actions (`quality_gate.yml`) que se ejecuta en cada Pull Request hacia la rama `main`. 

Este gate realiza dos validaciones obligatorias:
1. **Plantilla completada:** Verifica que el cuerpo del PR no contenga casillas de verificación vacías (`[ ]`). Si detecta alguna, rechaza la validación.
2. **Vault Limpio:** Ejecuta el script `_Meta/scripts/vault_lint.py .` para asegurar que las reglas documentales del repositorio se cumplan antes de integrar el código.
