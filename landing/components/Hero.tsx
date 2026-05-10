"use client";

import { useLang } from "./LangProvider";
import { PORTAL_STATS } from "@/lib/data";
import { PremiumFeatureTabs } from "@/components/blocks/premium-feature-tabs";
import { Database, Award, ShieldCheck } from "lucide-react";

const DASHBOARD_URL = "http://localhost:8501";

interface StatPill {
  value: string;
  labelEs: string;
  labelEn: string;
  highlight?: boolean;
}

export function Hero() {
  const { t } = useLang();

  const goldPct = Math.round(
    (PORTAL_STATS.goldDatasets / PORTAL_STATS.totalDatasets) * 100
  );

  const statPills: StatPill[] = [
    { value: String(PORTAL_STATS.totalDatasets), labelEs: "Datasets", labelEn: "Datasets" },
    { value: `${goldPct}%`, labelEs: "Calificación Oro", labelEn: "Gold rating", highlight: true },
    { value: String(PORTAL_STATS.totalOrgs), labelEs: "Organizaciones", labelEn: "Organizations" },
    { value: PORTAL_STATS.avgScore.toFixed(1), labelEs: "Puntuación media", labelEn: "Avg. score" },
  ];

  const heroTabs = [
    {
      value: "tab-1",
      icon: <Database className="h-5 w-5 shrink-0" />,
      label: t("Auditoría Continua", "Continuous Audit"),
      content: {
        badge: t("ISO/IEC 25012", "ISO/IEC 25012"),
        title: t("Métricas técnicas en tiempo real.", "Real-time technical metrics."),
        description: t(
          "Evaluamos completitud, exactitud, consistencia y unicidad directamente del portal de datos del estado. Todo automatizado y trazable.",
          "We evaluate completeness, accuracy, consistency, and uniqueness directly from the state data portal. Fully automated and traceable."
        ),
        buttonText: t("Ver Dashboard", "View Dashboard"),
        buttonLink: DASHBOARD_URL,
        imageSrc: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=800",
        imageAlt: "Data analysis visualization",
      },
    },
    {
      value: "tab-2",
      icon: <Award className="h-5 w-5 shrink-0" />,
      label: t("Estándar Oro", "Gold Standard"),
      content: {
        badge: t("Excelencia", "Excellence"),
        title: t("Identificando los mejores datos.", "Identifying the best data."),
        description: t(
          "Clasificamos los conjuntos de datos en Bronce, Plata y Oro. Promovemos la publicación de información de alto valor que sirva para investigación y negocio.",
          "We classify datasets into Bronze, Silver, and Gold. We promote publishing high-value information useful for research and business."
        ),
        buttonText: t("Explorar Rankings", "Explore Rankings"),
        buttonLink: "#rankings",
        imageSrc: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&q=80&w=800",
        imageAlt: "Gold quality standard dashboard",
      },
    },
    {
      value: "tab-3",
      icon: <ShieldCheck className="h-5 w-5 shrink-0" />,
      label: t("Transparencia", "Transparency"),
      content: {
        badge: t("Gobierno Abierto", "Open Government"),
        title: t("Confianza mediante código abierto.", "Trust through open source."),
        description: t(
          "Nuestra metodología y el código fuente de los validadores están disponibles para el público. Gobernar los datos es gobernar con evidencia.",
          "Our methodology and the source code for the validators are publicly available. Governing data is governing with evidence."
        ),
        buttonText: t("Leer Metodología", "Read Methodology"),
        buttonLink: "#methodology",
        imageSrc: "https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?auto=format&fit=crop&q=80&w=800",
        imageAlt: "Transparent process illustration",
      },
    },
  ];

  return (
    <div id="hero" className="min-h-screen bg-background">
      <PremiumFeatureTabs
        badge={`NL 2026 · ${t(`Evaluación ${PORTAL_STATS.snapshotDate}`, `Assessment ${PORTAL_STATS.snapshotDate}`)}`}
        heading={t("Gobernanza Pro", "Gobernanza Pro")}
        subtitle={t(
          "La salud de los datos abiertos en Nuevo León",
          "The health of open data in Nuevo León"
        )}
        description={t(
          "Auditoría automatizada bajo norma ISO/IEC 25012. Una ventana transparente al desempeño técnico de las dependencias estatales.",
          "Automated audit under ISO/IEC 25012. A transparent window into the technical performance of state agencies."
        )}
        tabs={heroTabs}
      >
        {/* KPI stat pills */}
        <div className="flex flex-wrap items-center justify-center gap-3 max-w-3xl mx-auto">
          {statPills.map((pill, idx) => (
            <div
              key={idx}
              className="flex flex-col items-center rounded-2xl border border-border/40 bg-card px-6 py-4 min-w-[110px]"
            >
              <span
                className={`font-mono text-2xl font-bold tabular-nums ${
                  pill.highlight ? "text-gold" : "text-foreground"
                }`}
              >
                {pill.value}
              </span>
              <span className="font-mono text-[9px] uppercase tracking-[0.16em] text-muted-foreground mt-1">
                {t(pill.labelEs, pill.labelEn)}
              </span>
            </div>
          ))}
        </div>
      </PremiumFeatureTabs>
    </div>
  );
}
