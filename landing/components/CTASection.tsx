"use client";

import { motion, useReducedMotion } from "framer-motion";
import { BarChart2, GitFork } from "lucide-react";
import { useLang } from "./LangProvider";

const DASHBOARD_URL = "http://localhost:8501";
const REPO_URL = "https://github.com/Aldo14G/DatosAbiertos2026-v3";
const ease = [0.16, 1, 0.3, 1] as const;

export function CTASection() {
  const { t } = useLang();
  const reduced = useReducedMotion();

  return (
    <section
      aria-label={t("Llamada a la acción", "Call to action")}
      className="py-16 px-4 sm:px-6"
    >
      <div className="mx-auto max-w-7xl">
        <motion.div
          {...(reduced
            ? {}
            : {
                initial: { opacity: 0, y: 24 },
                whileInView: { opacity: 1, y: 0 },
                viewport: { once: true, amount: 0.3 },
                transition: { duration: 0.5, ease },
              })}
          className="relative overflow-hidden rounded-3xl bg-midnight px-8 py-20 text-center"
        >
          {/* Decorative glows */}
          <div
            className="pointer-events-none absolute inset-0"
            aria-hidden="true"
          >
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_60%_80%_at_28%_50%,rgba(58,168,149,0.22)_0%,transparent_65%)]" />
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_40%_60%_at_76%_60%,rgba(212,162,76,0.14)_0%,transparent_62%)]" />
          </div>

          <div className="relative z-10">
            <h2 className="font-serif text-4xl md:text-5xl font-bold text-white mb-5">
              {t(
                "Explora los datos abiertos de Nuevo León",
                "Explore Nuevo León's open data"
              )}
            </h2>

            <p className="mx-auto mb-10 max-w-xl text-lg text-white/62">
              {t(
                "El dashboard interactivo permite filtrar, comparar y exportar los resultados de la auditoría. Todo el código es público y cada métrica es reproducible.",
                "The interactive dashboard lets you filter, compare, and export audit results. All code is public and every metric is fully reproducible."
              )}
            </p>

            <div className="flex flex-wrap items-center justify-center gap-4">
              <a
                href={DASHBOARD_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 rounded-xl bg-white px-6 py-3.5 font-semibold text-midnight shadow-lg shadow-black/25 transition hover:-translate-y-0.5 hover:shadow-xl focus-visible:outline focus-visible:outline-2 focus-visible:outline-white focus-visible:outline-offset-2 active:scale-[0.97]"
              >
                <BarChart2 className="size-5" aria-hidden="true" />
                {t("Explorar dashboard", "Explore dashboard")}
              </a>

              <a
                href={REPO_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 rounded-xl border border-white/30 px-6 py-3.5 font-semibold text-white transition hover:border-white/60 hover:bg-white/10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-white focus-visible:outline-offset-2 active:scale-[0.97]"
              >
                <GitFork className="size-5" aria-hidden="true" />
                {t("Ver código en GitHub", "View code on GitHub")}
              </a>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
