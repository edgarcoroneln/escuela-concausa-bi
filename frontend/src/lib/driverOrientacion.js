// Drivers cuyo valor crudo mide "lo bueno" (buena conectividad/infraestructura
// presente) y por eso hay que invertirlos (1 - valor) para leerlos en la misma
// escala de presión/severidad que los demás (alto = más presión, igual que D1,
// D2, D5, D6).
//
// Fuente de verdad del criterio: dbt/models/gold/features_escuela.sql:388-410
// (CTE con_driver_dominante) -- el backend YA invierte D3/D4 así para elegir
// driver_dominante, pero publica el valor crudo (d3_infraestructura,
// d4_conectividad) a propósito: es el frontend quien debe invertir para
// MOSTRAR, nunca para el argmax (eso ya viene resuelto en driver_dominante).
//
// FIX (2026-09-13, Diana/US-651 -- hallazgo de Marina García + su IA): esta
// constante y su conversión vivían solo en Explorador.jsx y
// ExpedienteEscuela.jsx. Panorama.jsx, Conclusion.jsx y LosSieteCasos.jsx no la
// aplicaban: una escuela con D4 = 1.00 (conectividad completa, el mejor caso)
// se pintaba como presión máxima. Única definición ahora, mismo espíritu que
// lib/cortesAtencion.js.
export const ORIENTADOS = ["D3", "D4"];

export function estaOrientado(code) {
  return ORIENTADOS.includes(code);
}

// raw puede ser null/undefined (SIN_DATO): se regresa tal cual, nunca se
// inventa un valor ni se convierte un hueco en 0.
export function valorOrientado(code, raw) {
  if (raw === null || raw === undefined) return raw;
  return estaOrientado(code) ? 1 - raw : raw;
}

// Conveniencia para objetos { D1: raw, ..., D6: raw } -> { D1: valor, ... }
// con D3/D4 ya orientados y el resto sin tocar.
export function driversOrientados(rawPorCodigo) {
  const salida = {};
  for (const [code, raw] of Object.entries(rawPorCodigo)) {
    salida[code] = valorOrientado(code, raw);
  }
  return salida;
}
