import { useState } from "react";
import { getAuthLoginUrl } from "../lib/api.js";

// Pantalla 0 -- Login (mockup 00_Login.html, 01_UX_Architecture.md "Mockup 0
// -- Login"). Nueva 12-sep (auditoría mockups vs código, a pedido de Diana):
// hasta hoy esta SPA no tenía una pantalla de login propia -- App.jsx
// montaba el shell completo (Sidebar/Header) sin importar la sesión, y cada
// pantalla fallaba por su cuenta con "sin sesión iniciada" (el error que
// Diana venía viendo en Panorama). Ver App.jsx: ahora el layout raíz
// muestra esta pantalla completa, sin Sidebar ni Header, mientras
// session.status === "anonimo".
//
// Contenido contra el spec: "un único botón de acceso con Google, sin
// campos de usuario o contraseña... el diseño debe aprovechar ese espacio
// para identidad y narrativa, no para un formulario que no existe." El
// texto es propio de este frente, en el mismo tono llano de Home.jsx --
// NO la narrativa de "sensores/telemetría" del mockup Stitch (00_Login.html
// dice "Sistema Nacional de Observación Socioescolar", "La Escuela como
// Sensor Social", etc.): esa narrativa ya se dejó fuera de P1 por la misma
// razón (no está en el spec aprobado), y 01_UX_Architecture.md no dicta un
// texto exacto para esta pantalla, solo el objetivo.
//
// Estados: "en reposo" (por defecto) y "redirigiendo a Google" (tras el
// clic, tan real como se puede simular sin bloquear la navegación). NO hay
// estado de "credenciales inválidas" -- nota explícita del spec (hallazgo
// de Marina, `src/api/v1/auth.py`): un fallo de OAuth no vuelve por esta
// pantalla ni por un parámetro en la URL, el backend lo resuelve en el
// callback antes de redirigir aquí. `lib/session.jsx` ya trata un canje
// fallido igual que "nunca se intentó" -- no se inventa un estado de error
// que el backend no expone.
export default function Login() {
  const [redirigiendo, setRedirigiendo] = useState(false);

  function iniciarSesion(e) {
    e.preventDefault();
    setRedirigiendo(true);
    window.location.assign(getAuthLoginUrl());
  }

  return (
    <div
      className="min-h-screen flex items-center justify-center p-6"
      style={{ background: "linear-gradient(135deg, #0b1524 0%, #16283f 100%)" }}
    >
      <div className="w-full flex flex-col items-center gap-8 text-center" style={{ maxWidth: "26rem" }}>
        <div>
          <span
            className="font-mono-dato text-[11px] uppercase font-semibold tracking-wider"
            style={{ color: "var(--faro-signal-soft)" }}
          >
            FARO
          </span>
          <h1 className="text-3xl leading-tight mt-3" style={{ color: "#ffffff", fontWeight: 700 }}>
            Investigar el riesgo de abandono escolar
          </h1>
          <p className="text-sm mt-4 leading-relaxed" style={{ color: "#b7c0d1" }}>
            FARO analiza 6 líneas de evidencia por escuela en 4 entidades del país para señalar
            dónde intervenir antes de que la matrícula se pierda. Acceso reservado al equipo FARO.
          </p>
        </div>

        <button
          type="button"
          onClick={iniciarSesion}
          disabled={redirigiendo}
          className="inline-flex items-center justify-center gap-2.5 text-sm font-semibold px-6 py-3.5 rounded-full w-full"
          style={{ background: "#ffffff", color: "#0b1524", opacity: redirigiendo ? 0.7 : 1 }}
        >
          {redirigiendo ? (
            "Conectando con Google…"
          ) : (
            <>
              <GoogleIcon />
              Iniciar sesión con Google
            </>
          )}
        </button>

        <p className="text-xs" style={{ color: "#6b7a94" }}>
          Al continuar, Google comparte tu nombre y correo con FARO para verificar tu acceso.
        </p>
      </div>
    </div>
  );
}

// Icono oficial "G" de Google (guía de marca de Google para botones de
// inicio de sesión) -- no un logo inventado ni el de otra plataforma.
function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true" focusable="false">
      <path
        fill="#4285F4"
        d="M17.64 9.2c0-.64-.06-1.25-.16-1.84H9v3.48h4.84a4.14 4.14 0 0 1-1.8 2.71v2.26h2.92c1.71-1.57 2.68-3.88 2.68-6.61z"
      />
      <path
        fill="#34A853"
        d="M9 18c2.43 0 4.47-.8 5.96-2.18l-2.92-2.26c-.81.54-1.84.86-3.04.86-2.34 0-4.32-1.58-5.03-3.7H.96v2.33A9 9 0 0 0 9 18z"
      />
      <path
        fill="#FBBC05"
        d="M3.97 10.72A5.4 5.4 0 0 1 3.68 9c0-.6.1-1.18.28-1.72V4.95H.96A9 9 0 0 0 0 9c0 1.45.35 2.83.96 4.05l3.01-2.33z"
      />
      <path
        fill="#EA4335"
        d="M9 3.58c1.32 0 2.51.45 3.44 1.35l2.59-2.59C13.46.89 11.43 0 9 0A9 9 0 0 0 .96 4.95l3.01 2.33C4.68 5.16 6.66 3.58 9 3.58z"
      />
    </svg>
  );
}
