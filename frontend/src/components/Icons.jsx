// Iconos -- copias exactas de los glifos de Material Symbols Outlined que
// usan las plantillas de Stitch (peso 400, variante "outlined"; fuente:
// paquete oficial @material-symbols/svg-400 de Google, licencia Apache
// 2.0 -- mismo set que Google Fonts sirve como "Material Symbols
// Outlined", solo que aqui van auto-hospedados como SVG en vez de
// depender de la fuente de iconos vía Google Fonts, que el CSP de
// nginx-unprivileged en produccion bloquea (mismo motivo por el que
// Inter/Space Grotesk/JetBrains Mono ya se sirven via @fontsource -- ver
// cabecera de index.css). `fill="currentColor"` en cada uno para que
// hereden el color de texto del elemento que los contiene, igual que la
// fuente de iconos original.
//
// Excepcion: `security_update_good` no existe en el set actual de
// Material Symbols (Google lo retiro/renombro ahi) -- se usa el mismo
// glifo del set clasico "Material Icons" (paquete
// @material-design-icons/svg, variante "outlined", tambien Apache 2.0),
// visualmente equivalente y del mismo peso de trazo.
function SymbolIcon({ size = 20, viewBox = "0 -960 960 960", path, ...props }) {
  return (
    <svg width={size} height={size} viewBox={viewBox} fill="currentColor" aria-hidden="true" focusable="false" {...props}>
      <path d={path} />
    </svg>
  );
}

export function IconHelpCenter(props) {
  return (
    <SymbolIcon
      path="M504-257.03q11-11.03 11-27T503.97-311q-11.03-11-27-11T450-310.97q-11 11.03-11 27T450.03-257q11.03 11 27 11T504-257.03ZM444-394h57q0-31 10-50.5t34.72-44.22Q579-522 592-547.5t13-53.5q0-53-34-84t-91.52-31q-51.87 0-88.17 24.5Q355-667 338-624l53 22q14-28 36.2-42.5Q449.4-659 479-659q32 0 50.5 16t18.5 44.1q0 19.9-11 38.4T500-517q-37 35-46.5 60t-9.5 63ZM180-120q-24 0-42-18t-18-42v-600q0-24 18-42t42-18h600q24 0 42 18t18 42v600q0 24-18 42t-42 18H180Zm0-60h600v-600H180v600Zm0-600v600-600Z"
      {...props}
    />
  );
}

export function IconArrowForward(props) {
  return <SymbolIcon path="M686-450H160v-60h526L438-758l42-42 320 320-320 320-42-42 248-248Z" {...props} />;
}

export function IconMenuBook(props) {
  return (
    <SymbolIcon
      path="M560-574v-48q33-14 67.5-21t72.5-7q26 0 51 4t49 10v44q-24-9-48.5-13.5T700-610q-38 0-73 9.5T560-574Zm0 220v-49q33-13.5 67.5-20.25T700-430q26 0 51 4t49 10v44q-24-9-48.5-13.5T700-390q-38 0-73 9t-67 27Zm0-110v-48q33-14 67.5-21t72.5-7q26 0 51 4t49 10v44q-24-9-48.5-13.5T700-500q-38 0-73 9.5T560-464ZM248-300q53.57 0 104.28 12.5Q403-275 452-250v-427q-45-30-97.62-46.5Q301.76-740 248-740q-38 0-74.5 9.5T100-707v434q31-14 70.5-20.5T248-300Zm264 50q50-25 98-37.5T712-300q38 0 78.5 6t69.5 16v-429q-34-17-71.82-25-37.82-8-76.18-8-54 0-104.5 16.5T512-677v427Zm-30 90q-51-38-111-58.5T248-239q-36.54 0-71.77 9T106-208q-23.1 11-44.55-3Q40-225 40-251v-463q0-15 7-27.5T68-761q42-20 87.39-29.5 45.4-9.5 92.61-9.5 63 0 122.5 17T482-731q51-35 109.5-52T712-800q46.87 0 91.93 9.5Q849-781 891-761q14 7 21.5 19.5T920-714v463q0 27.89-22.5 42.45Q875-194 853-208q-34-14-69.23-22.5Q748.54-239 712-239q-63 0-121 21t-109 58ZM276-489Z"
      {...props}
    />
  );
}

export function IconHub(props) {
  return (
    <SymbolIcon
      path="M153-73q-33-33-33-81t33.25-81q33.25-33 80.75-33 14 0 24.5 2.5T280-258l85-106q-19-23-29-52.5t-5-61.5l-121-41q-15 25-39.5 39T114-466q-47.5 0-80.75-33.25T0-580q0-47.5 33.25-80.75T114-694q47.5 0 80.75 33.25T228-580v4l122 42q18-32 43.5-49t56.5-24v-129q-39-11-61.5-43T366-846q0-47.5 33-80.75T480-960q48 0 81 33.25T594-846q0 35-23 67t-61 43v129q31 7 57 24t44 49l121-42v-4q0-47.5 33.25-80.75T846-694q47.5 0 80.75 33T960-580q0 48-33.25 81T846-466q-32 0-57-14t-39-39l-121 41q5 32-4.5 61.5T595-364l85 106q11-5 21.5-7.5t24.06-2.5Q774-268 807-235t33 81q0 48-33 81t-81 33q-48 0-81-33.25T612-154q0-20 5.5-36t15.5-31l-85-106q-32.13 17-68.56 17Q443-310 411-327l-84 107q10 15 15.5 30.5T348-154q0 47.5-33 80.75T234-40q-48 0-81-33Zm-38.96-453q22.96 0 38.46-15.54 15.5-15.53 15.5-38.5 0-22.96-15.54-38.46-15.53-15.5-38.5-15.5Q91-634 75.5-618.46 60-602.93 60-579.96 60-557 75.54-541.5q15.53 15.5 38.5 15.5ZM272.5-115.54q15.5-15.53 15.5-38.5 0-22.96-15.54-38.46-15.53-15.5-38.5-15.5-22.96 0-38.46 15.54-15.5 15.53-15.5 38.5 0 22.96 15.54 38.46 15.53 15.5 38.5 15.5 22.96 0 38.46-15.54Zm246-692q15.5-15.53 15.5-38.5 0-22.96-15.54-38.46-15.53-15.5-38.5-15.5-22.96 0-38.46 15.54-15.5 15.53-15.5 38.5 0 22.96 15.54 38.46 15.53 15.5 38.5 15.5 22.96 0 38.46-15.54ZM480.5-370q37.5 0 63.5-26.5t26-64q0-37.5-26.1-63.5T480-550q-37 0-63.5 26.1T390-460q0 37 26.5 63.5t64 26.5Zm284 254.46q15.5-15.53 15.5-38.5 0-22.96-15.54-38.46-15.53-15.5-38.5-15.5-22.96 0-38.46 15.54-15.5 15.53-15.5 38.5 0 22.96 15.54 38.46 15.53 15.5 38.5 15.5 22.96 0 38.46-15.54Zm120-426q15.5-15.53 15.5-38.5 0-22.96-15.54-38.46-15.53-15.5-38.5-15.5-22.96 0-38.46 15.54-15.5 15.53-15.5 38.5 0 22.96 15.54 38.46 15.53 15.5 38.5 15.5 22.96 0 38.46-15.54ZM480-846ZM114-580Zm366 120Zm366-120ZM234-154Zm492 0Z"
      {...props}
    />
  );
}

export function IconSensors(props) {
  return (
    <SymbolIcon
      path="M197-197q-54-54-85.5-126.5T80-480q0-84 31.5-156.5T197-763l43 43q-46 46-73 107.5T140-480q0 71 26.5 132T240-240l-43 43Zm113-113q-32-32-51-75.5T240-480q0-51 19-94.5t51-75.5l43 43q-24 24-38.5 56.5T300-480q0 38 14 70t39 57l-43 43Zm113.5-113.5Q400-447 400-480t23.5-56.5Q447-560 480-560t56.5 23.5Q560-513 560-480t-23.5 56.5Q513-400 480-400t-56.5-23.5ZM650-310l-43-43q24-24 38.5-56.5T660-480q0-38-14-70t-39-57l43-43q32 32 51 75.5t19 94.5q0 50-19 93.5T650-310Zm113 113-43-43q46-46 73-107.5T820-480q0-71-26.5-132T720-720l43-43q54 55 85.5 127.5T880-480q0 83-31.5 155.5T763-197Z"
      {...props}
    />
  );
}

export function IconMemory(props) {
  return (
    <SymbolIcon
      path="M377-377v-205h205v205H377Zm60-60h85v-85h-85v85Zm-77 317v-80H260q-24 0-42-18t-18-42v-100h-80v-60h80v-124h-80v-60h80v-100q0-24 18-42t42-18h100v-76h60v76h124v-76h60v76h100q24 0 42 18t18 42v100h76v60h-76v124h76v60h-76v100q0 24-18 42t-42 18H604v80h-60v-80H420v80h-60Zm344-140v-444H260v444h444ZM480-480Z"
      {...props}
    />
  );
}

export function IconAssignmentTurnedIn(props) {
  return (
    <SymbolIcon
      path="m423-329 277-277-43-43-234 234-121-121-42 42 163 165ZM180-120q-24.75 0-42.37-17.63Q120-155.25 120-180v-600q0-24.75 17.63-42.38Q155.25-840 180-840h205q5-35 32-57.5t63-22.5q36 0 63 22.5t32 57.5h205q24.75 0 42.38 17.62Q840-804.75 840-780v600q0 24.75-17.62 42.37Q804.75-120 780-120H180Zm0-60h600v-600H180v600Zm324.5-627.5Q515-818 515-832t-10.5-24.5Q494-867 480-867t-24.5 10.5Q445-846 445-832t10.5 24.5Q466-797 480-797t24.5-10.5ZM180-180v-600 600Z"
      {...props}
    />
  );
}

export function IconLockClock(props) {
  return (
    <SymbolIcon
      path="M350-634h260v-93q0-57-37.5-95T480-860q-55 0-92.5 38T350-727v93ZM557-80H220q-23 0-41.5-18.5T160-140v-434q0-23 18.5-41.5T220-634h70v-93q0-81 55-137t135-56q80 0 135 56t55 137v93h70q23 0 41.5 18.5T800-574v87q-13-3-27-4t-33-1v-82H220v434h301q7 17 15 30.5T557-80Zm60-23q-57-57-57-136t57-136q57-57 136-57t136 57q57 57 57 136t-57 136q-57 57-136 57t-136-57Zm210-35 27-27-84-76v-124h-42v135.78L827-138ZM220-574v434-434Z"
      {...props}
    />
  );
}

export function IconPerson(props) {
  return (
    <SymbolIcon
      path="M372-523q-42-42-42-108t42-108q42-42 108-42t108 42q42 42 42 108t-42 108q-42 42-108 42t-108-42ZM160-160v-94q0-38 19-65t49-41q67-30 128.5-45T480-420q62 0 123 15.5T731-360q31 14 50 41t19 65v94H160Zm60-60h520v-34q0-16-9.5-30.5T707-306q-64-31-117-42.5T480-360q-57 0-111 11.5T252-306q-14 7-23 21.5t-9 30.5v34Zm324.5-346.5Q570-592 570-631t-25.5-64.5Q519-721 480-721t-64.5 25.5Q390-670 390-631t25.5 64.5Q441-541 480-541t64.5-25.5ZM480-631Zm0 411Z"
      {...props}
    />
  );
}

// Del set clasico "Material Icons" (outlined), no de Symbols -- ver nota
// de licencia/motivo arriba.
export function IconSecurityUpdateGood(props) {
  return (
    <SymbolIcon
      viewBox="0 0 24 24"
      path="M17 1.01 7 1c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-1.99-2-1.99zM17 21H7v-1h10v1zm0-3H7V6h10v12zm0-14H7V3h10v1zm-1 6.05-1.41-1.41-3.54 3.54-1.41-1.41-1.41 1.41L11.05 15 16 10.05z"
      {...props}
    />
  );
}

// 13-sep -- 2 iconos nuevos para el pase de fidelidad de LosSieteCasos.jsx
// (Pantalla 3) contra mockups/03_Seleccion_Caso.png/.html: el banner de
// protocolo usa "info" y el módulo de georreferencia del panel inspector
// usa "location_on", ninguno existía todavía en este archivo.
export function IconInfo(props) {
  return (
    <SymbolIcon
      path="M440-280h80v-240h-80v240Zm40-320q17 0 28.5-11.5T520-640q0-17-11.5-28.5T480-680q-17 0-28.5 11.5T440-640q0 17 11.5 28.5T480-600Zm0 520q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q134 0 227-93t93-227q0-134-93-227t-227-93q-134 0-227 93t-93 227q0 134 93 227t227 93Zm0-320Z"
      {...props}
    />
  );
}

export function IconLocationOn(props) {
  return (
    <SymbolIcon
      path="M480-480q33 0 56.5-23.5T560-560q0-33-23.5-56.5T480-640q-33 0-56.5 23.5T400-560q0 33 23.5 56.5T480-480Zm0 294q122-112 181-203.5T720-552q0-109-69.5-178.5T480-800q-101 0-170.5 69.5T240-552q0 71 59 162.5T480-186Zm0 106Q319-217 239.5-334.5T160-552q0-150 96.5-239T480-880q127 0 223.5 89T800-552q0 100-79.5 217.5T480-80Zm0-480Z"
      {...props}
    />
  );
}

// 13-sep -- Diana pidió agregar de vuelta el icono decorativo del pie de
// la lista de casos (figura del mockup: una lÍnea ascendente tipo
// "insights"/tendencia). No se usa el glifo oficial de Material Symbols
// aquí (a diferencia de los demás iconos de este archivo): no se tiene
// certeza del trazo SVG exacto de "insights" y un `path` inventado se
// vería peor que un equivalente honesto. Este es un dibujo propio, simple
// y siempre válido (2 polylines, sin `path` adivinado) -- una línea
// ascendente con punta de flecha, mismo espíritu visual que "tendencia
// positiva", no una copia literal del glifo de Google.
export function IconTrendingUp({ size = 20, style, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false" style={style} {...props}>
      <polyline points="3,17 9,11 13,15 21,6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <polyline points="15,6 21,6 21,12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

// 13-sep -- iconos para el pase de fidelidad de ExpedienteEscuela.jsx
// (Pantalla 4) contra mockups/04_Expediente_Escuela.png/.html. IconArrowBack
// e IconLock son el glifo oficial de Material Symbols (misma familia que el
// resto del archivo). IconVerified, IconPsychology e IconHourglassEmpty son
// dibujos propios (mismo criterio que IconTrendingUp): no hay certeza del
// trazo SVG exacto de esos 3 glifos y un `path` adivinado saldría peor que
// un equivalente honesto construido con formas básicas.
export function IconArrowBack(props) {
  return <SymbolIcon path="M313-440l224 224-57 57-320-320 320-320 57 57-224 224h487v80H313Z" {...props} />;
}

export function IconLock(props) {
  return (
    <SymbolIcon
      path="M240-80q-33 0-56.5-23.5T160-160v-400q0-33 23.5-56.5T240-640h40v-80q0-83 58.5-141.5T480-920q83 0 141.5 58.5T680-720v80h40q33 0 56.5 23.5T800-560v400q0 33-23.5 56.5T720-80H240Zm0-80h480v-400H240v400Zm240-120q33 0 56.5-23.5T560-360q0-33-23.5-56.5T480-440q-33 0-56.5 23.5T400-360q0 33 23.5 56.5T480-280ZM360-640h240v-80q0-50-35-85t-85-35q-50 0-85 35t-35 85v80ZM240-160v-400 400Z"
      {...props}
    />
  );
}

export function IconVerified({ size = 20, style, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false" style={style} {...props}>
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" />
      <polyline points="8,12.5 10.5,15 16,9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
    </svg>
  );
}

export function IconPsychology({ size = 20, style, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false" style={style} {...props}>
      <circle cx="12" cy="9" r="6" stroke="currentColor" strokeWidth="2" />
      <line x1="12" y1="15" x2="12" y2="21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      <circle cx="9.5" cy="8" r="1.1" fill="currentColor" />
      <circle cx="14.5" cy="8" r="1.1" fill="currentColor" />
      <circle cx="12" cy="11" r="1.1" fill="currentColor" />
    </svg>
  );
}

export function IconHourglassEmpty({ size = 20, style, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false" style={style} {...props}>
      <polygon points="6,3 18,3 12,11 18,21 6,21 12,11" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" fill="none" />
      <line x1="6" y1="3" x2="18" y2="3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      <line x1="6" y1="21" x2="18" y2="21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

// 13-sep -- 3 iconos nuevos para el pase de fidelidad de Conclusion.jsx
// (Pantalla 5) contra mockups/05_Conclusion_Top3.png/.html. Mismo criterio
// que IconVerified/IconPsychology/IconHourglassEmpty: sin certeza del
// trazo SVG exacto de los glifos oficiales de Material Symbols ("shield",
// "router", "check_box_outline_blank") para estos 3, se dibujan a mano con
// formas básicas -- equivalente honesto, no una copia literal del glifo de
// Google. IconShield e IconRouter se usan solo para D2 y D4 (los únicos 2
// drivers que el mockup muestra como dominantes hoy); si algún día otro
// driver domina, Conclusion.jsx cae a IconEmptySquare en vez de inventar
// un ícono nuevo sin precedente en el mockup.
export function IconShield({ size = 20, style, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false" style={style} {...props}>
      <path
        d="M12 2.5 19.5 5.5V11.5C19.5 16 16.2 19.8 12 21.5C7.8 19.8 4.5 16 4.5 11.5V5.5L12 2.5Z"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinejoin="round"
        fill="none"
      />
    </svg>
  );
}

export function IconRouter({ size = 20, style, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false" style={style} {...props}>
      <rect x="3" y="13" width="18" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.8" fill="none" />
      <circle cx="7.5" cy="16.5" r="1" fill="currentColor" />
      <circle cx="11.5" cy="16.5" r="1" fill="currentColor" />
      <line x1="12" y1="13" x2="12" y2="8.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M8.5 8.5C9.7 7.3 11.3 6.6 12 6.6C12.7 6.6 14.3 7.3 15.5 8.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" fill="none" />
      <path d="M6.3 6.3C8.1 4.5 10.2 3.6 12 3.6C13.8 3.6 15.9 4.5 17.7 6.3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" fill="none" />
    </svg>
  );
}

export function IconEmptySquare({ size = 20, style, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false" style={style} {...props}>
      <rect x="4" y="4" width="16" height="16" rx="2" stroke="currentColor" strokeWidth="1.8" fill="none" />
    </svg>
  );
}

// 13-sep -- 2 iconos nuevos para el pase de fidelidad de Explorador.jsx
// (Pantalla 6) contra mockups/06_Explorador.png/.html: los filtros de
// "Ciclo escolar" y "Nivel educativo" usan "calendar_month" y "school" en
// la plantilla (el de "Entidad" ya existe, IconLocationOn). Mismo criterio
// que IconShield/IconRouter/IconEmptySquare: sin certeza del trazo SVG
// exacto de esos 2 glifos oficiales de Material Symbols, se dibujan a mano
// con formas básicas -- equivalente honesto, no una copia literal del
// glifo de Google.
export function IconCalendarMonth({ size = 20, style, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false" style={style} {...props}>
      <rect x="3.5" y="5" width="17" height="15" rx="2" stroke="currentColor" strokeWidth="1.8" fill="none" />
      <line x1="3.5" y1="9.5" x2="20.5" y2="9.5" stroke="currentColor" strokeWidth="1.8" />
      <line x1="7.5" y1="3" x2="7.5" y2="6.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <line x1="16.5" y1="3" x2="16.5" y2="6.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

export function IconSchool({ size = 20, style, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false" style={style} {...props}>
      <polygon points="12,4 22,9 12,14 2,9" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" fill="none" />
      <path d="M6 11.5V16C6 16 8.5 18 12 18C15.5 18 18 16 18 16V11.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" fill="none" />
      <line x1="22" y1="9" x2="22" y2="15" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

// 13-sep -- 2 iconos nuevos para los 2 botones del panel de "Expediente" de
// Explorador.jsx (P6) que Diana pidió restaurar ("Exportar Ficha CCT (PDF)"
// / "Vincular a Mesa de Enlace"). El mockup usa "file_download" y
// "assignment_add" de Material Symbols; mismo criterio que
// IconShield/IconRouter/IconCalendarMonth: sin certeza del trazo SVG exacto
// de esos 2 glifos oficiales, se dibujan a mano con formas básicas --
// equivalente honesto, no una copia literal del glifo de Google.
export function IconDownload({ size = 20, style, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false" style={style} {...props}>
      <line x1="12" y1="3.5" x2="12" y2="14.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <polyline points="7,10 12,15 17,10" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" fill="none" />
      <path d="M4.5 16.5V18.5C4.5 19.6 5.4 20.5 6.5 20.5H17.5C18.6 20.5 19.5 19.6 19.5 18.5V16.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" fill="none" />
    </svg>
  );
}

export function IconLink({ size = 20, style, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false" style={style} {...props}>
      <rect x="2.7" y="8.7" width="9" height="6.6" rx="3.3" transform="rotate(-45 2.7 8.7)" stroke="currentColor" strokeWidth="1.8" fill="none" />
      <rect x="12.3" y="8.7" width="9" height="6.6" rx="3.3" transform="rotate(-45 12.3 8.7)" stroke="currentColor" strokeWidth="1.8" fill="none" />
      <line x1="10.5" y1="13.5" x2="13.5" y2="10.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}
