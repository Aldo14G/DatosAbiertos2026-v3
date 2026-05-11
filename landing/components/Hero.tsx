"use client";

import { useLang } from "./LangProvider";
import { PORTAL_STATS } from "@/lib/data";
import { PremiumFeatureTabs } from "@/components/blocks/premium-feature-tabs";
import { CountUp } from "@/lib/count-up";
import { Database, Award, ShieldCheck } from "lucide-react";

const DASHBOARD_URL = "http://localhost:8501";

interface StatPill {
  end: number;
  suffix?: string;
  decimals?: number;
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
    { end: PORTAL_STATS.totalDatasets, labelEs: "Datasets evaluados", labelEn: "Datasets evaluated" },
    { end: goldPct, suffix: "%", labelEs: "Calificación Oro", labelEn: "Gold rating", highlight: true },
    { end: PORTAL_STATS.totalOrgs, labelEs: "Dependencias", labelEn: "Agencies" },
    { end: PORTAL_STATS.avgScore, decimals: 1, labelEs: "Puntuación media", labelEn: "Avg. score" },
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
          "Medimos siete características clave en cada dataset: si los datos están completos, son precisos y no tienen duplicados. Sin intervención manual, sin sesgos — resultados reproducibles por cualquier persona.",
          "We measure seven key characteristics in each dataset: whether the data is complete, accurate, and free of duplicates. No manual intervention, no bias — reproducible by anyone."
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
          "Cada dataset recibe un nivel — Bronce, Plata u Oro — según qué tan confiable es su información. Oro significa que el dato puede usarse con confianza para investigación, periodismo o política pública.",
          "Each dataset receives a tier — Bronze, Silver, or Gold — based on how reliable its information is. Gold means the data can be trusted for research, journalism, or public policy."
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
          "Cada decisión metodológica está documentada y el código es público. Cualquier ciudadano, periodista o investigador puede reproducir nuestra evaluación completa desde cero.",
          "Every methodological decision is documented and the code is open. Any citizen, journalist, or researcher can reproduce our full evaluation from scratch."
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
          "¿Son confiables los datos del gobierno de Nuevo León? Evaluamos cada dataset publicado por las dependencias estatales con la norma ISO/IEC 25012 — el estándar internacional de calidad de datos — y publicamos los resultados con total transparencia.",
          "How reliable is the data published by Nuevo León's government? We evaluate every dataset from state agencies using ISO/IEC 25012 — the international data quality standard — and publish the results with full transparency."
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
              <CountUp
                end={pill.end}
                suffix={pill.suffix}
                decimals={pill.decimals}
                duration={1.6}
                className={`font-mono text-2xl font-bold tabular-nums ${
                  pill.highlight ? "text-gold" : "text-foreground"
                }`}
              />
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
