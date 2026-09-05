---
id: DOC-US521B-AMBIENTE
title: "Guía de ambiente local reproducible — Airflow y jobs ML (US-521b)"
owner: "Edgar Ulises Jiménez López"
status: approved
version: "1.0"
traces_up: ["vault/12_Roadmap_Sprints/Sprints/5-edgar-ulises-jimenez-lopez.md"]
traces_down: []
tags: [devops, local-env, airflow, mlflow, US-521b]
---

# US-521b — Guía de ambiente local: Airflow y jobs ML

Esta guía documenta cómo reproducir el ambiente local de desarrollo para **Airflow** (orquestación de DAGs) y **MLflow** (tracking de experimentos) — componentes de **Célula 5 (Cloud & DevOps)** del proyecto FARO.

> **Última verificación:** 2026-09-04 · Todos los servicios Healthy en Mac

---

## 1. Requisitos previos

- **Python 3.11+** — verificar: `python3 --version`
- **Docker Desktop** ejecutándose
- **Git** configurado: `git config --global user.name "Tu Nombre"` y `git config --global user.email "tu@email.com"`
- **Virtualenv** (se crea en esta guía)

---

## 2. Clonar y preparar el ambiente

```bash
# 1. Clona el repositorio (si aún no lo hiciste)
git clone https://github.com/edgarcoroneln/escuela-concausa-bi.git
cd escuela-concausa-bi

# 2. Crea ambiente virtual (SOLO la primera vez)
python3 -m venv .venv

# 3. Actívalo (cada vez que abres terminal)
source .venv/bin/activate                    # macOS / Linux
# .venv\Scripts\Activate.ps1                 # Windows PowerShell

# 4. Verifica que está activo (debe ver (.venv) en el prompt)
which python

# 5. Actualiza pip
pip install --upgrade pip

# 6. Instala dependencias del proyecto
pip install -r requirements.txt

# 7. Instala dependencias extras de DevOps (Célula 5)
pip install docker-compose python-dotenv google-cloud-storage