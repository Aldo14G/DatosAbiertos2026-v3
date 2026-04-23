"use client";

import { ExternalLink, GitFork } from "lucide-react";
import { useLang } from "./LangProvider";

const LINKS = {
  labnl: "https://labnuevoleon.mx",
  wiki: "https://wiki.labnuevoleon.mx",
  repo1: "https://github.com/ricalanis/comovamoslabnle1",
  repo2: "https://github.com/olivergomezrs/comovamoslabnlv3",
  portal: "https://catalogodatos.nl.gob.mx",
  dashboard: "https://catalogodatos.nl.gob.mx",
};

export function CreditsSection() {
  const { t } = useLang();

  return (
    <footer id="credits" className="py-16 px-4 sm:px-6 bg-muted/40">
      <div className="mx-auto max-w-7xl">
        {/* Top row */}
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-3 mb-12">
          {/* About */}
          <div>
            <h3 className="font-serif text-lg font-semibold text-foreground mb-3">
              {t("Sobre el proyecto", "About the project")}
            </h3>
            <p className="text-sm text-muted-foreground leading-relaxed mb-3">
              {t(
                "DatosAbiertos NL 2026 es una evaluación independiente de calidad de datos del portal gubernamental de Nuevo León. Nace como evolución del proyecto fundacional 2024 «¿Cómo vamos en Datos en Nuevo León?»",
                "DatosAbiertos NL 2026 is an independent data quality assessment of Nuevo León's government open data portal. It evolved from the 2024 foundational project «¿Cómo vamos en Datos en Nuevo León?»"
              )}
            </p>
            <a
              href={LINKS.wiki}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-sm text-primary hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring rounded"
            >
              wiki.labnuevoleon.mx
              <ExternalLink className="size-3" aria-hidden="true" />
            </a>
          </div>

          {/* Repos */}
          <div>
            <h3 className="font-serif text-lg font-semibold text-foreground mb-3">
              {t("Repositorios", "Repositories")}
            </h3>
            <ul className="flex flex-col gap-3" role="list">
              <RepoLink
                href={LINKS.repo1}
                label="ricalanis/comovamoslabnle1"
                desc={t("Análisis fundacional 2024", "2024 foundational analysis")}
              />
              <RepoLink
                href={LINKS.repo2}
                label="olivergomezrs/comovamoslabnlv3"
                desc={t("Pipeline v3 — motor de evaluación", "Pipeline v3 — evaluation engine")}
              />
            </ul>
          </div>

          {/* Affiliation */}
          <div>
            <h3 className="font-serif text-lg font-semibold text-foreground mb-3">
              {t("Afiliación", "Affiliation")}
            </h3>
            <p className="text-sm text-muted-foreground leading-relaxed mb-3">
              {t(
                "Proyecto afiliado al",
                "Project affiliated with"
              )}{" "}
              <a
                href={LINKS.labnl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                LABNL — Laboratorio para la Ciudad de Nuevo León
              </a>
              .{" "}
              {t(
                "La metodología y el código fuente son de acceso abierto bajo licencia MIT.",
                "The methodology and source code are openly accessible under the MIT license."
              )}
            </p>
            <p className="text-sm text-muted-foreground">
              {t("Fuente de datos:", "Data source:")}{" "}
              <a
                href={LINKS.portal}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                catalogodatos.nl.gob.mx
              </a>
            </p>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-border pt-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <p className="font-serif text-sm font-semibold text-foreground">
              DatosAbiertos NL 2026
            </p>
            <p className="font-mono text-xs text-muted-foreground">
              ISO/IEC 25012:2008 · Pipeline v3.0 ·{" "}
              {t("Evaluación", "Assessment")} 2026-03-19
            </p>
          </div>
          <div className="flex items-center gap-4">
            <a
              href={LINKS.repo1}
              target="_blank"
              rel="noopener noreferrer"
              aria-label="GitHub"
              className="text-muted-foreground hover:text-foreground transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring rounded"
            >
              <GitFork className="size-5" />
            </a>
            <a
              href={LINKS.dashboard}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 rounded border border-border bg-background px-3 py-1.5 text-xs font-medium text-foreground transition-colors hover:bg-muted focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring"
            >
              {t("Ver dashboard", "Open dashboard")}
              <ExternalLink className="size-3" aria-hidden="true" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}

function RepoLink({
  href,
  label,
  desc,
}: {
  href: string;
  label: string;
  desc: string;
}) {
  return (
    <li>
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="group flex items-start gap-2 focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring rounded"
      >
        <GitFork
          className="mt-0.5 size-4 shrink-0 text-muted-foreground group-hover:text-foreground transition-colors"
          aria-hidden="true"
        />
        <div>
          <span className="font-mono text-sm text-primary group-hover:underline">
            {label}
          </span>
          <p className="text-xs text-muted-foreground">{desc}</p>
        </div>
      </a>
    </li>
  );
}
