"use client";

import type { ReactNode } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { Database, Trophy, Building2, TrendingUp } from "lucide-react";
import { useLang } from "./LangProvider";
import { PORTAL_STATS } from "@/lib/data";

const ease = [0.16, 1, 0.3, 1] as const;

interface StatCard {
  icon: ReactNode;
  value: string;
  labelEs: string;
  labelEn: string;
  highlight?: boolean;
}

export function StatsBarSection() {
  const { t } = useLang();
  const reduced = useReducedMotion();

  const goldPct = Math.round(
    (PORTAL_STATS.goldDatasets / PORTAL_STATS.totalDatasets) * 100
  );

  const stats: StatCard[] = [
    {
      icon: <Database className="size-6" aria-hidden="true" />,
      value: PORTAL_STATS.totalDatasets.toString(),
      labelEs: "Datasets evaluados",
      labelEn: "Datasets evaluated",
    },
    {
      icon: <Trophy className="size-6" aria-hidden="true" />,
      value: `${goldPct}%`,
      labelEs: "Calificación Oro",
      labelEn: "Gold rating",
      highlight: true,
    },
    {
      icon: <Building2 className="size-6" aria-hidden="true" />,
      value: PORTAL_STATS.totalOrgs.toString(),
      labelEs: "Organizaciones",
      labelEn: "Organizations",
    },
    {
      icon: <TrendingUp className="size-6" aria-hidden="true" />,
      value: PORTAL_STATS.avgScore.toFixed(1),
      labelEs: "Puntuación promedio",
      labelEn: "Average score",
    },
  ];

  return (
    <section
      aria-label={t("Estadísticas del portal", "Portal statistics")}
      className="py-16 px-4 sm:px-6 bg-background"
    >
      <div className="mx-auto max-w-7xl">
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {stats.map((stat, idx) => (
            <motion.div
              key={idx}
              {...(reduced
                ? {}
                : {
                    initial: { opacity: 0, y: 20 },
                    whileInView: { opacity: 1, y: 0 },
                    viewport: { once: true, amount: 0.3 },
                    transition: { duration: 0.4, ease, delay: idx * 0.08 },
                  })}
              className="flex flex-col items-center gap-3 rounded-2xl border border-border/40 bg-card px-6 py-8 text-center"
            >
              <span
                className={
                  stat.highlight
                    ? "text-gold"
                    : "text-muted-foreground"
                }
              >
                {stat.icon}
              </span>
              <span
                className={`font-mono text-4xl font-bold tabular-nums ${
                  stat.highlight ? "text-gold" : "text-foreground"
                }`}
              >
                {stat.value}
              </span>
              <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
                {t(stat.labelEs, stat.labelEn)}
              </span>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
