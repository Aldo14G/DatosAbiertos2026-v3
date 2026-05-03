"use client";

import { useRef } from "react";
import { useLang } from "./LangProvider";
import { useInView } from "@/lib/use-in-view";
import { PORTAL_STATS } from "@/lib/data";
import { PremiumFeatureTabs } from "@/components/blocks/premium-feature-tabs";
import { Database, Award, ShieldCheck } from "lucide-react";

const DASHBOARD_URL = "http://localhost:8501/#dashboards";

const goldPct = Math.round(
  (PORTAL_STATS.goldDatasets / PORTAL_STATS.totalDatasets) * 100
);

export function Hero() {
  const { t } = useLang();
  const statsRef = useRef<HTMLDivElement>(null);
  const statsVisible = useInView(statsRef, 0.2);

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
        {/* Stat bar injected into the Feature Tabs header */}
        <div
          ref={statsRef}
          data-visible={statsVisible}
          className="grid grid-cols-2 gap-4 sm:grid-cols-4 max-w-5xl mx-auto"
        >
          <StatCard value={PORTAL_STATS.totalDatasets.toString()} label={t("Datasets", "Datasets")} mono index={0} />
          <StatCard value={`${goldPct}%`} label={t("Calidad Oro", "Gold Quality")} mono highlight index={1} />
          <StatCard value={PORTAL_STATS.totalOrgs.toString()} label={t("Organizaciones", "Organizations")} mono index={2} />
          <StatCard value={PORTAL_STATS.avgScore.toFixed(1)} label={t("Score Promedio", "Average Score")} mono index={3} />
        </div>
      </PremiumFeatureTabs>
    </div>
  );
}

function StatCard({
  value,
  label,
  mono,
  highlight,
  index = 0,
}: {
  value: string;
  label: string;
  mono?: boolean;
  highlight?: boolean;
  index?: number;
}) {
  return (
    <div
      className={`card-entrance flex flex-col gap-1 px-4 py-5 sm:px-6 sm:py-6 rounded-2xl border bg-black/5 dark:bg-white/5 backdrop-blur-md shadow-sm transition-transform hover:-translate-y-1 ${
        highlight ? "border-amber-500/30 ring-1 ring-amber-500/20 bg-amber-500/5" : "border-border/50"
      }`}
      style={{ "--i": index } as React.CSSProperties}
    >
      <span
        className={`text-3xl sm:text-4xl font-bold leading-none ${
          mono ? "font-mono" : ""
        } ${highlight ? "text-amber-500" : "text-foreground"}`}
      >
        {value}
      </span>
      <span className="text-[10px] sm:text-xs font-medium text-muted-foreground uppercase tracking-wider mt-2">
        {label}
      </span>
    </div>
  );
}
