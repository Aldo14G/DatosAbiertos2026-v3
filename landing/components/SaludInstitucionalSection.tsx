"use client";

import { motion, useReducedMotion } from "framer-motion";
import { useLang } from "./LangProvider";

const ease = [0.16, 1, 0.3, 1] as const;

export function SaludInstitucionalSection() {
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
      id="salud-institucional"
      aria-labelledby="salud-heading"
      className="py-20 bg-background overflow-hidden"
    >
      <div className="mx-auto max-w-[850px] flex flex-col md:flex-row items-center gap-12 px-6">
        <motion.div className="flex-1 text-left" {...fadeUp(0)}>
          <span className="eyebrow">{t("Diagnóstico", "Diagnostic")}</span>
          <h2
            id="salud-heading"
            className="font-serif text-4xl md:text-5xl font-bold text-foreground mb-6"
          >
            {t("Salud Institucional", "Institutional Health")}
          </h2>
          <p className="text-muted-foreground text-lg leading-relaxed">
            {t(
              "Visualizamos la madurez de los datos en toda la administración pública, identificando líderes en transparencia y áreas que requieren remediación técnica.",
              "We visualize data maturity across the public administration, identifying transparency leaders and areas requiring technical remediation."
            )}
          </p>
        </motion.div>

        <motion.div
          className="flex-1 flex justify-center w-full max-w-[340px]"
          {...fadeUp(0.15)}
        >
          <img
            src="https://images.unsplash.com/photo-1639322537228-f710d846310a?auto=format&fit=crop&q=80&w=680"
            alt={t(
              "Red de instituciones gubernamentales interconectadas representando la salud institucional de los datos públicos",
              "Network of interconnected government institutions representing the institutional health of public data"
            )}
            className="w-full h-auto rounded-2xl object-cover shadow-lg"
            loading="lazy"
          />
        </motion.div>
      </div>
    </section>
  );
}
