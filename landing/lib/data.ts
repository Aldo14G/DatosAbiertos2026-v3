// Real data extracted from .antigravity/team/shared/advanced_quality_results.json
// Generated 2026-04-16. Pipeline v3.0, run_id: 20260415_181941

export const PORTAL_STATS = {
  totalDatasets: 272,
  avgScore: 95.45,
  totalOrgs: 61,
  goldDatasets: 246,
  silverDatasets: 16,
  bronzeDatasets: 10,
  goldOrgs: 54,
  silverOrgs: 7,
  bronzeOrgs: 0,
  snapshotDate: "2026-03-19",
  evaluationDate: "2026-04-15",
} as const;

export type Grade = "Gold" | "Silver" | "Bronze";

export interface OrgRanking {
  name: string;
  nameEn: string;
  datasets: number;
  score: number;
  grade: Grade;
}

// Top 20 organizations by average score (real data, cp1252 decoded)
export const ORG_RANKINGS: OrgRanking[] = [
  { name: "Servicios de Agua y Drenaje de Monterrey, I.P.D.", nameEn: "Monterrey Water & Drainage Services", datasets: 8, score: 98.3, grade: "Gold" },
  { name: "Secretaría de Igualdad e Inclusión", nameEn: "Secretary of Equality and Inclusion", datasets: 14, score: 98.3, grade: "Gold" },
  { name: "Instituto Estatal de Cultura Física y Deporte (INDE)", nameEn: "State Institute of Physical Culture and Sport", datasets: 6, score: 98.3, grade: "Gold" },
  { name: "Secretaría Ejecutiva del Sistema Estatal Anticorrupción (SESEANL)", nameEn: "Executive Secretary, Anti-Corruption System", datasets: 6, score: 98.3, grade: "Gold" },
  { name: "Fideicomiso Fondo para la Vivienda (FOVILEON)", nameEn: "Housing Trust Fund (FOVILEON)", datasets: 4, score: 98.3, grade: "Gold" },
  { name: "Instituto Estatal de las Mujeres", nameEn: "State Women's Institute", datasets: 2, score: 98.3, grade: "Gold" },
  { name: "Instituto de la Vivienda", nameEn: "State Housing Institute", datasets: 2, score: 98.3, grade: "Gold" },
  { name: "Universidad de Ciencias de la Seguridad", nameEn: "University of Security Sciences", datasets: 2, score: 98.3, grade: "Gold" },
  { name: "Parque Fundidora, O.P.D", nameEn: "Fundidora Park", datasets: 2, score: 98.3, grade: "Gold" },
  { name: "Junta Local de Conciliación y Arbitraje", nameEn: "Local Conciliation and Arbitration Board", datasets: 2, score: 98.3, grade: "Gold" },
  { name: "Consejo para la Cultura y las Artes de Nuevo León", nameEn: "Council for Culture and Arts of Nuevo León", datasets: 2, score: 98.3, grade: "Gold" },
  { name: "Instituto Estatal de las Personas Adultas Mayores (IEPAM)", nameEn: "State Institute for Older Adults", datasets: 2, score: 98.3, grade: "Gold" },
  { name: "Colegio de Estudios Científicos y Tecnológicos (CECyTENL)", nameEn: "College of Scientific and Technological Studies", datasets: 2, score: 98.3, grade: "Gold" },
  { name: "Instituto de Investigación, Innovación y Estudios de Posgrado para la Educación", nameEn: "Research and Innovation Institute for Education", datasets: 2, score: 98.3, grade: "Gold" },
  { name: "Fideicomiso Fondo de Fomento Agropecuario del Estado de Nuevo León", nameEn: "Agricultural Development Trust Fund", datasets: 2, score: 98.3, grade: "Gold" },
  { name: "Secretaría de Cultura", nameEn: "Secretary of Culture", datasets: 5, score: 85.8, grade: "Silver" },
  { name: "Fideicomiso Para el Desarrollo de la Zona Citrícola", nameEn: "Citrus Zone Development Trust", datasets: 2, score: 82.9, grade: "Silver" },
  { name: "Fideicomiso No. 2209 — Línea 3 del Sistema de Transporte Colectivo Metrorrey", nameEn: "Metrorrey Line 3 Trust", datasets: 2, score: 81.3, grade: "Silver" },
  { name: "Fideicomiso para la Conservación del Patrimonio Cultural", nameEn: "Cultural Heritage Conservation Trust", datasets: 2, score: 76.5, grade: "Silver" },
  { name: "Oficina Ejecutiva del Titular del Poder Ejecutivo", nameEn: "Executive Office of the State Governor", datasets: 2, score: 74.6, grade: "Silver" },
];

export const ISO_DIMENSIONS = [
  {
    id: "completeness",
    nameEs: "Completitud",
    nameEn: "Completeness",
    weight: 25,
    icon: "CheckSquare",
    descriptionEs: "Proporción de valores no nulos sobre el total de celdas esperadas en el dataset.",
    descriptionEn: "Ratio of non-null values over the total expected cells in the dataset.",
    formulaEs: "Celdas completas ÷ Total celdas × 100",
    formulaEn: "Complete cells ÷ Total cells × 100",
    exampleEs: "Solicitudes de Acceso a la Información — 13 columnas, 100% sin nulos.",
    exampleEn: "Public Information Requests — 13 columns, 100% non-null.",
    isoRef: "ISO/IEC 25012:2008 §4.14",
  },
  {
    id: "timeliness",
    nameEs: "Puntualidad",
    nameEn: "Timeliness",
    weight: 25,
    icon: "Clock",
    descriptionEs: "Actualidad del dataset medida por días transcurridos desde la última modificación.",
    descriptionEn: "Dataset currency measured by days elapsed since last modification.",
    formulaEs: "max(0, 100 − días_desde_actualización × 0.1)",
    formulaEn: "max(0, 100 − days_since_update × 0.1)",
    exampleEs: "Dataset con metadata_modified de ayer → score 99.9.",
    exampleEn: "Dataset modified yesterday → score 99.9.",
    isoRef: "ISO/IEC 25012:2008 §4.15",
  },
  {
    id: "accessibility",
    nameEs: "Accesibilidad",
    nameEn: "Accessibility",
    weight: 20,
    icon: "Globe",
    descriptionEs: "Disponibilidad del recurso: URL activa, formato abierto y descargable sin autenticación.",
    descriptionEn: "Resource availability: active URL, open format, downloadable without authentication.",
    formulaEs: "URL activa (40) + formato abierto (40) + descarga libre (20)",
    formulaEn: "Active URL (40) + open format (40) + free download (20)",
    exampleEs: "CSV directo en datos.nl.gob.mx → 100/100.",
    exampleEn: "Direct CSV at datos.nl.gob.mx → 100/100.",
    isoRef: "ISO/IEC 25012:2008 §4.12",
  },
  {
    id: "documentation",
    nameEs: "Documentación",
    nameEn: "Documentation",
    weight: 20,
    icon: "FileText",
    descriptionEs: "Presencia de título, descripción, licencia, organización y frecuencia de actualización en los metadatos CKAN.",
    descriptionEn: "Presence of title, description, license, organization, and update frequency in CKAN metadata.",
    formulaEs: "Σ campos presentes × peso_campo ÷ peso_máximo × 100",
    formulaEn: "Σ present fields × field_weight ÷ max_weight × 100",
    exampleEs: "Dataset sin licencia explícita → descuento de 20 puntos.",
    exampleEn: "Dataset without explicit license → 20-point deduction.",
    isoRef: "ISO/IEC 25012:2008 §4.13",
  },
  {
    id: "openness",
    nameEs: "Apertura",
    nameEn: "Openness",
    weight: 10,
    icon: "Unlock",
    descriptionEs: "Calificación de la licencia según el Open Definition: dominio público > CC-BY > CC-BY-SA > restrictiva.",
    descriptionEn: "License rating per the Open Definition: public domain > CC-BY > CC-BY-SA > restrictive.",
    formulaEs: "Dominio público=100, CC-BY=80, CC-BY-SA=60, Sin licencia=20",
    formulaEn: "Public domain=100, CC-BY=80, CC-BY-SA=60, No license=20",
    exampleEs: "Mayoría de datasets NL bajo licencia implícita → score promedio 60.",
    exampleEn: "Most NL datasets under implicit license → average score 60.",
    isoRef: "ISO/IEC 25012:2008 §4.16",
  },
];

export const GRADE_CRITERIA = {
  gold: {
    threshold: 90,
    color: "gold",
    criteria: [
      { es: "Score global ≥ 90 / 100", en: "Global score ≥ 90 / 100" },
      { es: "Completitud ≥ 95%", en: "Completeness ≥ 95%" },
      { es: "URL activa y formato CSV/JSON", en: "Active URL and CSV/JSON format" },
      { es: "Metadata con título, descripción y organización", en: "Metadata with title, description, and organization" },
      { es: "Actualización en los últimos 90 días", en: "Updated within the last 90 days" },
    ],
  },
  silver: {
    threshold: 70,
    color: "silver",
    criteria: [
      { es: "Score global 70–89 / 100", en: "Global score 70–89 / 100" },
      { es: "Completitud ≥ 80%", en: "Completeness ≥ 80%" },
      { es: "URL activa (formato no restrictivo)", en: "Active URL (non-restrictive format)" },
      { es: "Metadata parcial (mínimo título y organización)", en: "Partial metadata (minimum title and organization)" },
      { es: "Actualización en los últimos 180 días", en: "Updated within the last 180 days" },
    ],
  },
  bronze: {
    threshold: 0,
    color: "bronze",
    criteria: [
      { es: "Score global < 70 / 100", en: "Global score < 70 / 100" },
      { es: "Completitud < 80% o valores nulos significativos", en: "Completeness < 80% or significant null values" },
      { es: "URL rota o formato propietario (PDF/XLSX sin alternativa)", en: "Broken URL or proprietary format (PDF/XLSX without alternative)" },
      { es: "Metadata insuficiente", en: "Insufficient metadata" },
      { es: "Sin actualización en más de 180 días", en: "No update in more than 180 days" },
    ],
  },
};
