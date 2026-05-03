"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, ChevronsUpDown } from "lucide-react";
import { useLang } from "./LangProvider";
import { ORG_RANKINGS, type OrgRanking, type Grade } from "@/lib/data";

type SortKey = "name" | "score" | "datasets";
type SortDir = "asc" | "desc";

const GRADE_STYLES: Record<Grade, { badge: string; dot: string }> = {
  Gold: {
    badge:
      "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-400 dark:border-amber-700/50",
    dot: "bg-amber-500",
  },
  Silver: {
    badge:
      "bg-gray-100 text-gray-600 border-gray-300 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-600",
    dot: "bg-gray-400",
  },
  Bronze: {
    badge:
      "bg-violet-50 text-violet-700 border-violet-200 dark:bg-violet-950/40 dark:text-violet-400 dark:border-violet-700/50",
    dot: "bg-violet-500",
  },
};

function scoreColorClass(score: number): string {
  if (score >= 90) return "text-amber-700 dark:text-amber-400";
  if (score >= 70) return "text-gray-600 dark:text-gray-300";
  return "text-violet-700 dark:text-violet-400";
}

export function RankingsSection() {
  const { t } = useLang();
  const [sort, setSort] = useState<{ key: SortKey; dir: SortDir }>({
    key: "score",
    dir: "desc",
  });
  const [filter, setFilter] = useState<Grade | "all">("all");

  const sorted = [...ORG_RANKINGS]
    .filter((o) => filter === "all" || o.grade === filter)
    .sort((a, b) => {
      const mul = sort.dir === "asc" ? 1 : -1;
      if (sort.key === "name") return mul * a.name.localeCompare(b.name, "es");
      if (sort.key === "datasets") return mul * (a.datasets - b.datasets);
      return mul * (a.score - b.score);
    });

  function handleSort(key: SortKey) {
    setSort((prev) =>
      prev.key === key
        ? { key, dir: prev.dir === "asc" ? "desc" : "asc" }
        : { key, dir: "desc" }
    );
  }

  return (
    <section
      id="rankings"
      aria-labelledby="rankings-heading"
      className="py-20 px-4 sm:px-6 border-b border-border"
    >
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <p className="font-mono text-xs font-medium tracking-widest text-muted-foreground uppercase mb-3">
            {t("Resultados por dependencia", "Results by agency")} ·{" "}
            {t("Evaluación 2026", "2026 assessment")}
          </p>
          <h2
            id="rankings-heading"
            className="font-serif text-4xl md:text-5xl font-bold text-foreground mb-4"
          >
            {t(
              "Calificaciones por dependencia estatal",
              "Ratings by state agency"
            )}
          </h2>
          <p className="text-muted-foreground max-w-2xl">
            {t(
              "Ranking de las dependencias evaluadas según su score global ponderado. Los datos son computados automáticamente desde el portal oficial.",
              "Ranking of evaluated agencies by weighted global score. Data is automatically computed from the official portal."
            )}
          </p>
        </div>

        {/* Grade filter */}
        <div
          className="flex flex-wrap gap-2 mb-6"
          role="group"
          aria-label={t("Filtrar por calificación", "Filter by grade")}
        >
          {(["all", "Gold", "Silver", "Bronze"] as const).map((g) => (
            <button
              key={g}
              onClick={() => setFilter(g)}
              aria-pressed={filter === g}
              className={`rounded border px-3 py-1.5 pointer-coarse:py-2.5 pointer-coarse:px-4 text-sm font-medium transition select-none cursor-pointer active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/60 focus-visible:ring-offset-1 ${
                filter === g
                  ? "bg-foreground text-background border-foreground"
                  : "bg-background text-muted-foreground border-border hover:border-foreground hover:text-foreground"
              }`}
            >
              {g === "all"
                ? t("Todas", "All")
                : g === "Gold"
                ? t("Gold", "Gold")
                : g === "Silver"
                ? t("Silver", "Silver")
                : t("Bronze", "Bronze")}
            </button>
          ))}
          <span className="ml-auto self-center font-mono text-xs text-muted-foreground">
            {sorted.length} {t("dependencias", "agencies")}
          </span>
        </div>

        {/* Mobile card list — visible only on small screens */}
        <div className="sm:hidden space-y-2" aria-live="polite">
          {sorted.map((org, idx) => (
            <MobileOrgCard key={org.name} org={org} rank={idx + 1} />
          ))}
          {sorted.length === 0 && (
            <p className="py-10 text-center text-muted-foreground text-sm">
              {t(
                "Sin resultados para este filtro.",
                "No results for this filter."
              )}
            </p>
          )}
        </div>

        {/* Desktop table — hidden on small screens */}
        <div className="hidden sm:block rounded-lg border border-border overflow-hidden">
          <table className="w-full text-sm" aria-live="polite">
            <thead>
              <tr className="border-b border-border bg-muted/50">
                <th className="px-4 py-3 text-left font-mono text-xs font-medium text-muted-foreground uppercase tracking-wide w-10">
                  #
                </th>
                <SortHeader
                  label={t("Dependencia", "Agency")}
                  sortKey="name"
                  current={sort}
                  onSort={handleSort}
                  className="text-left"
                />
                <SortHeader
                  label={t("Score", "Score")}
                  sortKey="score"
                  current={sort}
                  onSort={handleSort}
                  className="text-right"
                />
                <SortHeader
                  label={t("Datasets", "Datasets")}
                  sortKey="datasets"
                  current={sort}
                  onSort={handleSort}
                  className="text-right"
                />
                <th className="px-4 py-3 text-center font-mono text-xs font-medium text-muted-foreground uppercase tracking-wide">
                  {t("Grado", "Grade")}
                </th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((org, idx) => (
                <OrgRow key={org.name} org={org} rank={idx + 1} />
              ))}
              {sorted.length === 0 && (
                <tr>
                  <td
                    colSpan={5}
                    className="px-4 py-10 text-center text-muted-foreground text-sm"
                  >
                    {t(
                      "Sin resultados para este filtro.",
                      "No results for this filter."
                    )}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Legend */}
        <div className="mt-4 flex flex-wrap gap-4">
          {(["Gold", "Silver", "Bronze"] as Grade[]).map((g) => (
            <span
              key={g}
              className="flex items-center gap-1.5 text-xs text-muted-foreground"
            >
              <span
                className={`inline-block size-2 rounded-full ${GRADE_STYLES[g].dot}`}
                aria-hidden="true"
              />
              {g === "Gold" && t("Gold ≥ 90 pts", "Gold ≥ 90 pts")}
              {g === "Silver" && t("Silver 70–89 pts", "Silver 70–89 pts")}
              {g === "Bronze" && t("Bronze < 70 pts", "Bronze < 70 pts")}
            </span>
          ))}
          <span className="ml-auto text-xs text-muted-foreground">
            {t(
              "Fuente: catalogodatos.nl.gob.mx · Pipeline v3.0",
              "Source: catalogodatos.nl.gob.mx · Pipeline v3.0"
            )}
          </span>
        </div>
      </div>
    </section>
  );
}

function MobileOrgCard({ org, rank }: { org: OrgRanking; rank: number }) {
  const { lang, t } = useLang();
  const styles = GRADE_STYLES[org.grade];

  return (
    <div className="flex items-center gap-3 px-4 py-3 rounded-lg border border-border bg-background hover:bg-muted/30 transition-colors">
      <span className="font-mono text-xs text-muted-foreground w-5 shrink-0 tabular-nums">
        {rank}
      </span>
      <div className="flex-1 min-w-0">
        <p className="font-medium text-sm text-foreground leading-snug line-clamp-2">
          {lang === "es" ? org.name : org.nameEn}
        </p>
        <p className="font-mono text-xs text-muted-foreground mt-0.5">
          {org.datasets} {t("datasets", "datasets")}
        </p>
      </div>
      <div className="flex flex-col items-end gap-1.5 shrink-0">
        <span
          className={`font-mono text-base font-bold tabular-nums ${scoreColorClass(org.score)}`}
        >
          {org.score.toFixed(1)}
        </span>
        <span
          className={`inline-flex items-center gap-1 rounded border px-2 py-0.5 text-xs font-medium ${styles.badge}`}
        >
          <span
            className={`size-1.5 rounded-full ${styles.dot}`}
            aria-hidden="true"
          />
          {org.grade}
        </span>
      </div>
    </div>
  );
}

function OrgRow({ org, rank }: { org: OrgRanking; rank: number }) {
  const { lang } = useLang();
  const styles = GRADE_STYLES[org.grade];

  return (
    <tr className="border-b border-border last:border-0 hover:bg-muted/30 transition-colors">
      <td className="px-4 py-3 font-mono text-xs text-muted-foreground tabular-nums">
        {rank}
      </td>
      <td className="px-4 py-3 text-foreground max-w-xs">
        <span className="block font-medium leading-snug">
          {lang === "es" ? org.name : org.nameEn}
        </span>
      </td>
      <td className="px-4 py-3 text-right font-mono text-sm font-medium tabular-nums">
        <span className={scoreColorClass(org.score)}>{org.score.toFixed(1)}</span>
      </td>
      <td className="px-4 py-3 text-right font-mono text-sm text-muted-foreground tabular-nums">
        {org.datasets}
      </td>
      <td className="px-4 py-3 text-center">
        <span
          className={`inline-flex items-center gap-1 rounded border px-2 py-0.5 text-xs font-medium ${styles.badge}`}
        >
          <span
            className={`size-1.5 rounded-full ${styles.dot}`}
            aria-hidden="true"
          />
          {org.grade}
        </span>
      </td>
    </tr>
  );
}

function SortHeader({
  label,
  sortKey,
  current,
  onSort,
  className,
}: {
  label: string;
  sortKey: SortKey;
  current: { key: SortKey; dir: SortDir };
  onSort: (k: SortKey) => void;
  className?: string;
}) {
  const active = current.key === sortKey;
  const Icon = active
    ? current.dir === "asc"
      ? ChevronUp
      : ChevronDown
    : ChevronsUpDown;

  return (
    <th
      className={`px-4 py-3 ${className ?? ""}`}
      aria-sort={
        active ? (current.dir === "asc" ? "ascending" : "descending") : "none"
      }
    >
      <button
        onClick={() => onSort(sortKey)}
        className={`inline-flex items-center gap-1 font-mono text-xs font-medium uppercase tracking-wide transition select-none cursor-pointer active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/60 focus-visible:ring-offset-1 rounded ${
          active
            ? "text-foreground"
            : "text-muted-foreground hover:text-foreground"
        }`}
      >
        {label}
        <Icon className="size-3" aria-hidden="true" />
      </button>
    </th>
  );
}
