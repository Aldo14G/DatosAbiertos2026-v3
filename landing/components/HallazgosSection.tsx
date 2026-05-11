"use client";

import { motion, useReducedMotion } from "framer-motion";
import {
  Award,
  TrendingUp,
  Clock,
  Building2,
  Database,
  Fingerprint,
} from "lucide-react";
import { useLang } from "./LangProvider";
import { CountUp } from "@/lib/count-up";

const ease = [0.16, 1, 0.3, 1] as const;

const FINDINGS = [
  {
    id: "oro",
    icon: Award,
    iconClass: "bg-gold/10 text-gold",
    statNum: 65,
    statDecimals: 0,
    statSuffix: "%",
    statClass: "text-amber-600 dark:text-gold",
    titleEs: "Mayoría en nivel Oro",
    titleEn: "Majority at Gold level",
    descEs:
      "189 de 290 datasets superan el umbral de calidad Oro (score ≥ 85). El portal de NL lidera entre estados con portales de datos activos.",
    descEn:
      "189 of 290 datasets exceed the Gold quality threshold (score ≥ 85). NL's portal leads among states with active data portals.",
  },
  {
    id: "max",
    icon: TrendingUp,
    iconClass: "bg-teal/10 text-teal",
    statNum: 96.2,
    statDecimals: 1,
    statSuffix: "",
    statClass: "text-teal",
    titleEs: "Score máximo del portal",
    titleEn: "Portal maximum score",
    descEs:
      "Universidad de Ciencias de la Seguridad alcanzó 96.2 / 100. Completitud y exactitud perfectas en ambos datasets publicados.",
    descEn:
      "Universidad de Ciencias de la Seguridad scored 96.2 / 100. Perfect completeness and accuracy in both published datasets.",
  },
  {
    id: "actualidad",
    icon: Clock,
    iconClass: "bg-rose-500/10 text-rose-600 dark:text-rose-400",
    statNum: 7,
    statDecimals: 0,
    statSuffix: "%",
    statClass: "text-rose-600 dark:text-rose-400",
    titleEs: "Área crítica: Actualidad",
    titleEn: "Critical area: Timeliness",
    descEs:
      "21 datasets quedaron en Bronce. La dimensión de Actualidad —fecha de publicación— fue la de menor rendimiento promedio del portal.",
    descEn:
      "21 datasets remained at Bronze. The Timeliness dimension —publication date— had the lowest average performance across the portal.",
  },
  {
    id: "orgs-oro",
    icon: Building2,
    iconClass: "bg-teal/10 text-teal",
    statNum: 33,
    statDecimals: 0,
    statSuffix: "",
    statClass: "text-teal",
    titleEs: "Organizaciones Oro",
    titleEn: "Gold Organizations",
    descEs:
      "33 de 65 dependencias lograron nivel Oro en promedio. La Secretaría de Salud lideró con 29 datasets y un score global de 94.1.",
    descEn:
      "33 of 65 agencies achieved Gold level on average. Secretaría de Salud led with 29 datasets and a global score of 94.1.",
  },
  {
    id: "promedio",
    icon: Database,
    iconClass: "bg-gold/10 text-gold",
    statNum: 88.8,
    statDecimals: 1,
    statSuffix: "",
    statClass: "text-amber-600 dark:text-gold",
    titleEs: "Score promedio del portal",
    titleEn: "Portal average score",
    descEs:
      "Media ponderada global de 88.83 / 100. Supera el umbral Oro, clasificando al portal de NL en nivel de excelencia institucional.",
    descEn:
      "Global weighted average of 88.83 / 100. Exceeds the Gold threshold, placing NL's portal at the institutional excellence level.",
  },
  {
    id: "cobertura",
    icon: Fingerprint,
    iconClass: "bg-teal/10 text-teal",
    statNum: 100,
    statDecimals: 0,
    statSuffix: "%",
    statClass: "text-teal",
    titleEs: "Cobertura total del portal",
    titleEn: "Full portal coverage",
    descEs:
      "Evaluación completa de los 290 datasets activos al 2026-04-23. Cada dataset fue medido en las 7 dimensiones ISO/IEC 25012:2008.",
    descEn:
      "Complete evaluation of all 290 active datasets as of 2026-04-23. Each dataset was measured across all 7 ISO/IEC 25012:2008 dimensions.",
  },
] as const;

export function HallazgosSection() {
  const { t } = useLang();
  const reduced = useReducedMotion();

  return (
    <section
      id="hallazgos"
      aria-labelledby="hallazgos-heading"
      className="relative overflow-hidden py-24 px-4 sm:px-6 bg-background"
    >
      {/* Decorative glows */}
      <div
        className="pointer-events-none absolute inset-0 overflow-hidden"
        aria-hidden="true"
      >
        <div className="absolute right-0 top-1/4 h-96 w-96 rounded-full bg-rose-500/[0.12] dark:bg-rose-500/[0.08] blur-[100px]" />
        <div className="absolute bottom-0 left-0 h-80 w-80 rounded-full bg-gold/[0.12] dark:bg-gold/[0.08] blur-[80px]" />
      </div>

      <div className="relative z-10 mx-auto max-w-7xl">
        {/* Header */}
        <motion.div
          className="mb-14"
          {...(reduced
            ? {}
            : {
                initial: { opacity: 0, y: 24 },
                whileInView: { opacity: 1, y: 0 },
                viewport: { once: true, amount: 0.2 },
                transition: { duration: 0.5, ease },
              })}
        >
          <span className="eyebrow">
            {t("Resultados · Evaluación 2026-04-23", "Results · Assessment 2026-04-23")}
          </span>
          <h2
            id="hallazgos-heading"
            className="font-serif text-4xl md:text-5xl font-bold text-foreground mb-4"
          >
            {t("¿Qué encontramos?", "What did we find?")}
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl">
            {t(
              "La evaluación automatizada de los 290 datasets del portal de Nuevo León revela un panorama de calidad institucional por encima del promedio nacional.",
              "The automated evaluation of Nuevo León's 290 portal datasets reveals an institutional quality landscape above the national average."
            )}
          </p>
        </motion.div>

        {/* Cards grid */}
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {FINDINGS.map((item, idx) => {
            const Icon = item.icon;
            return (
              <motion.article
                key={item.id}
                {...(reduced
                  ? {}
                  : {
                      initial: { opacity: 0, y: 24 },
                      whileInView: { opacity: 1, y: 0 },
                      viewport: { once: true, amount: 0.1 },
                      transition: {
                        duration: 0.35,
                        ease,
                        delay: idx * 0.06 + 0.1,
                      },
                    })}
                className="rounded-2xl border border-border/40 bg-background/50 p-6 backdrop-blur-sm transition-all duration-300 hover:-translate-y-1 hover:border-border/70 hover:shadow-xl hover:shadow-teal/5"
              >
                <div
                  className={`mb-4 inline-flex size-11 items-center justify-center rounded-xl ${item.iconClass}`}
                  aria-hidden="true"
                >
                  <Icon className="size-5" />
                </div>

                <CountUp
                  end={item.statNum}
                  decimals={item.statDecimals}
                  suffix={item.statSuffix}
                  duration={1.2 + idx * 0.05}
                  className={`mb-2 font-mono text-3xl font-bold leading-none block ${item.statClass}`}
                />

                <h3 className="font-serif text-lg font-semibold text-foreground mb-2">
                  {t(item.titleEs, item.titleEn)}
                </h3>

                <p className="text-sm text-muted-foreground leading-relaxed">
                  {t(item.descEs, item.descEn)}
                </p>
              </motion.article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
