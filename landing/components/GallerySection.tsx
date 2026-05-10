"use client";

import { motion, useReducedMotion } from "framer-motion";
import {
  LayoutDashboard,
  Table2,
  ShieldCheck,
  Building2,
  Search,
  type LucideIcon,
} from "lucide-react";
import { useLang } from "./LangProvider";

const ease = [0.16, 1, 0.3, 1] as const;

interface Screen {
  id: string;
  icon: LucideIcon;
  labelEs: string;
  labelEn: string;
  span?: boolean;
}

const SCREENS: Screen[] = [
  {
    id: "inicio",
    icon: LayoutDashboard,
    labelEs: "Inicio — Resumen ejecutivo",
    labelEn: "Home — Executive summary",
    span: true,
  },
  {
    id: "datasets",
    icon: Table2,
    labelEs: "Catálogo de datasets",
    labelEn: "Dataset catalog",
  },
  {
    id: "calidad",
    icon: ShieldCheck,
    labelEs: "Calidad Pro",
    labelEn: "Quality Pro",
  },
  {
    id: "organizaciones",
    icon: Building2,
    labelEs: "Organizaciones",
    labelEn: "Organizations",
  },
  {
    id: "hallazgos-dash",
    icon: Search,
    labelEs: "Hallazgos",
    labelEn: "Findings",
  },
];

export function GallerySection() {
  const { t } = useLang();
  const reduced = useReducedMotion();

  const fadeUp = (delay = 0) =>
    reduced
      ? {}
      : {
          initial: { opacity: 0, y: 24 },
          whileInView: { opacity: 1, y: 0 },
          viewport: { once: true, amount: 0.2 },
          transition: { duration: 0.5, ease, delay },
        };

  return (
    <section
      id="gallery"
      aria-labelledby="gallery-heading"
      className="py-24 px-4 sm:px-6 bg-background"
    >
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <motion.div className="mb-14" {...fadeUp(0)}>
          <span className="eyebrow">
            {t("Herramienta · Dashboard interactivo", "Tool · Interactive dashboard")}
          </span>
          <h2
            id="gallery-heading"
            className="font-serif text-4xl md:text-5xl font-bold text-foreground mb-4"
          >
            {t("Explora los datos tú mismo", "Explore the data yourself")}
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl">
            {t(
              "Cinco vistas interactivas que cubren desde el resumen ejecutivo hasta el análisis granular por dataset, organización y hallazgo.",
              "Five interactive views covering everything from the executive summary to granular analysis by dataset, organization, and finding."
            )}
          </p>
        </motion.div>

        {/* Bento grid — 3 cols × 2 rows; first item spans 2 rows */}
        <div className="grid grid-cols-3 grid-rows-2 gap-4 min-h-[440px]">
          {SCREENS.map((item, idx) => {
            const Icon = item.icon;
            return (
              <motion.div
                key={item.id}
                {...(reduced
                  ? {}
                  : {
                      initial: { opacity: 0, scale: 0.96 },
                      whileInView: { opacity: 1, scale: 1 },
                      viewport: { once: true, amount: 0.1 },
                      transition: { duration: 0.4, ease, delay: idx * 0.06 },
                    })}
                className={`group relative flex flex-col items-center justify-center gap-3 overflow-hidden rounded-2xl border border-border bg-slate-100 dark:bg-white/[0.07] transition-all duration-500 hover:-translate-y-1 hover:border-teal/40 hover:shadow-xl hover:shadow-teal/10 ${
                  item.span ? "row-span-2" : ""
                }`}
                aria-label={t(item.labelEs, item.labelEn)}
              >
                {/* Hover glow */}
                <div
                  className="pointer-events-none absolute inset-0 bg-gradient-to-br from-teal/[0.12] via-transparent to-gold/[0.08] opacity-0 transition-opacity duration-500 group-hover:opacity-100"
                  aria-hidden="true"
                />

                <Icon
                  className="relative z-10 size-10 text-teal/70 transition-colors duration-300 group-hover:text-teal"
                  aria-hidden="true"
                />
                <span className="relative z-10 px-4 text-center font-mono text-[10px] uppercase tracking-[0.14em] text-muted-foreground transition-colors duration-300 group-hover:text-foreground">
                  {t(item.labelEs, item.labelEn)}
                </span>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
