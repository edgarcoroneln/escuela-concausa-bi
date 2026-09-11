// Datos de ejemplo que reflejan los valores reales verificados en producción
// (para que el diseño se pruebe con números creíbles, no con "Lorem ipsum").
// Cuando conectemos al API real, este archivo se sustituye por llamadas fetch,
// sin tocar los componentes que lo consumen.

export const kpis = [
  { label: "Matrícula total", value: "6,704,229", hint: "Alumnado inscrito en el ciclo 2024-2025" },
  { label: "Completitud de drivers", value: "62%", hint: "3 de 6 observados en promedio" },
  { label: "Índice de riesgo promedio", value: "0.36", hint: "Promedio ponderado nacional" },
  { label: "Escuelas en riesgo alto", value: "7", hint: "Índice ≥ 0.50 (línea de alerta, DEC-019)" },
];

export const matriculaPorCiclo = [
  { ciclo: "2022-2023", matricula: 6512340 },
  { ciclo: "2023-2024", matricula: 6598110 },
  { ciclo: "2024-2025", matricula: 6704229 },
];

export const escuelasPorNivel = [
  { nombre: "Primaria", valor: 62 },
  { nombre: "Secundaria", valor: 28 },
  { nombre: "Preescolar", valor: 10 },
];

export const rankingMunicipios = [
  { municipio: "Iztapalapa", entidad: "Ciudad de México", escuelas: 545 },
  { municipio: "Ecatepec de Morelos", entidad: "México", escuelas: 575 },
  { municipio: "Guadalajara", entidad: "Jalisco", escuelas: 585 },
  { municipio: "Monterrey", entidad: "Nuevo León", escuelas: 428 },
  { municipio: "Gustavo A. Madero", entidad: "Ciudad de México", escuelas: 420 },
];

// El par demo real, verificado en vivo contra producción.
export const parDiferenciador = {
  a: {
    nombre: "Francisco I. Madero",
    cct: "15DPR0920D",
    ubicacion: "Ecatepec de Morelos, Estado de México",
    indiceRiesgo: 0.4774,
    driver: "D4",
    driverNombre: "Conectividad digital",
    recomendacion: "Ampliar conectividad y dotación de equipo de cómputo.",
  },
  b: {
    nombre: "Ricardo Flores Magón",
    cct: "15DPR2254O",
    ubicacion: "Ecatepec de Morelos, Estado de México",
    indiceRiesgo: 0.4774,
    driver: "D2",
    driverNombre: "Inseguridad del entorno",
    recomendacion: "Coordinar con seguridad pública rutas escolares seguras y entornos protegidos.",
  },
  lineaAlerta: 0.5,
};

export const driverColors = {
  D1: "#8a5cf6", // pobreza y rezago
  D2: "#e0483c", // inseguridad
  D3: "#c99a2e", // infraestructura
  D4: "#2b5aa8", // conectividad
  D5: "#1b8a72", // estrés hídrico
  D6: "#6b7280", // calidad del aire
};

export const driverNombres = {
  D1: "Pobreza y rezago",
  D2: "Inseguridad",
  D3: "Infraestructura",
  D4: "Conectividad",
  D5: "Estrés hídrico",
  D6: "Calidad del aire",
};

export const driverIcons = {
  D1: "🏘️",
  D2: "🚨",
  D3: "🏗️",
  D4: "📶",
  D5: "💧",
  D6: "🌫️",
};

// Nivel de atención por umbral -- ADR-011 (Edgar) / DEC-024, no el semáforo
// original del mockup de UX/UI. Reutiliza LINEA_DE_ALERTA (DEC-019, =0.50,
// src/api/repositorio_gold.py) y RIESGO_ESTABLE del backend: el frontend
// deriva su propio nivel directo de indice_riesgo y NO consume/reinterpreta
// gold.recomendaciones.prioridad (esa columna sigue anclada a 0.60, ver
// ADR-011). Corrige el corte anterior (Alto ≥0.65/Medio 0.50-0.64), que no
// estaba alineado con el resto del sistema.
export function nivelRiesgo(indice) {
  if (indice >= 0.5) return { label: "Alta", color: "var(--color-risk-high)" };
  if (indice >= 0.3) return { label: "Media", color: "var(--color-risk-mid)" };
  return { label: "Baja", color: "var(--color-risk-low)" };
}

// "Los 7 casos" — escuelas con índice de riesgo ≥ 0.50 (DEC-019).
// TODO: sustituir por getEscuelas({ indice_riesgo_min: 0.5 }) del API real
// (src/lib/api.js) — ese endpoint ya devuelve latitud/longitud/nivel/
// variación reales (EscuelaDetalleOut). Solo el registro 1 (Francisco I.
// Madero) está verificado en producción; el resto son placeholders creados
// para poder probar el diseño completo de las 7 tarjetas mientras llega la
// lista real desde el API.
export const escuelasEnRiesgo = [
  { cct: "15DPR0920D", nombre: "Francisco I. Madero", nivel: "Primaria", municipio: "Ecatepec", entidad: "Edomex", latitud: 19.6018, longitud: -99.0561, indice_riesgo: 0.4774, variacion: -21, driver_dominante: "D4" },
  { cct: "15DPR2254O", nombre: "Ricardo Flores Magón", nivel: "Secundaria", municipio: "Ecatepec", entidad: "Edomex", latitud: 19.605, longitud: -99.048, indice_riesgo: 0.4774, variacion: -22, driver_dominante: "D2" },
  { cct: "PLACEHOLDER-3", nombre: "Caso 3 (placeholder)", nivel: "Primaria", municipio: "Oaxaca de Juárez", entidad: "Oaxaca", latitud: 20.6597, longitud: -103.3496, indice_riesgo: 0.65, variacion: -18, driver_dominante: "D1" },
  { cct: "PLACEHOLDER-4", nombre: "Caso 4 (placeholder)", nivel: "Preescolar", municipio: "León", entidad: "Guanajuato", latitud: 25.6866, longitud: -100.3161, indice_riesgo: 0.62, variacion: -25, driver_dominante: "D3" },
  { cct: "PLACEHOLDER-5", nombre: "Caso 5 (placeholder)", nivel: "Primaria", municipio: "Tuxtla Gtz.", entidad: "Chiapas", latitud: 19.4326, longitud: -99.1332, indice_riesgo: 0.61, variacion: -20, driver_dominante: "D5" },
  { cct: "PLACEHOLDER-6", nombre: "Caso 6 (placeholder)", nivel: "Secundaria", municipio: "Hermosillo", entidad: "Sonora", latitud: 21.1619, longitud: -86.8515, indice_riesgo: 0.59, variacion: -17, driver_dominante: "D6" },
  { cct: "PLACEHOLDER-7", nombre: "Caso 7 (placeholder)", nivel: "Primaria", municipio: "Guadalajara", entidad: "Jalisco", latitud: 17.0732, longitud: -96.7266, indice_riesgo: 0.58, variacion: -19, driver_dominante: "D4" },
];

// Matriz de drivers por escuela (D1..D6). `null` = SIN_DATO (driver no
// observado para esa escuela, ver indice_completitud_drivers en
// EscuelaDetalleOut). Valores ilustrativos: los 2 primeros registros
// respetan driver_dominante real del par diferenciador; el resto son
// placeholder con un patrón de faltantes consistente con el ~62% de
// completitud promedio reportado en kpis.
export const matrizDrivers = [
  { cct: "15DPR0920D", nombre: "Francisco I. Madero", drivers: { D1: 0.31, D2: 0.28, D3: 0.35, D4: 0.71, D5: null, D6: 0.22 } },
  { cct: "15DPR2254O", nombre: "Ricardo Flores Magón", drivers: { D1: 0.29, D2: 0.68, D3: null, D4: 0.33, D5: 0.24, D6: 0.19 } },
  { cct: "PLACEHOLDER-3", nombre: "Caso 3 (placeholder)", drivers: { D1: 0.52, D2: null, D3: 0.30, D4: 0.27, D5: null, D6: 0.18 } },
  { cct: "PLACEHOLDER-4", nombre: "Caso 4 (placeholder)", drivers: { D1: null, D2: 0.33, D3: 0.61, D4: 0.29, D5: 0.21, D6: null } },
  { cct: "PLACEHOLDER-5", nombre: "Caso 5 (placeholder)", drivers: { D1: 0.26, D2: 0.31, D3: null, D4: null, D5: 0.28, D6: 0.65 } },
  { cct: "PLACEHOLDER-6", nombre: "Caso 6 (placeholder)", drivers: { D1: 0.34, D2: null, D3: null, D4: 0.30, D5: 0.62, D6: 0.20 } },
  { cct: "PLACEHOLDER-7", nombre: "Caso 7 (placeholder)", drivers: { D1: 0.58, D2: 0.27, D3: 0.32, D4: 0.25, D5: null, D6: null } },
];
