"use client";

import { motion, useReducedMotion } from "framer-motion";
import { Check, ExternalLink } from "lucide-react";
import { useLang } from "./LangProvider";
import { GRADE_CRITERIA, PORTAL_STATS } from "@/lib/data";

const REPO_URL = "https://github.com/Aldo14G/DatosAbiertos2026-v3";

const TIERS = [
  {
    key: "bronze" as const,
    labelEs: "Bronze",
    labelEn: "Bronze",
    descEs: "Datos presentes, calidad insuficiente",
    descEn: "Data present, insufficient quality",
    count: PORTAL_STATS.bronzeDatasets,
    cardClass: "border-rose-500/10 bg-gradient-to-b from-rose-500/5 to-transparent",
    headerClass: "border-border/30 bg-background/50 backdrop-blur-sm",
    badgeClass: "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20",
    checkClass: "text-rose-500",
  },
  {
    key: "silver" as const,
    labelEs: "Silver",
    labelEn: "Silver",
    descEs: "Datos accesibles, documentación parcial",
    descEn: "Accessible data, partial documentation",
    count: PORTAL_STATS.silverDatasets,
    cardClass: "border-teal/10 bg-gradient-to-b from-teal/5 to-transparent",
    headerClass: "border-border/30 bg-background/50 backdrop-blur-sm",
    badgeClass: "bg-teal/10 text-teal-600 dark:text-teal-400 border-teal/20",
    checkClass: "text-teal",
  },
  {
    key: "gold" as const,
    labelEs: "Gold",
    labelEn: "Gold",
    descEs: "Datos completos, actualizados y documentados",
    descEn: "Complete, up-to-date, and documented data",
    count: PORTAL_STATS.goldDatasets,
    cardClass: "border-gold/20 bg-gradient-to-b from-gold/10 to-transparent shadow-lg shadow-gold/5",
    headerClass: "border-border/30 bg-background/50 backdrop-blur-sm",
    badgeClass: "bg-gold/10 text-amber-600 dark:text-gold border-gold/20",
    checkClass: "text-gold",
    featured: true,
  },
];

const ease = [0.16, 1, 0.3, 1] as const;

export function MethodologySection() {
  const { t } = useLang();
  const reduced = useReducedMotion();

  const fadeUp = (delay = 0) =>
    reduced
      ? {}
      : {
          initial: { opacity: 0, y: 24 },
          whileInView: { opacity: 1, y: 0 },
          viewport: { once: true, amount: 0.15 },
          transition: { duration: 0.5, ease, delay },
        };

  return (
    <section
      id="methodology"
      aria-labelledby="methodology-heading"
      className="py-24 px-4 sm:px-6 relative overflow-hidden bg-background"
    >
      <div className="mx-auto max-w-7xl relative z-10">
        {/* Header */}
        <motion.div className="mb-16" {...fadeUp(0)}>
          <span className="text-[10px] font-mono tracking-[0.2em] text-gold uppercase opacity-80 mb-4 block">
            {t("Cómo calificamos · Pipeline v3.0", "How we grade · Pipeline v3.0")}
          </span>
          <h2
            id="methodology-heading"
            className="font-serif text-4xl md:text-5xl font-bold text-foreground mb-6"
          >
            {t(
              "Metodología Bronze / Silver / Gold",
              "Bronze / Silver / Gold Methodology"
            )}
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl">
            {t(
              "Cada dataset recibe una calificación según umbrales definidos sobre su score ponderado. Los criterios son públicos, reproducibles y auditables desde el repositorio.",
              "Each dataset receives a grade based on defined thresholds over its weighted score. Criteria are public, reproducible, and auditable from the repository."
            )}
          </p>
        </motion.div>

        {/* Grade cards */}
        <div className="grid gap-6 sm:grid-cols-3 mb-12">
          {TIERS.map((tier, idx) => {
            const criteria = GRADE_CRITERIA[tier.key];
            return (
              <motion.article
                key={tier.key}
                {...(reduced
                  ? {}
                  : {
                      initial: { opacity: 0, y: 24 },
                      whileInView: { opacity: 1, y: 0 },
                      viewport: { once: true, amount: 0.1 },
                      transition: { duration: 0.35, ease, delay: idx * 0.08 + 0.15 },
                    })}
                className={`relative overflow-hidden rounded-2xl border ${tier.cardClass} backdrop-blur-sm transition-all duration-500 hover:-translate-y-1 hover:shadow-xl group ${
                  tier.featured ? "ring-1 ring-gold/30" : ""
                }`}
              >
                {tier.featured && (
                  <div className="absolute -inset-1 bg-gradient-to-r from-gold/0 via-gold/10 to-gold/0 blur-lg opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                )}

                <div className={`border-b px-6 py-5 relative z-10 ${tier.headerClass}`}>
                  <div className="flex items-center justify-between mb-2">
                    <span
                      className={`inline-flex items-center justify-center rounded-full border px-3 py-1 font-serif text-sm font-bold tracking-wide ${tier.badgeClass}`}
                    >
                      {t(tier.labelEs, tier.labelEn)}
                    </span>
                    <span className="font-mono text-sm font-medium text-muted-foreground bg-midnight/5 px-2 py-0.5 rounded border border-border/50">
                      ≥ {criteria.threshold} {t("pts", "pts")}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground mt-3">
                    {t(tier.descEs, tier.descEn)}
                  </p>
                  <p className="mt-2 font-mono text-[10px] uppercase tracking-wider text-muted-foreground/70">
                    <strong className="text-foreground">{tier.count}</strong>{" "}
                    {t("datasets en esta categoría", "datasets in this category")}
                  </p>
                </div>

                <div className="px-6 py-5 relative z-10">
                  <ul className="flex flex-col gap-3" role="list">
                    {criteria.criteria.map((c, i) => (
                      <li key={i} className="flex items-start gap-3">
                        <Check
                          className={`mt-0.5 size-4 shrink-0 ${tier.checkClass}`}
                          aria-hidden="true"
                        />
                        <span className="text-sm text-foreground/80 leading-snug">
                          {t(c.es, c.en)}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              </motion.article>
            );
          })}
        </div>

        {/* Score bar visualization */}
        <motion.div
          className="rounded-2xl border border-border/40 bg-midnight/5 backdrop-blur-md px-8 py-6 mb-8 relative overflow-hidden"
          {...fadeUp(0.25)}
        >
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-gold/5 to-transparent opacity-50" />

          <p className="font-mono text-[10px] font-medium text-muted-foreground uppercase tracking-[0.2em] mb-4 relative z-10">
            {t("Escala de puntuación (0–100)", "Score scale (0–100)")}
          </p>
          <div
            className="relative h-4 rounded-full overflow-hidden flex shadow-inner relative z-10"
            role="progressbar"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={100}
          >
            <div
              className="h-full bg-rose-500/20 flex items-center justify-center border-r border-background/20 relative"
              style={{ width: "70%" }}
              aria-label="Bronze: 0-69"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-rose-500/10 to-rose-500/30" />
            </div>
            <div
              className="h-full bg-teal/20 flex items-center justify-center border-r border-background/20 relative"
              style={{ width: "20%" }}
              aria-label="Silver: 70-89"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-teal/10 to-teal/30" />
            </div>
            <div
              className="h-full bg-gold/20 flex items-center justify-center relative"
              style={{ width: "10%" }}
              aria-label="Gold: 90-100"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-gold/10 to-gold/30" />
            </div>
          </div>
          <div className="mt-4 flex justify-between font-mono text-[11px] font-medium text-muted-foreground relative z-10">
            <span className="text-rose-600 dark:text-rose-400">0 (Bronze)</span>
            <span className="text-teal absolute" style={{ left: "70%", transform: "translateX(-50%)" }}>70 (Silver)</span>
            <span className="text-amber-600 dark:text-gold absolute" style={{ left: "90%", transform: "translateX(-50%)" }}>90 (Gold)</span>
            <span className="text-foreground">100</span>
          </div>
        </motion.div>

        {/* Repo link */}
        <motion.div
          className="inline-flex items-center rounded-full border border-border/50 bg-background/50 px-4 py-2 backdrop-blur-sm"
          {...fadeUp(0.3)}
        >
          <p className="text-[13px] text-muted-foreground">
            {t(
              "La ficha técnica completa con definiciones formales y código fuente está disponible en",
              "The full technical specification with formal definitions and source code is available at"
            )}{" "}
            <a
              href={REPO_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 font-medium text-teal hover:text-gold transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring rounded"
            >
              GitHub
              <ExternalLink className="size-3" aria-hidden="true" />
            </a>
          </p>
        </motion.div>
      </div>
    </section>
  );
}
