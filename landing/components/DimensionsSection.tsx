"use client";

import {
  CheckSquare,
  Clock,
  Globe,
  FileText,
  Unlock,
} from "lucide-react";
import { useLang } from "./LangProvider";
import { ISO_DIMENSIONS } from "@/lib/data";

const ICON_MAP: Record<string, React.ElementType> = {
  CheckSquare,
  Clock,
  Globe,
  FileText,
  Unlock,
};

export function DimensionsSection() {
  const { t } = useLang();

  return (
    <section
      id="dimensions"
      aria-labelledby="dimensions-heading"
      className="py-24 px-4 sm:px-6 relative overflow-hidden bg-background"
    >
      {/* Decorative background elements */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-[10%] -right-[10%] w-[500px] h-[500px] rounded-full bg-teal/5 blur-[120px]" />
        <div className="absolute -bottom-[10%] -left-[10%] w-[400px] h-[400px] rounded-full bg-gold/5 blur-[100px]" />
      </div>

      <div className="mx-auto max-w-7xl relative z-10">
        {/* Header */}
        <div className="mb-16">
          <span className="text-[10px] font-mono tracking-[0.2em] text-gold uppercase opacity-80 mb-4 block">
            {t("Marco normativo", "Normative framework")} · ISO/IEC 25012:2008
          </span>
          <h2
            id="dimensions-heading"
            className="font-serif text-4xl md:text-5xl font-bold text-foreground mb-6"
          >
            {t(
              "Cinco dimensiones para medir la calidad",
              "Five dimensions to measure quality"
            )}
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl">
            {t(
              "Cada dataset del portal es evaluado en cinco dimensiones derivadas de la norma internacional. Los pesos reflejan la criticidad operativa de cada atributo para datos abiertos gubernamentales.",
              "Each portal dataset is evaluated across five dimensions derived from the international standard. Weights reflect the operational criticality of each attribute for government open data."
            )}
          </p>
        </div>

        {/* Cards grid */}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {ISO_DIMENSIONS.map((dim) => {
            const Icon = ICON_MAP[dim.icon] ?? CheckSquare;
            return (
              <article
                key={dim.id}
                className="relative overflow-hidden rounded-2xl border border-border/40 bg-background/40 backdrop-blur-md p-6 transition-all duration-500 hover:shadow-2xl hover:shadow-teal/5 hover:-translate-y-1 group"
              >
                {/* Subtle gradient hover effect */}
                <div className="absolute inset-0 bg-gradient-to-br from-teal/5 via-transparent to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
                
                {/* Icon + title row */}
                <div className="flex items-start justify-between mb-4 relative z-10">
                  <div className="flex items-center gap-3">
                    <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-midnight/5 border border-border/50 text-teal transition-transform duration-500 group-hover:scale-110">
                      <Icon className="size-5" aria-hidden="true" />
                    </div>
                    <h3 className="font-serif text-xl font-bold text-foreground leading-tight">
                      {t(dim.nameEs, dim.nameEn)}
                    </h3>
                  </div>
                  {/* Weight badge */}
                  <span className="shrink-0 ml-2 inline-flex items-center justify-center rounded-full border border-gold/20 bg-gold/10 px-3 py-1 font-mono text-xs font-bold text-gold">
                    {dim.weight}%
                  </span>
                </div>

                {/* Description */}
                <p className="text-sm text-muted-foreground mb-5 leading-relaxed relative z-10">
                  {t(dim.descriptionEs, dim.descriptionEn)}
                </p>

                {/* Formula */}
                <div className="mb-4 rounded-xl bg-midnight/5 border border-border/30 px-4 py-3 relative z-10">
                  <p className="font-mono text-[11px] text-foreground/80 leading-relaxed">
                    <span className="text-teal font-semibold">∑</span> {t(dim.formulaEs, dim.formulaEn)}
                  </p>
                </div>

                {/* Example */}
                <p className="text-xs text-muted-foreground/80 italic relative z-10">
                  <span className="text-foreground/60 font-semibold not-italic">{t("Ejemplo:", "Example:")}</span> {t(dim.exampleEs, dim.exampleEn)}
                </p>

                {/* ISO ref */}
                <p className="mt-4 font-mono text-[10px] tracking-widest uppercase text-muted-foreground/40 relative z-10">
                  {dim.isoRef}
                </p>
              </article>
            );
          })}

          {/* Weight total card */}
          <div className="relative overflow-hidden rounded-2xl border border-border/40 bg-gradient-to-br from-midnight/5 to-transparent backdrop-blur-md p-8 flex flex-col justify-center items-center text-center sm:col-span-2 lg:col-span-1 group">
            <div className="absolute inset-0 bg-gradient-to-tr from-gold/5 via-transparent to-teal/5 opacity-50" />
            
            <p className="font-serif text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-br from-foreground to-foreground/50 mb-3 relative z-10">
              100%
            </p>
            <p className="text-sm text-muted-foreground max-w-xs relative z-10">
              {t(
                "Suma de pesos. El score global es la media ponderada de las cinco dimensiones.",
                "Weight sum. The global score is the weighted average of the five dimensions."
              )}
            </p>
            <div className="mt-6 w-full h-2 rounded-full bg-midnight/10 overflow-hidden flex relative z-10">
              {ISO_DIMENSIONS.map((dim) => (
                <div
                  key={dim.id}
                  style={{ width: `${dim.weight}%` }}
                  className={`h-full ${getWeightColor(dim.id)} transition-all duration-1000 ease-out origin-left`}
                  title={`${t(dim.nameEs, dim.nameEn)}: ${dim.weight}%`}
                />
              ))}
            </div>
            <div className="mt-4 flex flex-wrap justify-center gap-x-4 gap-y-2 relative z-10">
              {ISO_DIMENSIONS.map((dim) => (
                <span key={dim.id} className="flex items-center gap-1.5 text-[10px] font-mono tracking-wider text-muted-foreground uppercase">
                  <span className={`inline-block size-1.5 rounded-full ${getWeightColor(dim.id)}`} />
                  {t(dim.nameEs, dim.nameEn)}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function getWeightColor(id: string) {
  const map: Record<string, string> = {
    completeness: "bg-teal",
    timeliness: "bg-gold",
    accessibility: "bg-rose-500",
    documentation: "bg-amber-600",
    openness: "bg-indigo-400",
  };
  return map[id] ?? "bg-muted-foreground";
}
